from django.urls import path
from . import views
from .postbacks import offerwall_postback

urlpatterns = [
    path('', views.home, name='home'),
    path('register/', views.register, name='register'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('tasks/', views.tasks, name='tasks'),
    path('tasks/<int:task_id>/', views.complete_task, name='complete_task'),
    path('withdraw/', views.withdraw, name='withdraw'),
    path('api/postback/<slug:provider_slug>/', offerwall_postback, name='offerwall_postback'),
]
