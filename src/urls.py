from django.shortcuts import render
from django.urls import path
from src import views

urlpatterns=[

    path("",views.view_immo,name="view_test"),
]
