from __future__ import absolute_import
from celery import Celery

# RabbitMQ Web GUI: http://qa-esb1.qa.bigswitch.com:15672/
app = Celery('template_services',
             broker='amqp://guest@qa-esb1.qa.bigswitch.com//',
             backend='amqp://guest@qa-esb1.qa.bigswitch.com//',
             include=['template_services.tasks'])

# Optional configuration, see the application user guide.
app.conf.update(
    CELERY_TASK_RESULT_EXPIRES=3600,  # 1 hour
)

if __name__ == '__main__':
    app.start()
