from django.views.generic.detail import DetailView
from django.shortcuts import get_object_or_404, render
from django.utils.translation import gettext_lazy as _
from django.contrib import messages
from django.urls import reverse
from django.http import HttpResponseRedirect
from django.http import Http404

from sudoku.models import Sudoku

class SudokuDetailView(DetailView):
    model = Sudoku

    def get_object(self, queryset=None):
        try:
            sudoku = super().get_object(queryset)
        except:
            raise Http404

        if self.request.user.is_staff is False:
            if sudoku.is_published() is False:
                raise Http404

        if sudoku.is_published() is False:
            messages.add_message(self.request, messages.INFO,
                                 "This Sudoku puzzle is not published.")
        return sudoku

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['choices'] = Sudoku.Difficulty.choices
        if 'diff' in self.request.GET:
            context['difficulty'] = self.request.GET['diff']
        else:
            context['difficulty'] = '0'
        return context

class SudokuLatest(SudokuDetailView):

    def get_object(self, queryset=None):
        sudoku = Sudoku.objects.published().latest('published')
        return sudoku


def nav(request, pk):
    puzzle = get_object_or_404(Sudoku, pk=pk)
    try:
        nav = request.GET['nav']
        difficulty = request.GET['diff']
    except:
        nav = 'prev'
        difficulty = '0'

    if difficulty == '0':
        lo_diff = '0'
        hi_diff = max(Sudoku.Difficulty.choices)[0]
    else:
        lo_diff = difficulty
        hi_diff = difficulty

    try:
        if nav == 'next':
            pk_new = Sudoku.objects.published(). \
                filter(difficulty__gte=lo_diff). \
                filter(difficulty__lte=hi_diff). \
                filter(published__gt=puzzle.published).earliest('published').pk
        else:
            pk_new = Sudoku.objects.published(). \
                filter(difficulty__gte=lo_diff). \
                filter(difficulty__lte=hi_diff). \
                filter(published__lt=puzzle.published).latest('published').pk
    except Sudoku.DoesNotExist:
        pk_new=puzzle.pk

    url = reverse('sudoku:detail', args=(pk_new,)) + '?diff=' + difficulty
    return HttpResponseRedirect(url)
