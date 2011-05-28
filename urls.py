from django.conf.urls.defaults import *

urlpatterns = patterns('django_status.views',
    url(r'^$', 'status', name='status',),
)
