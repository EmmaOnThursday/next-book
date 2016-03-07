from celery import Celery

app = Celery('tasks', broker='sqla+postgresql:///nextbook')

@app.task
def add(x, y):
    return x + y


if __name__ == '__main__':
    celery.start()