from django.shortcuts import render
from django.views.generic import DetailView
from django.views.generic.edit import CreateView, UpdateView
from django.contrib.auth.mixins import PermissionRequiredMixin
from socialmedia.models import TwitterHandle

fields = ['name', 'slug',]

class TwitterHandleCreate(PermissionRequiredMixin, CreateView):
    permission_required = 'socialmedia.add_twitterhandle'
    model = TwitterHandle
    fields = fields

class TwitterHandleUpdate(PermissionRequiredMixin, UpdateView):
    permission_required = 'socialmedia.change_twitterhandle'
    model = TwitterHandle
    fields = fields

class TwitterHandleDetail(PermissionRequiredMixin, DetailView):
    permission_required = 'socialmedia.change_twitterhandle'
    model = TwitterHandle
