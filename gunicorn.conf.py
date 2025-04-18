bind = "unix:/home/nestrah/nestrah/nestrah.sock"
workers = 3
worker_class = 'sync'
worker_connections = 1000
timeout = 30
keepalive = 2

# Logging
accesslog = "/home/nestrah/nestrah/logs/gunicorn_access.log"
errorlog = "/home/nestrah/nestrah/logs/gunicorn_error.log"
loglevel = "info"

# Process naming
proc_name = "nestrah_gunicorn"

# Server mechanics
daemon = False
pidfile = "/home/nestrah/nestrah/gunicorn.pid"
user = "nestrah"
group = "www-data"

# Server hooks
def on_starting(server):
    server.log.info("Starting Gunicorn server for Nestrah") 