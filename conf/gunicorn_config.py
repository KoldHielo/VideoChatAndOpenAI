command = '/home/ubuntu/webdev/venv/bin/gunicorn'
pythonpath = '/home/ubuntu/webdev/vc'
bind = '10.0.0.145:8003'
workers = 1
worker_class = 'uvicorn.workers.UvicornWorker'
certfile = '/etc/letsencrypt/live/kieranoldfield.co.uk/fullchain.pem'
keyfile = '/etc/letsencrypt/live/kieranoldfield.co.uk/privkey.pem'
