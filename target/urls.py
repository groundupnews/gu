from django.urls import path

from . import views

app_name = "target"


urlpatterns = [
    path('targets/', views.TargetList.as_view(), name='list'),
    path('target/', views.TargetLatest.as_view(), name='latest'),
    path('target/<int:pk>', views.TargetDetail.as_view(), name='detail'),
    path('target/create/', views.TargetCreate.as_view(), name='create'),
    path('target/create/<str:letters>',
         views.TargetCreate.as_view(), name='create_letters'),
    path('target/update/<int:pk>', views.TargetUpdate.as_view(), name='update'),
    path('target/delete/<int:pk>', views.TargetDelete.as_view(), name='delete')

]
