from django.urls import path, include
from . import views

urlpatterns= [
    path('', views.index, name='index'),
    path('ajax/getLogs', views.getLogs, name='getLogs'),
    path('logout/', views.logout, name='logout'),
    path('login/', views.login, name='login'),
    path('analyza/', views.analyza, name='analyza'),
    path('analyza/<int:id>', views.analyzaVystup, name='analyzaVystup'),
]