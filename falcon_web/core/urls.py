from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('tasks/', views.tasks, name='tasks'),
    path('tasks/<int:task_id>/', views.complete_task, name='complete_task'),
    path('withdraw/', views.withdraw, name='withdraw'),
]
