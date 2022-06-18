from django.contrib import admin
from django.urls import path,include
from . import views
urlpatterns = [
    path('',views.index,name="index"),
    path('addfile/',views.addfile,name="addfile"),
    path('openfile/',views.readfile,name="openfile"),
    path('dictionary/',views.dictionary,name="dictionary"),
]