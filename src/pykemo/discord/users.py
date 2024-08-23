"""
Discord users module.
"""

from dataclasses import dataclass, field
from typing import Any, Optional

from ..core import UrlType
from ..files import File


@dataclass(kw_only=True)
class DiscordUser:
    """
    A discord user. Not to be confused with :class:`.Creator`, as they have different properties.

    :param id: The ID of the Discord user. The same the Discord API uses.
    :param username: The specific username that the user utilizes in this guild.
    :param global_name: The global name the Discord user has.
    :param discriminator: The discriminator of the Discord user, if any (they are not really used anymore).
    :param avatar: The avatar file.
    :param avatar_decoration_data: Aditional avatar info.
    :param clan: I guess this refers to the HypeSquad clans.
    :param accent_color: The accent color that the user chooses.
    :param banner: The banner of the user profile.
    :param banner_color: The accent color for the banner itself.
    :param flags: The flags in this guild.
    :param public_flags: The flags globally.

    :type id: :class:`str`
    :type username: :class:`str`
    :type global_name: :class:`str`
    :type discriminator: :class:`str`
    :type avatar: :class:`.File`
    :type avatar_decoration_data: Optional[:class:`Any`]
    :type clan: Optional[:class:`Any`]
    :type accent_color: Optional[:class:`str`]
    :type banner: Optional[:class:`Any`]
    :type banner_color: Optional[:class:`str`]
    :type flags: :class:`int`
    :type public_flags: :class:`int`
    """

    id: str
    username: str
    global_name: str
    discriminator: str
    avatar: File = field(repr=False)
    avatar_decoration_data: Optional[Any] = field(default=None, repr=False)
    clan: Optional[Any] = field(default=None, repr=False)
    accent_color: Optional[str] = field(default=None, repr=False)
    banner: Optional[Any] = field(default=None, repr=False)
    banner_color: Optional[str] = field(default=None, repr=False)
    flags: int = field(default=0, repr=False)
    public_flags: int = field(default=0, repr=False)


    @classmethod
    def from_dict(cls, **fields) -> "DiscordUser":
        """
        Initializes a DiscordUser instance from a response fields.

        :return: A user instance.
        :rtype: :class:`DiscordUser`
        """

        user_id = fields.get("id")
        username = fields.get("username")

        avatar_subpath = fields.get("avatar")
        avatar = File(name=f"{username}_avatar.png",
                      path=f"/avatars/{user_id}/{avatar_subpath}",
                      url_source=UrlType.DISCORD)


        return cls(
            id=user_id,
            username=username,
            global_name=fields.get("global_name"),
            discriminator=fields.get("discriminator"),
            avatar=avatar,
            avatar_decoration_data=fields.get("avatar_decoration_data", None),
            clan=fields.get("clan", None),
            accent_color=fields.get("accent_color", None),
            banner=fields.get("banner", None),
            banner_color=fields.get("banner_color", None),
            flags=fields.get("flags", 0),
            public_flags=fields.get("public_flags", 0)
        )
