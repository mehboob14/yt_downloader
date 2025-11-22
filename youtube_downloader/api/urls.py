from django.urls import path
from . import views
urlpatterns = [
    path("admin/login",views.api_admin_login,name="api_admin_login"),
    path("admin/update",views.api_admin_update,name="api_admin_update"),
    path("create-new-langauge",views.create_new_language,name="create_new_language"),
    path("edit-language",views.edit_language,name="edit_language"),
    path('delete-language/<int:language_id>/', views.delete_language, name='delete_language'),
    path("add-new-cutom-page",views.add_new_cutom_page,name="add_new_cutom_page"),
    path("edit-cutom-page",views.edit_cutom_page,name="edit_cutom_page"),
    path('delete-custom-page/<int:page_id>/', views.delete_custom_page, name='delete_custom_page'),
    path("settings",views.api_settings,name="api_settings"),
    path("theme",views.theme,name="theme"),
    path("logo-and-favicon",views.logo_and_favicon,name="logo_and_favicon"),
    path("global-header/update",views.api_global_header_update,name="api_global_header_update"),
    path("global-footer/update",views.api_global_footer_update,name="api_global_footer_update"),
    path("redirect/create",views.api_redirect_create,name="api_redirect_create"),
    path("redirect/delete",views.api_redirect_delete,name="api_redirect_delete"),
    path("direct-redirect/delete",views.api_direct_redirect_delete,name="api_direct_redirect_delete"),
    path("redirect",views.api_redirect,name="api_redirect"),
    path("robots-dot-txt/update",views.api_robots_dot_txt_update,name="api_robots_dot_txt_update"),
]