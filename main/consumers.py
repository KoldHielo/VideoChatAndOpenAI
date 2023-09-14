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
      print(data['room_name'], self.room_group_name)
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
    elif data['action'] == 'store_offerer_SDP' and self.room_group_name == data['for_group']:
      cache.set(f'{self.room_group_name}-offerer_SDP', data['offerer_SDP'])
    elif data['action'] == 'send_answerer_SDP' and self.room_group_name == data['for_group']:
      async_to_sync(self.channel_layer.group_send)(
            self.room_group_name,
            {
                'type': 'send_answer',
                'answerer_SDP': data['answerer_SDP']
            }
          )
    elif data['action'] == 'get_offerer_SDP' and self.room_group_name == data['for_group']:
      offerer_SDP = cache.get(f'{self.room_group_name}-offerer_SDP')
      self.send(json.dumps({
          'offerer_SDP': offerer_SDP
      }))
      
    elif data['action'] == 'GPT_help' and self.room_group_name == data['for_group']:
      system_message = 'Please help this conversation? Messages input to you in this conversation will be wrapped in HTML div elements. The class "message lc" will be the first peer, "message rc" will be the second peer and "message gpt" will be what you have responded previously in the conversation. Your output should just be plain text, no HTML whatsoever as I will handle this. !gpt at the beginning of a message is a prompt to call upon you, just to clarify in case of confusion.'
      messages = [
            {'role': 'system', 'content': system_message},
            {'role': 'user', 'content': data['prompt']}
          ]
      response = openai.ChatCompletion.create(
            model='gpt-3.5-turbo',
            messages=messages
          )
      gpt_message = response['choices'][0]['message']['content']
      async_to_sync(self.channel_layer.group_send)(
            self.room_group_name,
            {
                'type': 'send_gpt_message',
                'gpt_message': gpt_message
            }
          )
      
          
      
  def send_answer(self, event):
    self.send(json.dumps({
        'answerer_SDP': event['answerer_SDP']
    }))
    
  def send_gpt_message(self, event):
    self.send(json.dumps({
        'gpt_message': event['gpt_message']
    }))