from __future__ import absolute_import
from celery import Celery
from kombu import Exchange, Queue

# RabbitMQ Web GUI: http://qa-esb1.qa.bigswitch.com:15672/
app = Celery('template_services',
             broker='amqp://guest@qa-esb1.qa.bigswitch.com//',
             backend='amqp://guest@qa-esb1.qa.bigswitch.com//',
             include=['template_services.tasks'])
queue_name = 'template_services'

# Optional configuration, see the application user guide.
app.conf.update(
    CELERY_TASK_RESULT_EXPIRES=1800,  # 1/2 hour
    CELERY_ACCEPT_CONTENT=['pickle', 'json', 'msgpack', 'yaml'],
    CELERY_QUEUES=(
        Queue(queue_name,
              Exchange(queue_name),
              routing_key=queue_name),
    ),
    CELERY_DEFAULT_QUEUE=queue_name,
    CELERY_DEFAULT_EXCHANGE_TYPE='direct',
    CELERY_DEFAULT_ROUTING_KEY=queue_name,
)

if __name__ == '__main__':
    app.start()
