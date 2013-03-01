from django.conf.urls import patterns, url

from django.contrib import admin
admin.autodiscover()

from .views import (handle_login,
                    handle_logout,
                    get_models,
                    get_model_instances,
                    handle_instance_form)

urlpatterns = patterns('',
    # Examples:
    url(r'^login/$', handle_login, name='adminapi_handle_login'),
    url(r'^logout/$', handle_logout, name='adminapi_handle_logout'),
    url(r'^apps/$', get_models, name='adminapi_get_all_models'),
    url(r'^apps/(?P<app_label>\w+)/models/$', get_models, name='adminapi_get_models'),
    url(r'^apps/(?P<app_label>\w+)/models/(?P<model_name>\w+)/instances/$', get_model_instances, name='adminapi_get_model_instances'),
    url(r'^apps/(?P<app_label>\w+)/models/(?P<model_name>\w+)/instances/form/$', handle_instance_form, name='adminapi_handle_instance_add_form'),
    url(r'^apps/(?P<app_label>\w+)/models/(?P<model_name>\w+)/instances/(?P<instance_id>\d+)/form/$', handle_instance_form, name='adminapi_handle_instance_edit_form'),
)
