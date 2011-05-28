from django.core.management.base import NoArgsCommand
from django.conf import settings
from django.contrib.sites.models import Site
from django.contrib.auth.models import User

from django_status.mail import send_mail_from_template
from django_status.monitors import monitors as monitor_types
from django_status import models

import datetime
from itertools import groupby

from_email = "status@%s" % (Site.objects.get_current().domain,) or settings.DJANGO_STATUS_FROM_EMAIL

class StatusNotificationCommand(NoArgsCommand):
    
    notify_kwargs = {}
    email_template = 'status_notification'
    
    def monitors_to_notify(self, monitors, status):
        return filter(lambda m: m.status() == status, monitors)
    
    def send_notification(self, user, data):
        send_mail_from_template(user.email, self.email_template, data, from_email=from_email)
    
    def handle_noargs(self, verbosity, **options):
        users = User.objects.exclude(status_monitors=None)
        for user in users:
            monitors = []
            for monitor_type in monitor_types:
                monitors += list(
                    monitor_type.objects.filter(
                        notifiees=user,
                        **self.notify_kwargs
                    )
                )
            
            monitors = filter(lambda x: x.status() != models.STATUS.FINE, monitors)
            
            if monitors:
                monitors = sorted(monitors, key=lambda x: x.status(), reverse=True)
                problem_monitors = self.monitors_to_notify(monitors, models.STATUS.PROBLEM)
                warning_monitors = self.monitors_to_notify(monitors, models.STATUS.WARNING)
                
                if problem_monitors or warning_monitors:
                    
                    data = {
                        'problem_monitors': problem_monitors,
                        'warning_monitors': warning_monitors,
                        'user': user,
                    }
                    
                    self.send_notification(user, data)