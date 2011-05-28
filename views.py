from django.views.generic.simple import direct_to_template
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from django.contrib.sites.models import Site

from models import *

from itertools import groupby

@login_required
def status(request):
    if not request.user.is_staff:
        from django.http import Http404
        raise Http404
    from monitors import monitors as monitor_types
    get_status = lambda m: m.status
    monitors = reduce(list.__add__, [list(type.objects.all()) for type in monitor_types])
    monitor_groups = sorted([(app, sorted(list(group), key=get_status, reverse=True)) for app, group in groupby(monitors, lambda m: m._meta.app_label)])
    monitors = sorted(monitors, key=get_status, reverse=True)
    
    data = {
        'monitors': monitors,
        'monitor_groups': monitor_groups,
        'site': Site.objects.get_current(),
    }
    
    return direct_to_template(request, 'status/status.html', data)