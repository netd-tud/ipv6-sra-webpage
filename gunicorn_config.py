# Code taken from https://betterstack.com/community/guides/scaling-python/gunicorn-explained
# Worker Settings
import multiprocessing

workers = 2 * multiprocessing.cpu_count() + 1  # Dynamically determine the optimal workers
worker_class = 'eventlet'  # Use gevent async workers
worker_connections = 1000  # Maximum concurrent connections per worker

# Timeout Settings
timeout = 30  # Automatically restart workers if they take too long
graceful_timeout = 30  # Graceful shutdown for workers

# Keep-Alive Settings
keepalive = 2  # Keep connections alive for 2s

# Worker Restart Settings
max_requests = 1000  # Restart workers after processing 1000 requests
max_requests_jitter = 50  # Add randomness to avoid mass restarts

# Logging Settings
accesslog = "gunicorn_access.log"  # Log HTTP requests to a file
errorlog = "gunicorn_error.log"  # Log errors to a file
loglevel = "info"  # Set log verbosity (debug, info, warning, error, critical)

# Server Settings
bind = "127.0.0.1:5000"
forwarded_allow_ips = "*"  # Allow requests from Nginx
proxy_protocol = True  # Enable proxy support
