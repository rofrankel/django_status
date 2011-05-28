from django_status.management.commands import StatusNotificationCommand
from django_status import models, utils

from datetime import timedelta, datetime

def should_send(monitor):
    delay = monitor.instant_notification_delay
    last_sent = monitor.instant_notification_last_sent
    
    # if we aren't remembering when we last notified about this, notify
    if not last_sent:
        return True
    
    # if we've exceeded the delay since we last sent, return True
    if last_sent + timedelta(seconds=delay) < datetime.now():
        return True
    else:
        print monitor, last_sent + timedelta(seconds=delay), datetime.now()
    
    return False

class Command(StatusNotificationCommand):
    notify_kwargs = {
        'notify_type': models.NOTIFY.INSTANT,
    }
    
    def __init__(self, *args, **kwargs):
        super(Command, self).__init__(*args, **kwargs)
        self.notified = []
    
    def monitors_to_notify(self, monitors, status):
        monitors = super(Command, self).monitors_to_notify(monitors, status)
        return filter(should_send, monitors)
    
    def send_notification(self, user, data):
        super(Command, self).send_notification(user, data)
        for status in ['warning_monitors', 'problem_monitors']:
            for monitor in data[status]:
                if monitor not in self.notified:
                    self.notified.append(monitor)
    
    def handle_noargs(self, verbosity, **options):
        
        # clear the last_sent date on anything which is now fine, so that if it
        # goes bad again we won't wait the full delay
        monitors_to_reset = utils.all_monitors(exclude_kwargs={'instant_notification_last_sent': None})
        monitors_to_reset = filter(lambda x: x.status() == models.STATUS.FINE, monitors_to_reset)
        for monitor in monitors_to_reset:
            monitor.instant_notification_last_sent = None
            monitor.save()
        
        
        super(Command, self).handle_noargs(verbosity, **options)
        
        
        # if we sent a notification, set the last_sent date
        for monitor in self.notified:
            monitor.instant_notification_last_sent = datetime.now()
            monitor.save()
