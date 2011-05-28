from django_status.management.commands import StatusNotificationCommand
from django_status import models

class Command(StatusNotificationCommand):
    notify_kwargs = {
        'notify_type__in': [models.NOTIFY.DIGEST, models.NOTIFY.INSTANT]
    }
