command = '/home/ubuntu/webdev/venv/bin/gunicorn'
pythonpath = '/home/ubuntu/webdev/videochatapp'
bind = '172.31.18.58:8003'
workers = 1
worker_class = 'uvicorn.workers.UvicornWorker'
certfile = '/etc/letsencrypt/live/kieranoldfield.co.uk-0001/fullchain.pem'
keyfile = '/etc/letsencrypt/live/kieranoldfield.co.uk-0001/privkey.pem'
