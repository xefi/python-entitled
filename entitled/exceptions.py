"""Authorization related exceptions"""


class AuthorizationException(Exception):
    """Raised when an authorization is denied"""


class UndefinedAction(AuthorizationException):
    """Raised when attempting to authorize an undefined action"""
