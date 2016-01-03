from django.shortcuts import render
from django.http import HttpResponseRedirect
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib import messages
from django.core.cache import caches
import sys

from .forms import ClearCacheForm

@staff_member_required
def clear_cache(request):
    if request.method == 'POST':
        form = ClearCacheForm(request.POST)
        if form.is_valid():
            try:
                cache = caches["default"]
                cache.clear()
                messages.add_message(request, messages.INFO,
                                     "Cache successfully cleared.")
            except:
                msg = "There was a problem clearing the cache: ." +  \
                      str(sys.exc_info()[0])
                messages.add_message(request, messages.ERROR, msg)
            form = ClearCacheForm()
            return render(request, 'clearcache/clearcache.html',
                          {'form': None })
        else:
            messages.add_message(request, messages.ERROR,
                                 "There was a problem clearing the cache.")
            return render(request, 'clearcache/clearcache.html',
                          {'form': form})

    # if a GET (or any other method) we'll create a blank form
    else:
        form = ClearCacheForm()

    return render(request, 'clearcache/clearcache.html', {'form': form})
