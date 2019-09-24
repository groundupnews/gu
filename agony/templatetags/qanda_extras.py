from django.template.loader import render_to_string
from django import template

from agony.models import QandA

register = template.Library()

@register.simple_tag
def qanda_random():
    qanda = QandA.objects.published().filter(recommended=True). \
                                                order_by('?').first()
    return render_to_string("agony/qanda_tag_random.html",
                            {'object': qanda})
