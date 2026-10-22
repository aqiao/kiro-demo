# This is the only supported production WSGI configuration.
wsgi_app = "wsgi:app"
workers = 1
worker_class = "gthread"
threads = 8
preload_app = False
