# -*- coding: utf-8 -*-
"""
Global Django exception and warning classes.
"""


class PermissionDenied(Exception):
    """The user did not have permission to do that"""
    pass


class ViewDoesNotExist(Exception):
    """The requested view does not exist"""
    pass
