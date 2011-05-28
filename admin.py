from models import *
import monitors

from django.contrib import admin

for monitor in monitors.monitors:
    admin.site.register(monitor)
