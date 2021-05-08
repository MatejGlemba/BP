from django.urls import path, include
from . import views

urlpatterns= [
    path('', views.index, name='index'),
    path('logout/', views.logout, name='logout'),
    path('login/', views.login, name='login'),
    path('data/', views.data, name='data'),
]