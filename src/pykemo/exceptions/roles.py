"""
Roles exceptions module.
"""

from .general import PyKemoException


class InvalidRole(PyKemoException):
    "A different account role was expected."


class InsufficientPrivileges(PyKemoException):
    "One does not have the required clearance for an operation."
