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


class RegisterError(PyKemoException):
    "Generic register error in connection."

class InvalidRegister(RegisterError):
    "Register failed due to user errors."