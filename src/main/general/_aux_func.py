"""
Module for auxilair functions.
"""

from typing import Optional, TYPE_CHECKING

from ..core import get
from ..creators import Creator
from ..posts import Post

if TYPE_CHECKING:
    from ..services import ServiceLike


def get_creators() -> list[Creator]:
    """
    Gets all creators.
    """

    response = get("/creators.txt")
    creators = []

    for creator_fields in response.json():
        creators.append(get_creator(creator_fields.get("service"),
                                    creator_fields.get("id")))

    return creators


def get_posts(query: Optional[str]=None, offset: Optional[int]=None) -> list[Post]:
    """
    Gets all posts that coincide with the given parameters.

    query: A query string to use in the search.

    offset: The result offset. Must be a multiple of 50.
    """

    response = get("/posts", params=Creator.query_params(query, offset))
    posts = []

    for post_fields in response.json():
        print(post_fields)
        post_fields.update(creator=Creator.from_profile(post_fields.get("service"),
                                                        post_fields.get("user")))
        posts.append(Post.from_dict(**post_fields))

    return posts


def get_creator(service: "ServiceLike", creator_id: str) -> Optional[Creator]:
    """
    Tries to retrieve a creator with the given ID and service.
    Returns `None` if it does not find it.
    """

    return Creator.from_profile(service, creator_id)


def get_creator_links(service: "ServiceLike", creator_id: str) -> list[Creator]:
    """
    Retrieves a list that is the other accounts of a creator, should it have any in
    other services, for example.
    """

    return get_creator(service, creator_id).other_links()


def get_app_version() -> str:
    """
    Retrieves the last commit hash of the API.
    """

    return get("/app_version").text
