from django.db.models.base import ModelBase

from models import Monitor

from types import ModuleType

monitors = []

def is_monitor(maybe_monitor):
    return type(maybe_monitor) == ModelBase and issubclass(maybe_monitor, Monitor) and maybe_monitor is not Monitor

def register(monitor_or_module):
    """
    Either registers all subclasses of Monitor in the given module, or registers
    the given subclass of Monitor.
    """
    if type(monitor_or_module) == ModuleType:
        for monitor in monitor_or_module.__dict__.values():
            if is_monitor(monitor):
                register(monitor)
    else:
        if is_monitor(monitor_or_module) and monitor_or_module not in monitors and not monitor_or_module._meta.abstract:
            monitors.append(monitor_or_module)
