from django.urls import path, include
from . import views

urlpatterns= [
    path('', views.index, name='index'),
    path('logout/', views.logout, name='logout'),
    path('login/', views.login, name='login'),
    path('analyza/<int:id>', views.analyza, name='analyza'),
    path('analyza/<int:id>/<str:id2>', views.analyzaVystup, name='analyzaVystup'),
]