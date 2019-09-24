from django.template.loader import render_to_string
from django import template

from target.models import Target

register = template.Library()

@register.simple_tag
def target_teaser(pk=None):
    if pk is None:
        target = Target.objects.published().first()
    else:
        pk = int(pk)
        target = Target.objects.published()(pk=pk)
    return render_to_string("target/target_teaser.html",
                            {'object': target})
