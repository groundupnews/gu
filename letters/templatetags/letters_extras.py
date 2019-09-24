from random import randint

from django.template.loader import render_to_string
from django import template

from letters.models import Letter

register = template.Library()

@register.simple_tag
def letter_random():
    r = randint(0, 5)
    try:
        letter = Letter.objects.published().filter(recommended=True)[r]
    except IndexError:
        letter = None
    return render_to_string("letters/letters_tag_random.html",
                            {'object': letter})
