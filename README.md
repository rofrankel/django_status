django\_status is a status dashboard that allows you to keep track of various
properties of your site. Uses cases include monitoring the age of editorial
content, making sure mailer queues aren't full for too long, making sure a task
queue remains below a certain size, or anything else you can think of.


Monitors
========


django\_status defines the concept of monitors which monitor values and return a
status - either fine, warning, or problem. Specifically,
`django_status.models.STATUS.FINE`, `django_status.models.STATUS.WARNING`, or
`django_status.models.STATUS.PROBLEM`. A dashboard can be displayed, showing the
state of all monitors.

Using django\_status generally means subclassing `django_status.models.Montior`
and overriding the `status` function, returning something from
`django_status.models.STATUS` as described above. See the *Installation and
Usage* section for more.

You might always want to override the `report` method. The dashboard will show
the output of `report()` for each monitor, which should just reuturn a string
elaborating on the meaning of the result of `status()`. For example:

    def report(self):
        STATUS = django_status.models.STATUS
        return {
            STATUS.FINE: "Everything's okay.",
            STATUS.WARNING: "The server is a little warm.",
            STATUS.PROBLEM: "The server is on fire.",
        }[self.status()]


Notifications
=============

Email notifications can be sent out for warning or problem statuses. Each
Monitor has a `notifees` many-to-many field to
`django.contrib.auth.models.User`, and the notifees of a monitor will receive
its notification emails. Two management commands are provided:
`status_send_digest` and `status_send_instant.` The former sends a digest to
each user with any warning or problem monitors (you might want to have cron run
this daily or weekly); the latter sends a notification immediately, but only for
warning or problem monitors with `notify_type` set to
`django_status.models.NOTIFY.INSTANT` (you might want to have cron run this
every five minutes).

`status_send_digest` is smart enough not to spam your inbox - once it has sent
an instant notification for a given monitor M, it won't send notifications for M
again until it either becomes fine and then goes back to warning or problem, or
until `M.instant_notification_delay` seconds have elapsed since the last
notification for M. Note that this check only occurs when `status_send_instant`
is run, and so isn't necessarily appropriate for monitors whose statuses might
change with high frequency.

By default, only `User` objects with `is_staff == True` will be available as
notifees. This seems like the right choice for most use cases (and saves you
searching through your entire user table when setting up a monitor); if this
doesn't work for you, you can override the `notifees` field in your subclass.

Notifications will be sent from `settings.django_STATUS_FROM_EMAIL`, defaulting
to `status@<your domain>`.


Installation and Usage
======================

* Check out this repo to somewhere on your PYTHONPATH.
* Add `'django_status'` to settings.INSTALLED_APPS.
* Subclass `django_status.models.Monitor`. Override the `status` method, which
  returns a value from `django_status.models.STATUS`.
** There is one subclass provided, `django_status.models.AgeMonitor`. This is
   useful if you want to monitor a timedelta. Just override `get_age` (which
   should return a timedelta), `warning_seconds` (an integer), and
   `problem_seconds` (another integer). (These aren't instances of
   `IntegerField` in the base class, but you could certainly override them to
   make them so for your monitor.)
* Register your monitor class by passing it to `django_status.monitor.register`.
  For example:
`from django_status.monitors import register
register(MyMonitor)`
** If you put an app's Monitor subclasses in e.g. monitors.py, you can pass the
   entire module to `register` instead, e.g. in the app's __init__.py.
** Registering a Monitor subclass with django\_status will automatically
   register it in the Django admin.
* Route a URL (e.g. `r'^status/$'`) to `django_status.views.status`.
* Copy the included template and CSS to the appropriate locations (or create
  your own).  Make sure the path to status.css in your template is correct.
* Instantiate your `Monitor` subclass(es) via the Django admin.
