"""
Administrator account module.
"""

from .base import _AccountBase, _AccountParams
from .cons import _ConsumerMixin
from .mod import _ModeratorMixin
from .role import AccountRole


class _AdministratorMixin(_AccountParams):
    "A basic compound of all moderator level operations."


class Admin(_AccountBase, _ConsumerMixin, _ModeratorMixin, _AdministratorMixin):
    """
    An administrator account.

    .. warning:: It is not recommended to use unless you know what you're doing. Methods like :meth:`.login()` are preferred as they automatically create a session internally.
    
    :param id: The account ID.
    :param username: The name of the user's account.
    :param created_at: When was the account created.
    :param ks: The underlying session of the account context.

    :type id: :class:`int`
    :type username: :class:`str`
    :type created_at: :class:`datetime.datetime`
    :type ks: :class:`.KemoSession`
    """

    @staticmethod
    def role() -> AccountRole:
        return AccountRole.ADMINISTRATOR
