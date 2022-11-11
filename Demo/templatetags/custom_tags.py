from django import template
from django.conf import settings
import time
register = template.Library()

ALLOWABLE_VALUES = ("PRO_HOST","SOCKET_SERVER")
#客製化讓前端模板取得setting
# settings value
@register.simple_tag
def settings_value(name):
    if name in ALLOWABLE_VALUES:
        return getattr(settings, name, '')
    return ''
version = 0
@register.simple_tag
def static_version():
    print("version changed!!")

    return version