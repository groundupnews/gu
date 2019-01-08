from django.views.generic import ListView, DetailView
from django.http import Http404
from django.contrib import messages
from newsroom.models import Topic

from agony.models import QandA

class QandAList(ListView):
    paginate_by = 10

    def get_queryset(self):
        if 'topic' in self.request.GET:
            try:
                topic = int(self.request.GET['topic'])
                return QandA.objects.published().filter(topics__in=[topic,])
            except:
                pass
        return QandA.objects.published()


    def get_context_data(self, **kwargs):
        context = super(QandAList, self).get_context_data(**kwargs)
        if self.request.user.has_perm('agony.change_qanda'):
            context['can_edit'] = True
        else:
            context['can_edit'] = False
        if 'topic' in self.request.GET:
            try:
                topic = int(self.request.GET['topic'])
                topic = Topic.objects.get(pk=topic)
                context['topic'] = topic.name
            except:
                pass
        return context

class QandADetail(DetailView):
    model = QandA

    def get_object(self, queryset=None):
        obj = super(QandADetail, self).get_object()
        if obj.is_published() is False:
            if self.request.user.is_staff is True:
                messages.add_message(self.request, messages.INFO,
                                     "This Q&A is not published.")
            else:
                raise Http404
        return obj
