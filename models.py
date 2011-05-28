from django.db import models
from django.contrib.auth.models import User
from django.template.defaultfilters import timesince, timeuntil

from datetime import datetime, timedelta

class STATUS(object):
    FINE = 0
    WARNING = 1
    PROBLEM = 2

class NOTIFY(object):
    NONE = 0
    INSTANT = 1
    DIGEST = 2

NOTIFY_CHOICES = (
    (NOTIFY.NONE, 'None'),
    (NOTIFY.INSTANT, 'Instant (and digest)'),
    (NOTIFY.DIGEST, 'Digest'),
)

class Monitor(models.Model):
    
    notifiees = models.ManyToManyField(User, related_name="status_monitors", limit_choices_to={'is_staff': True})
    notify_type = models.IntegerField(default=NOTIFY.DIGEST, choices=NOTIFY_CHOICES)
    
    # wait 6 hours before resending an instant notification
    instant_notification_delay = 60 * 60 * 6 
    # this will remember when the last instant notification was sent, to prevent
    # spam.  this will be cleared if the monitor's status is seen to be fine, so
    # that if the problem occurs twice in a row the delay is ignored
    instant_notification_last_sent = models.DateTimeField(null=True, blank=True)
    
    desc = "Generic monitor"
    
    @property
    def status(self):
        """
        0 is good/green, 1 is warning/orange, 2 is problem/red
        """
        return STATUS.FINE
    
    def can_view(self, user):
        """
        Returns whether or not the user can view this monitor.
        """
        return True
    
    def report(self):
        return ""


class AgeMonitor(Monitor):
    
    warning_seconds = 60 * 60 * 24 * 1
    problem_seconds = 60 * 60 * 24 * 2
    
    none_status = STATUS.PROBLEM
    
    def __init__(self, *args, **kwargs):
        super(AgeMonitor, self).__init__(*args, **kwargs)
        
        # for caching purposes
        if self.pk:
            self.age = self.get_age()
    
    def get_age(self):
        return timedelta(0)
    
    def status(self):
        if self.age is None:
            return self.none_status
        
        if self.age >= timedelta(seconds=self.problem_seconds):
            return STATUS.PROBLEM
        elif self.age >= timedelta(seconds=self.warning_seconds):
            return STATUS.WARNING
        else:
            return STATUS.FINE
    
    def timeuntil(self):
        return timeuntil(datetime.now() - self.age)
    
    def timesince(self):
        return timesince(datetime.now() - self.age)
    
    class Meta:
        abstract = True