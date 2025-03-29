"""
Account view module.
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Self

from .._aux import MILI_DATE_FMT
from .role import AccountRole


@dataclass(kw_only=True)
class AccountView:
    "A basic view of an Account."

    id: int
    username: str
    created_at: datetime = field(repr=False)
    role: AccountRole


    @classmethod
    async def from_dict(cls, **fields) -> Self:
        """
        Initializes an AccountView instance from a response fields.

        :return: An instace of an account view.
        """

        created_date = fields.get("created_at")
        if isinstance(created_date, str):
            created_date = datetime.strptime(created_date, MILI_DATE_FMT)

        role = fields.get("role")
        if isinstance(role, str):
            role = (AccountRole(role) if role in AccountRole else AccountRole.CONSUMER)


        return cls(
            id=fields.get("id"),
            username=fields.get("username"),
            created_at=created_date,
            role=role
        )
