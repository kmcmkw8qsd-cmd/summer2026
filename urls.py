from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('deen/', views.deen, name='deen'),
    path('sport/', views.sport, name='sport'),
    path('regime/', views.regime, name='regime'),
    path('learning/', views.learning, name='learning'),
    path('selfcare/', views.selfcare, name='selfcare'),
    path('homecare/', views.homecare, name='homecare'),
    path('goals/', views.goals, name='goals'),
]