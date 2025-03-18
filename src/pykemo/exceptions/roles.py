"""
Roles exceptions module.
"""

from .general import PyKemoException


class InvalidRole(PyKemoException):
    "A different account role was expected."