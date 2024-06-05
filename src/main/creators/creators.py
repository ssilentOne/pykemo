"""
Creators module.
"""

from datetime import datetime
from typing import TYPE_CHECKING, Literal, Optional, TypeAlias, Union

from ..core import get, UrlType
from ..posts import Post

if TYPE_CHECKING:
    from ..core import UrlLike
    from ..services import ServiceLike

_CreatorFields: TypeAlias = Literal["id", "name", "service", "indexed", "updated", "public_id", "favorited"]
CreatorDict: TypeAlias = dict[_CreatorFields, str | int | None]


class Creator:
    """
    Container class for a creator.
    """

    def __init__(self,
                 *,
                 id: str,
                 name: str,
                 service: "ServiceLike",
                 indexed: datetime,
                 updated: datetime,
                 public_id: str,
                 favorited: int) -> None:
        """
        Initializes a Creator.

        id: It is the ID of the creator.
        name: It is the given name of the creator.
        service: The service that provides the content.
        indexed: Datetime that expresses when the creator is indexed.
        updated: Datetime that expresses when the creator was last updated.
        favorited: A integer displaying how many have favorited this creator.
        """

        self._id: str = id
        self._name: str = name
        self._service: "ServiceLike" = service
        self._indexed: datetime = indexed
        self._updated: datetime = updated
        self._public_id: str = public_id
        self._favorited: int = favorited


    @classmethod
    def from_dict(cls, **fields: CreatorDict) -> "Creator":
        """
        Initializes a creator from a dictionary containing its properties.
        """

        date_fmt = r"%Y-%m-%dT%H:%M:%S.%f"

        return cls(
            id=fields.get("id", None) or fields.get("user"),
            name=fields.get("name", None),
            service=fields.get("service", None),
            indexed=datetime.strptime(fields.get("indexed"), date_fmt),
            updated=datetime.strptime(fields.get("updated"), date_fmt),
            public_id=fields.get("public_id", None),
            favorited=fields.get("favorited", None)
        )


    @classmethod
    def from_profile(cls, service: "ServiceLike", creator_id: str) -> Optional["Creator"]:
        """
        Retrieves a creator using its profile info.
        """

        creator_response = get(f"/{service}/user/{creator_id}/profile")

        if creator_response.status_code == 404:
            return None

        return Creator.from_dict(**creator_response.json())


    @staticmethod
    def query_params(query: Optional[str], offset: Optional[int]) -> dict[str, Union[str, int]]:
        "Porcesses and creates a dictionary that is the aprameters of a request."

        params = {}

        if query is not None:
            params.update(q=query)

        if offset is not None:
            if offset % 50 != 0:
                raise ValueError(f"Value for offset {offset} not valid. Must be a multiple of 50.")

            params.update(o=offset)

        return params


    def __str__(self) -> str:
        "Represents the Creator class in a string."

        return repr(self)
    

    def __repr__(self) -> str:
        "Represents a creator as-is."

        return f"<Creator '{self.name}'>"


    @property
    def id(self) -> str:
        "Gives the ID of the creator."

        return self._id


    @property
    def name(self) -> str:
        "Gives the name of the creator."

        return self._name


    @property
    def service(self) -> "ServiceLike":
        "Gives the service of the content of the creator."

        return self._service


    @property
    def indexed(self) -> datetime:
        """
        Gives the string for when the creator was indexed.
        """

        return self._indexed


    @property
    def updated(self) -> datetime:
        """
        Gives the string for when the creator was updated..
        """

        return self._updated


    @property
    def public_id(self) -> str:
        "Gives the public ID of the creator."

        return self._public_id


    @property
    def favorited(self) -> int:
        "Tells how many times the creator was favorited."

        return self._favorited


    @property
    def url(self) -> "UrlLike":
        """
        Retrieves the URL of the creator.
        """

        return f"{UrlType.SITE}/{self.service}/user/{self.id}"


    def other_links(self) -> list["Creator"]:
        """
        Searches for other accounts of this creator.
        """

        link_response = get(f"/{self.service}/user/{self.id}/links")
        links = []

        for link_fields in link_response.json():
            creator = Creator.from_profile(link_fields.get("service"),
                                           link_fields.get("id"))
            if creator is not None:
                links.append(creator)

        return links


    def posts(self, query: Optional[str]=None, offset: Optional[int]=None) -> list[Post]:
        """
        Retrieves posts under this creator.
        """

        response = get(f"/{self.service}/user/{self.id}",
                       params=self.query_params(query, offset))
        posts_list = []

        for post_fields in response.json():
            post_fields.update(creator=self)
            posts_list.append(Post.from_dict(**post_fields))

        return posts_list


    def get_post(self, post_id: str) -> Optional[Post]:
        """
        Get a specific post by its ID.
        """

        response = get(f"/{self.service}/user/{self.id}/post/{post_id}")

        if response.status_code == 404:
            return None

        return Post.from_dict(**response.json())
