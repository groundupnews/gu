from django.shortcuts import render
from django.views import generic
from django.contrib.admin.views.decorators import staff_member_required
from . import models


class LicenceList(generic.ListView):
    model = models.Licence
    paginate_by = 100


class LicenceDetail(generic.DetailView):
    model = models.Licence
