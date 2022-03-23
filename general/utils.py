# -*- coding: utf-8 -*-

# --------------------------------------------------------
# Custom mixins for generic class-based views
# http://brack3t.com/our-custom-mixins.html
# ---------------------------------------------------------
from django.utils.decorators import method_decorator
from general.decorators import smart_login_required


class LoginRequiredMixin(object):
    """
    Mixin to implement the functionality of a login_required decorator
    in generic class-based views
    """

    @method_decorator(smart_login_required)
    def dispatch(self, *args, **kwargs):
        return super(LoginRequiredMixin, self).dispatch(*args, **kwargs)

# customized implementation of PermissionRequiredMixin from above url
# class PermissionRequiredMixin(object):
#     '''
#     Mixin to implement checking for custom permissions, essentially the same
#     functionality as core.views.decorators.custom_permissions_required decorator.
#
#     Also implements login checking, same way as LoginRequiredMixin
#
#     Class Settings
#      - permission_required:
#         iterable of tuples of core.constants.PERMISSION_CATEGORIES
#         and core.constants.PERMISSION_TYPES
#      - permission_missing_message:
#         the message to be displayed if the user is missing the required permission.
#
#     Example:
#
#     class MyListView(PermissionRequiredMixin, ListView):
#         permission_required = ((PERM_CAT, PERMISSION_TYPES.list))
#         (...)
#
#
#     '''
#     permission_required = None
#     permission_missing_message = 'You are not authorized to access this url'
#
#     @method_decorator(smart_login_required)
#     def dispatch(self, request, *args, **kwargs):
#         # Verify class settings
#         if self.permission_required is None:
#             raise ImproperlyConfigured("'PermissionRequiredMixin' requires "
#                                        "'permission_required' attribute to be set.")
#         custom_user = CustomUser.objects.get(username=request.user.username)
#
#         # If the list of permissions required is just a simple tuple it is required to convert it
#         # into a tuple of tuples
#         if isinstance(self.permission_required, (tuple, list)) and not isinstance(
#                 self.permission_required[0], (tuple, list)):
#             self.permission_required = (self.permission_required,)
#
#         # If some permissions are like (None, permission) it should instanciate None to the entity
#         # type of the id in kwargs
#         self.permission_required = clean_permissions(kwargs.get('id'), *self.permission_required)
#
#         has_permission = custom_user.has_permissions(*self.permission_required)
#
#         if not has_permission:
#             # User doesn't have the necessary permissions
#             context = {
#                 'title': 'Permission Error',
#                 'message': self.permission_missing_message}
#             return render_to_response(
#                 'info.html',
#                 context,
#                 context_instance=RequestContext(request))
#
#         # User has permission
#         return super(PermissionRequiredMixin, self).dispatch(request, *args, **kwargs)
#
