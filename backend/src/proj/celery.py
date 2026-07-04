from celery import Celery

app = Celery('proj', backend='redis://localhost:6379/1', broker='redis://localhost:6379/0', include=['proj.tasks'])

app.conf.update(
    result_expires=3600,
)

if __name__ == '__main__':
    app.start()