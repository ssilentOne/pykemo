"""
Account view module.
"""

from typing import TYPE_CHECKING
from datetime import datetime
from dataclasses import dataclass, field

if TYPE_CHECKING:
    from .role import AccountRole


@dataclass(kw_only=True)
class AccountView:
    "A basic view of an Account."

    id: int
    username: str
    created_at: datetime = field(repr=False)
    role: "AccountRole"
