bind = '172.31.18.58:8003'
workers = 1
worker_class = 'uvicorn.workers.UvicornWorker'
certfile = '/etc/letsencrypt/live/kieranoldfield.co.uk/fullchain.pem'
keyfile = '/etc/letsencrypt/live/kieranoldfield.co.uk/privkey.pem'
