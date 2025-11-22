"""youtube_downloader URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from django.conf import settings
from django.urls import path,include
from django.urls import re_path as url
from django.conf import settings
from django.views.static import serve
from . import views
from .views import ckeditor_upload
from django.http import HttpResponse
import os
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

def robots_txt(request):
    file_path = os.path.join(BASE_DIR, 'robots.txt')
    with open(file_path, 'r') as file:
        return HttpResponse(file.read(), content_type="text/plain")

def sitemap_xml(request):
    file_path = os.path.join(BASE_DIR, 'sitemap.xml')
    with open(file_path, 'r') as file:
        return HttpResponse(file.read(), content_type="application/xml")
    
urlpatterns = [
    url(r'^media/(?P<path>.*)$', serve,{'document_root': settings.MEDIA_ROOT}),
    url(r'^static/(?P<path>.*)$', serve,{'document_root': settings.STATIC_ROOT}),
    path("api/",include("api.urls")),
    path("search",views.search_video),
    path("audio",views.audio),
    path("video",views.video),
    path('robots.txt', robots_txt, name='robots_txt'),
    path('sitemap.xml', sitemap_xml, name='sitemap_xml'),
    path('ckeditor/upload/', ckeditor_upload, name='ckeditor_upload'),
    path("admin/panel/install",views.install,name="install"),
    path("admin/panel/home",views.home_page,name="home_page"),
    path("admin/panel/login",views.login_page,name="login_page"),
    path("admin/panel/logout",views.logout,name="logout"),
    path("admin/panel/account",views.account_page,name="account_page"),
    path("admin/panel/languages",views.languages_page,name="languages_page"),
    path("admin/panel/add-new-language",views.add_new_language_page,name="add_new_language_page"),
    path("admin/panel/language/<int:id>/pages",views.language_pages_page,name="language_pages_page"),
    path("admin/panel/language/<int:id>/edit",views.language_edit_page,name="language_edit_page"),
    path("admin/panel/language/<int:id>/add-new-cutom-page",views.add_new_cutom_page,name="add_new_cutom_page"),
    path("admin/panel/language/<int:id>/edit-cutom-page",views.edit_cutom_page,name="edit_cutom_page"),
    path("admin/panel/api",views.api,name="api"),
    path("admin/panel/theme",views.theme,name="theme"),
    path("admin/panel/logo-&-favicon",views.logo_and_favicon,name="logo_and_favicon"),
    path("admin/panel/global-header",views.global_header_page,name="global_header_page"),
    path("admin/panel/global-footer",views.global_footer_page,name="global_footer_page"),
    path("admin/panel/redirects",views.redirects_page,name="redirects_page"),
    path("admin/panel/robots-dot-txt",views.robots_dot_txt_page,name="robots_dot_txt_page"),
]