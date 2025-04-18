import multiprocessing

bind = "unix:/run/gunicorn.sock"
workers = multiprocessing.cpu_count() * 2 + 1
worker_class = "uvicorn.workers.UvicornWorker"
max_requests = 1000
max_requests_jitter = 50
timeout = 30
keepalive = 2

# Logging
accesslog = "/var/log/gunicorn/access.log"
errorlog = "/var/log/gunicorn/error.log"
loglevel = "info"

# SSL
keyfile = "/etc/letsencrypt/live/noinsur.com/privkey.pem"
certfile = "/etc/letsencrypt/live/noinsur.com/fullchain.pem"

# Security
limit_request_line = 4094
limit_request_fields = 100
limit_request_field_size = 8190 