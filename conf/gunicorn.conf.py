import multiprocessing

bind = "0.0.0.0:5000"
workers = 4
worker_class = "gthread"
threads = 4
max_requests = 1000
max_requests_jitter = 50
loglevel = "info"
capture_output = True
errorlog = "-"
accesslog = "-"