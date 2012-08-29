from django.contrib.admin.sites import site
from django.core.serializers.json import simplejson as json
from django.core.urlresolvers import reverse, NoReverseMatch
from django.forms import ModelForm
from django.http import Http404, HttpResponse
from django.utils.text import capfirst

from django_remote_forms.forms import RemoteForm

from adminapi.apps.adminapi.utils import LazyEncoder


def handle_login(request):
    if request.method == 'GET':
        # Return login form
        pass
    elif request.method == 'POST':
        # Process login
        pass


def get_models(request, app_label=None):
    # Return data on all models registered with admin
    user = request.user

    if app_label is None:
        if user.is_staff or user.is_superuser:
            has_module_perms = True
    else:
        has_module_perms = user.has_module_perms(app_label)

    app_dict = {}

    for model, model_admin in site._registry.items():
        model_name = model._meta.module_name

        if app_label is not None and app_label != model._meta.app_label:
            continue
        else:
            current_app_label = model._meta.app_label

        if current_app_label not in app_dict:
            app_dict[current_app_label] = {}

        if has_module_perms:
            perms = model_admin.get_model_perms(request)

            # Check whether user has any perm for this module.
            # If so, add the module to the model_list.
            if True in perms.values():
                model_dict = {
                    'name': model_name,
                    'title': unicode(capfirst(model._meta.verbose_name_plural)),
                    'perms': perms,
                }
                if perms.get('change', False):
                    try:
                        model_dict['admin_url'] = reverse('adminapi_get_models', args=[app_label])
                    except NoReverseMatch:
                        pass
                if perms.get('add', False):
                    try:
                        model_dict['add_url'] = reverse('adminapi_handle_instance_form', args=[app_label, model_name])
                    except NoReverseMatch:
                        pass

                if app_dict[current_app_label]:
                    app_dict[current_app_label]['models'].append(model_dict),
                else:
                    # First time around, now that we know there's
                    # something to display, add in the necessary meta
                    # information.
                    app_dict[current_app_label] = {
                        'name': current_app_label.title(),
                        'title': '%s administration' % capfirst(current_app_label),
                        'has_module_perms': has_module_perms,
                        'models': [model_dict],
                    }
        # Sort the models alphabetically within each app.
        app_dict[current_app_label]['models'].sort(key=lambda x: x['name'])

    if not app_dict:
        raise Http404('The requested admin page does not exist')

    response_data = {
        'app_list': [app_dict],
    }

    return HttpResponse(json.dumps(response_data, cls=LazyEncoder), mimetype="application/json")


def get_model_instances(request, app_label, model_name):
    # Return list of instances for a given model
    response_data = {
        'app_label': app_label,
        'model_name': model_name,
        'instances': []
    }

    for model, model_admin in site._registry.items():
        if app_label != model._meta.app_label or model_name != model._meta.module_name:
            continue

        for model_instance in model.objects.all():
            response_data['instances'].append({
                'id': model_instance.pk,
                'title': unicode(model_instance),
                'add_url': reverse('adminapi_handle_instance_add_form', args=[app_label, model_name]),
                'edit_url': reverse('adminapi_handle_instance_edit_form', kwargs={
                    'app_label': app_label,
                    'model_name': model_name,
                    'instance_id': model_instance.pk
                }),
                'delete_url': ''
            })

    return HttpResponse(json.dumps(response_data, cls=LazyEncoder), mimetype="application/json")


def handle_instance_form(request, app_label, model_name, instance_id=None):
    response_data = {
        'app_label': app_label,
        'model_name': model_name
    }

    instance = None

    for model, model_admin in site._registry.items():
        if app_label != model._meta.app_label or model_name != model._meta.module_name:
            continue

        if instance_id is not None:
            response_data[instance_id] = instance_id
            try:
                instance = model.objects.get(pk=instance_id)
            except model.DoesNotExist:
                raise Http404('Invalid instance ID')

        current_model = model

        class CurrentModelForm(ModelForm):
            class Meta:
                model = current_model

        if request.method == 'GET':
            # Return instance form for given model name
            # Return initial values if instance ID is supplied, otherwise return empty form
            if instance is None:
                form = CurrentModelForm()
            else:
                form = CurrentModelForm(instance=instance)

                # Load initial data
                for field_name, field in form.fields.items():
                    if field_name in form.initial:
                        field.initial = form.initial[field_name]

            remote_form = RemoteForm(form)
            response_data['form'] = remote_form.as_dict()
        elif request.method == 'POST':
            # Create new instance for given data
            pass
        elif hasattr(request, 'raw_post_data'):
            # PUT data available, update instance
            pass

    return HttpResponse(json.dumps(response_data, cls=LazyEncoder), mimetype="application/json")
