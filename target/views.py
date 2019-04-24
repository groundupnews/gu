from django.shortcuts import render
from django.views import generic
from . import models
from target.target import makeTarget
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


class TargetCreate(PermissionRequiredMixin, generic.edit.CreateView):
    permission_required = 'target.create_target'
    model = models.Target
    fields = ['letters', 'bullseye', 'words', 'published', 'public_solution']
    target = ""

    def get_initial(self):
        puzzle = makeTarget()
        self.target = puzzle['target']
        return {'letters': ''.join(puzzle['letters']),
                'bullseye': puzzle['bullseye'],
                'words': '\n'.join(puzzle['words'])}

    def form_valid(self, form):
        if self.request.method == 'POST':
            if self.request.POST.get("save_continue"):
                result = super().form_valid(form)
                if self.object:
                    return HttpResponseRedirect(reverse('target:update',
                                                        args=(self.object.pk,)))
                else:
                    return result
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['target'] = self.target
        return context

class TargetUpdate(PermissionRequiredMixin, generic.edit.UpdateView):
    permission_required = 'target.change_target'
    model = models.Target
    fields = ['letters', 'bullseye', 'words', 'published', 'public_solution']

    def form_valid(self, form):
        if self.request.method == 'POST':
            if self.request.POST.get("save_continue"):
                super().form_valid(form)
                return HttpResponseRedirect(self.request.path_info)
        return super().form_valid(form)

class TargetDelete(PermissionRequiredMixin, generic.edit.DeleteView):
    permission_required = 'target.delete_target'
    model = models.Target
    success_url = reverse_lazy('target:list')
