from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('submit/', views.submit_feedback, name='submit_feedback'),
    path('professor/<int:professor_id>/', views.professor_detail, name='professor_detail'),
    
]