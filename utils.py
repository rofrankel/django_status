from monitors import monitors as monitor_types

def all_monitors(filter_kwargs={}, exclude_kwargs={}):
    monitors = []
    for type in monitor_types:
        monitors += list(type.objects.filter(**filter_kwargs).exclude(**exclude_kwargs))
    
    return monitors