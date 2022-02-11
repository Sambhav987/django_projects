from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("<str:title>", views.entry, name="entryPage"),
    path("search/",views.search, name="search"),
    path("new/",views.new, name="new"),
    path("random/",views.random, name ="random"),
    path("edit/",views.edit, name="edit"),
    path("save/",views.save, name="save")
]