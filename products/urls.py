from django.urls import path

from products import views

urlpatterns = [
    path('create', views.create, name='create')
]
