from __future__ import absolute_import
from celery import Celery
from kombu import Exchange, Queue
import autobot.helpers as helpers


queue_name = 'bsn_common_services'
broker = helpers.bigrobot_esb_broker()
app = Celery(queue_name, broker=broker, backend=broker,
             include=[queue_name + '.tasks'])

# Optional configuration, see the application user guide.
app.conf.update(
    CELERY_TASK_RESULT_EXPIRES=1800,  # 1/2 hour
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
