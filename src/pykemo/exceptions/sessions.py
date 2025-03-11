"""
Custom sessions exceptions module.
"""

from .general import PyKemoException


class LoginError(PyKemoException):
    "Generic login error in connection."


class InvalidLogin(LoginError):
    "The login was unsuccessful."


class AlreadyLoggedIn(LoginError):
    "The user is already logged in."