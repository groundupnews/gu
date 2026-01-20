import string

from django.contrib import messages
from django.shortcuts import render
from django.views import generic
from . import models
from target.target import makeTarget
from target.utils import saveTargetImage
from django import forms
from django.http import HttpResponseRedirect, Http404
from django.urls import reverse, reverse_lazy
from django.contrib.auth.mixins import PermissionRequiredMixin


class TargetList(generic.ListView):
    model = models.Target
    paginate_by = 10

    def get_queryset(self):
        if self.request.user.has_perm("target.change_target"):
            return models.Target.objects.all()
        else:
            return models.Target.objects.published()


class TargetDetail(generic.DetailView):
    model = models.Target

    def get_object(self):
        puzzle = super().get_object()
        if puzzle.is_published() or \
           self.request.user.has_perm("target.change_target"):
            return puzzle
        else:
            raise Http404

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        number = self.object.number
        if number > 0:
            p = models.Target.objects.published().filter(number__lt=number).first()
            context['previous_target'] = p
            n = models.Target.objects.published().filter(number__gt=number).last()
            context['next_target'] = n
        return context

def is_valid_word(word, letters):
    for c in word:
        if word.count(c) > letters.count(c):
            return False
    return True

def validate_form(words, letters):
    msg = ""

    # Exactly 9 letters
    if len(letters) != 9:
        return {
            "status": False,
            "msg": "Must be exactly 9 letters",
            "field": "letters"
        }

    # Check for invalid letters
    l = [l for l in letters if not (l in string.ascii_lowercase)]
    if len(l) > 0:
        return {
            "status": False,
            "msg": "Invalid letters: " + ','.join(l),
            "field": "letters"
        }

    words = words.split("\r\n")
    # Check all words contain bullseye
    w = [w for w in words if letters[0] not in w]

    if len(w) > 0:
        return {
            "status": False,
            "msg": "Words without bullseye: " + ','.join(w),
            "field": "words"
        }

    # Check all words only contain target letters

    w = [w for w in words if not is_valid_word(w, letters)]

    if len(w) > 0:
        return {
            "status": False,
            "msg": "Words with wrong letters: " + ','.join(w),
            "field": "words"
        }

    # Check for one 9-letter word
    if len([w for w in words if len(w) == 9]) != 1:
        return {
            "status": False,
            "msg": "There must be exactly one 9-letter word",
            "field": "words"
        }

    # Check for short words
    w = [w for w in words if len(w) < 4]
    if len(w):
        return {
            "status": False,
            "msg": "Shorter than 4 letters: " + ','.join(w),
            "field": "words"
        }

    return {
        "status": True,
        "error": None,
        "field": None
    }

class TargetUpdate(PermissionRequiredMixin, generic.edit.UpdateView):
    permission_required = 'target.change_target'
    model = models.Target
    fields = [ 'letters', 'words', 'published', 'publish_solution_after',
               'clue', 'tweet_text',
               'rules', ]

    def post(self, request, *args, **kwargs):
        if "cancel" in request.POST:
            return HttpResponseRedirect(reverse_lazy('target:list'))
        elif "delete" in request.POST:
            pk = self.get_object().pk
            return HttpResponseRedirect(reverse_lazy('target:delete', args=(pk,)))
        else:
            return super().post(request, *args, **kwargs)

    def form_valid(self, form):
        form.instance.words = '\r\n'.join(sorted(set(form.instance.words.
                                                          split("\r\n"))))
        validation = validate_form(form.instance.words,
                                   form.instance.letters)
        if validation["status"] == False:
            form.add_error(validation["field"], validation["msg"])
            return self.form_invalid(form)

        if self.request.method == 'POST':
            fv = super().form_valid(form)
            saveTargetImage(list(self.object.letters.upper()), self.object.pk)
            messages.add_message(self.request, messages.INFO, "Target saved")
            if self.request.POST.get("save_continue"):
                return HttpResponseRedirect(reverse_lazy("target:update",
                                                         args=(self.object.pk,)))
            else:
                return fv
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.object:
            try:
                context['nine_letter_word'] = [w for w in
                                               self.object.words.split("\r\n")
                                               if len(w) == 9][0]
            except:
                context['nine_letter_word'] = ""
                messages.add_message(self.request, messages.WARNING,
                                     "No nine letter found")
        return context


class TargetCreate(TargetUpdate):
    permission_required = 'target.add_target'
    nine_letter_word = ""

    def get_initial(self):
        if 'letters' in self.kwargs:
            puzzle = makeTarget(user_letters=self.kwargs['letters'])
        else:
            puzzle = makeTarget()
        self.nine_letter_word = puzzle['target']
        return {'letters': ''.join(puzzle['letters']),
                'bullseye': puzzle['letters'][0],
                'words': '\n'.join(puzzle['words'])}

    def get_object(self, queryset=None):
        try:
            return super().get_object(queryset)
        except AttributeError:
            return None

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['nine_letter_word'] = self.nine_letter_word
        return context


class TargetDelete(PermissionRequiredMixin, generic.edit.DeleteView):
    permission_required = 'target.delete_target'
    model = models.Target
    success_url = reverse_lazy('target:list')


class TargetLatest(generic.RedirectView):
    def get_redirect_url(self, *args, **kwargs):
        target = models.Target.objects.published().latest('published')
        return reverse('target:detail', args=[target.pk])
