"""
URL patterns for the publications app.
"""
from django.conf.urls import url

from . import views

urlpatterns = [
    url(r"^$", views.list_for_all, name="publications-main"),
    url(r"^by-person/$", views.list_people_with_pubs, name="publications-people-list"),
    url(r"^add/$", views.add, name="publications-add"),
    url(r"^update/(?P<refkey>[\:\w-]+)/$", views.update, name="publications-edit"),
    url(
        r"^update/(?P<refkey>[\:\w-]+)/delete$",
        views.delete_view,
        name="publications-delete",
    ),
    url(r"^bibtex-upload/$", views.bibtex_upload, name="publications-bibtex-upload"),
    url(
        r"^(?P<slug>[\w-]+)/$", views.list_for_person, name="publications-personal-list"
    ),
    url(
        r"^(?P<slug>[\w-]+)/bibtex-upload/$",
        views.bibtex_upload_for_person,
        name="publications-bibtex-upload-for-person",
    ),
    url(
        r"^(?P<slug>[\w-]+)/bibtex/$",
        views.bibtex_for_person,
        name="publications-personal-bibtex",
    ),
]
