# -*- coding: utf-8 -*-
from functools import wraps


def smart_login_required(view):
    """
        A smart login required that handle both ajax calls and normal request
    """

    @wraps(view)
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated():
            if request.is_ajax():
                raise PermissionDenied
            else:
                return login_required(view)(request, *args, **kwargs)
        return view(request, *args, **kwargs)

    return wrapper

#
# class custom_permissions_required(object):
#     """ A decorator to check if the user logged has permissions to access some views """
#
#     def __init__(self, permissions, **kwargs):
#         self.permissions = permissions
#         self.message = kwargs.get('message', 'You are not authorized to access this url')
#
#     def __call__(self, wrapped_function):
#         def inner(request, *args, **kwargs):
#             return check_user_permissions_request(request, permissions=self.permissions,
#                                                   message=self.message,
#                                                   call_back=partial(wrapped_function, request,
#                                                                     *args,
#                                                                     **kwargs),
#                                                   **kwargs)
#
#         return inner
#
#
# def check_user_permissions_request(request, permissions, message=None, call_back=None, **kwargs):
#     from core.views.utils import clean_permissions
#
#     # Get custom user
#     custom_user = CustomUser.objects.get(username=request.user.username)
#
#     # If the list of permissions required is just a simple tuple it is required to convert
#     # it into a tuple of tuples
#     if isinstance(permissions, (tuple, list)) and not isinstance(permissions[0], (tuple, list)):
#         permissions = (permissions,)
#
#     cleaned_permissions = clean_permissions(kwargs.get('id'), *permissions)
#
#     if custom_user.has_permissions(*cleaned_permissions):
#         # User have the necessary permissions
#         if call_back:
#             return call_back()
#         return True
#     else:
#         # User doesn't have the necessary permissions
#         context = {'title': 'Permissions Error',
#                    'message': message or ''}
#         return HttpResponse(
#             render_to_string('info.html', context,
#                              context_instance=RequestContext(request)),
#             status=401)