from flask import Flask, request
from celery import Celery
import os
import time

# Adding the required settings in order to connect our flask app with celery and redis
app = Flask(__name__)
app.config["CELERY_BROKER_URL"] = "redis://localhost:6379/0"
# Using the route "/0" to send the message to redis
app.config["result_backend"] = "redis://localhost:6379/1"
# Using the route "/1" to save the result-object we return in the background task 

CELERY_BEAT_SCHEDULE = {
      'do-this-every-5-minutes': {
        'task': 'main.task_example',
        'schedule': 300.0,
    },
    'do-this-every-1-minut': {
        'task': 'main.task_per_minute',
        'schedule': 60.0,
    },
}

celery = Celery(app.name, broker=app.config["CELERY_BROKER_URL"])
celery.conf.update(
    result_backend=app.config["result_backend"],
    beat_schedule=CELERY_BEAT_SCHEDULE
)

@celery.task()
def task_per_minute():
    print("--> This message should be printed every minute <--")
    return {
        "task_returned": True,
        "developer": "Bearz"
    }

@celery.task()
def task_example():
    time.sleep(25)
    print("--------> Deleting all files in ./data directory <---------")
    for _file in os.listdir('./data'):
        os.remove(f"./data/{_file}")
    return {
        "state": "Done",
        "owner": "Elmer&Hachy"
    }

@app.route('/', methods = ['POST', 'GET'])
def main():
    task = task_example.delay()
    return "GG BRO"


if __name__=='__main__':
    app.run(debug=True, port=5000)


# Flower GUI to monitor tasks ------> celery -A main.celery flower --loglevel=info --port=9999
# Celery workers, execute tasks ----> celery -A main.celery worker --loglevel=info
# Scheduler for Periodic tasks -----> celery -A main.celery beat
# Start the flask server