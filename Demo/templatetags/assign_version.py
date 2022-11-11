from django import template
import time
register = template.Library()

version = 0
@register.simple_tag
def static_version():
    print("version changed!!")

    return version