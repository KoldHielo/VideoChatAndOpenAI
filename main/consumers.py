import json
from channels.generic.websocket import WebsocketConsumer
from asgiref.sync import async_to_sync
from django.core.cache import cache
import openai
import os

openai.api_key = os.environ['OPENAI_API_KEY']

class VideoChatConsumer(WebsocketConsumer):
  def connect(self):
    self.accept()

  def receive(self, text_data):
    data = json.loads(text_data)
    if data['action'] == 'join_room':
      self.room_group_name = data['room_name']
      quantity = cache.get(f'{self.room_group_name}-quantity')
      if quantity == None:
        cache.set(f'{self.room_group_name}-quantity', 1)
        async_to_sync(self.channel_layer.group_add)(
          self.room_group_name,
          self.channel_name
        )
        self.send(json.dumps({
            'role': 'offerer',
            'room': self.room_group_name,
        }))
      elif quantity == 1:
        cache.set(f'{self.room_group_name}-quantity', 2)
        async_to_sync(self.channel_layer.group_add)(
          self.room_group_name,
          self.channel_name
        )
        self.send(json.dumps({
            'role': 'answerer',
            'room': self.room_group_name,
        }))
      elif quantity >= 2:
        self.room_group_name = None
        self.send(json.dumps({
          'role': 'full',
          'room': None
        }))
    
    elif data['action'] == 'candidate_exchange' and self.room_group_name == data['for_group']:
      room_capacity = cache.get(f'{self.room_group_name}-quantity')
      if data['role'] == 'offerer':
        if room_capacity == 2:
          candidates = cache.get(f'{self.room_group_name}-offerer-candidates')
          if candidates is not None:
            candidates = json.loads(candidates)
            candidates.append(data['candidate'])
            cache.delete(f'{self.room_group_name}-offerer-candidates')
          else:
            candidates = [data['candidate']]
          async_to_sync(self.channel_layer.group_send)(
              self.room_group_name,
              {
                'type': 'send_candidates',
                'for': 'answerer',
                'candidates': candidates,
                'for_group': self.room_group_name
              }
            )
        else:
          key_name = f'{self.room_group_name}-offerer-candidates'
          candidates = cache.get(key_name)
          if candidates == None:
            value = json.dumps([data['candidate']])
            cache.set(key_name, value)
          else:
            candidates = json.loads(candidates)
            candidates.append(data['candidate'])
            value = json.dumps(candidates)
            cache.set(key_name, value)
      elif data['role'] == 'answerer':
        if room_capacity == 2:
          async_to_sync(self.channel_layer.group_send)(
              self.room_group_name,
              {
                'type': 'send_candidates',
                'for': 'offerer',
                'candidates': [data['candidate']],
                'for_group': self.room_group_name
              }
            )
    elif data['action'] == 'get_offerer_candidates' and self.room_group_name == data['for_group']:
      sdp = cache.get(f'{self.room_group_name}-offerer-SDP')
      candidates = cache.get(f'{self.room_group_name}-offerer-candidates')
      if candidates is not None:
        async_to_sync(self.channel_layer.group_send)(
              self.room_group_name,
              {
                'type': 'send_candidates',
                'for': 'answerer',
                'candidates': candidates,
                'offerer_SDP': sdp,
                'for_group': self.room_group_name
              }
            )
        cache.delete(f'{self.room_group_name}-offerer-candidates')
        cache.delete(f'{self.room_group_name}-offerer-SDP')
    elif data['action'] == 'store_offerer_SDP' and self.room_group_name == data['for_group']:
      cache.set(f'{self.room_group_name}-offerer-SDP', data['offerer_SDP'])
    elif data['action'] == 'send_answerer_SDP' and data['for_group'] == self.room_group_name:
      async_to_sync(self.channel_layer.group_send)(
          self.room_group_name,
          {
              'type': 'send_candidates',
              'answerer_SDP': data['answerer_SDP']
          }
          )
    elif data['action'] == 'GPT_help' and self.room_group_name == data['for_group']:
      system_message = 'You are a helpful assistant.'
      messages = [
            {'role': 'system', 'content': system_message}
          ]
      for message in data['prompts']:
        if message['user'] == 'user-1':
          role = 'user'
          content = f'User 1: {message["content"]}'
        elif message['user'] == 'user-2':
          role = 'user'
          content = f'User 2: {message["content"]}'
        elif message['user'] == 'assistant':
          role = 'assistant'
          content = message['content']
        messages.append({'role': role, 'content': content})
          
      response = openai.ChatCompletion.create(
            model='gpt-3.5-turbo',
            messages=messages
          )
      gpt_message = response['choices'][0]['message']['content']
      gpt_message = gpt_message.replace('\n', '<br>')
      async_to_sync(self.channel_layer.group_send)(
            self.room_group_name,
            {
                'type': 'send_gpt_message',
                'gpt_message': gpt_message
            }
          )

  def disconnect(self, close_code):
    async_to_sync(self.channel_layer.group_discard)(
      self.room_group_name,
      self.channel_name
    )
    quantity = cache.get(f'{self.room_group_name}-quantity')
    if quantity == 2:
      cache.set(f'{self.room_group_name}-quantity', 1)
    elif quantity == 1:
      cache.delete(f'{self.room_group_name}-quantity')
      
  def send_candidates(self, event):
    self.send(json.dumps(event))
    
  def send_gpt_message(self, event):
    self.send(json.dumps({
        'gpt_message': event['gpt_message']
    }))
