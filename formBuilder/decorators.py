from django.core.exceptions import PermissionDenied
from applicationModule.models import Application


def form_module_check(view_func):
    def wrap(request,*args, **kwargs):
        id = request.path.split('/')[3]
        app_obj = Application.objects.get(id=id)
        if app_obj.form_builder_module:
            return view_func(request,*args, **kwargs)
        else:
            raise PermissionDenied
    return wrap

