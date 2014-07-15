from __future__ import absolute_import
from celery import Celery

app = Celery('bsn_services',
             broker='amqp://guest@qa-esb1.qa.bigswitch.com//',
             backend='amqp://guest@qa-esb1.qa.bigswitch.com//',
             include=['bsn_services.tasks'])

# Optional configuration, see the application user guide.
app.conf.update(
    CELERY_TASK_RESULT_EXPIRES=3600,
)

if __name__ == '__main__':
    app.start()
