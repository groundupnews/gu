from django.template.loader import render_to_string
from django import template

from sudoku.models import Sudoku

register = template.Library()

@register.simple_tag
def sudoku_teaser(pk=None):
    if pk is None:
        sudoku = Sudoku.objects.published().latest('published')
    else:
        pk = int(pk)
        sudoku = Sudoku.objects.published().filter(pk=pk)
    return render_to_string("sudoku/sudoku_teaser.html",
                            {'object': sudoku})
