from django.urls import path
from agony.views import QandAList, QandADetail

app_name = "agony"

urlpatterns = [
    path('qanda/', QandAList.as_view(), name='list'),
    path('qanda/<int:pk>/', QandADetail.as_view(), name='detail'),
]
