import json
import logging
from django.template.loader import render_to_string
from django import template
from newsroom.models import Article, WetellBulletin
from django.template.loader import render_to_string

logger = logging.getLogger("django")

register = template.Library()

@register.simple_tag
def contains_class(field, cls):
    if 'class' in field.widget.attrs:
        if cls in field.widget.attrs['class']:
            return True
    return False

@register.simple_tag
def visible_btn(pk, field):
    pk = int(pk)
    article = Article.objects.get(pk=pk)
    if 'data-not' in field.widget.attrs: # data-not only has to exist for negation
        op = lambda x: not x
    else:
        op = lambda x: x
    if 'data-visible' in field.widget.attrs:
        attr = getattr(article, field.widget.attrs['data-visible'])
        if callable(attr):
            return op(attr())
        return op(attr)
    return op(True) # Default is visible

@register.simple_tag
def display_btn(field, start_html, end_html, cls):
    result = start_html
    result += "<button id='" + field.html_name + "' class='" + cls + "'>" + field.label + "</button>"
    result += end_html
    return result

def wetell_text(bulletin, intro_only=False):
    try:
        context = json.loads(bulletin.data)
    except Exception as e:
        msg = "Error converting bulletin data" + str(e)
        logger.error(msg)
        return

    context['published'] = bulletin.published
    if intro_only:
        return context['intro']
    else:
        text = render_to_string('newsroom/wetell.html', context)
    return text

@register.simple_tag
def wetell_by_pk(pk, intro_only=True):
    try:
        bulletin = WetellBulletin.objects.get(pk=pk)
    except WetellBulletin.DoesNotExist:
        logger.error("Wetell bulletin not found")
        return ""

    return wetell_text(bulletin, intro_only)

@register.simple_tag
def wetell():
    try:
        bulletin = WetellBulletin.objects.latest('published')
    except WetellBulletin.DoesNotExist:
        logger.error("Wetell bulletin not found")
        return

    return wetell_text(bulletin)
