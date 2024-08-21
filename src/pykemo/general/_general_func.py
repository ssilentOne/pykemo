"""
Module for auxilair functions.
"""

from typing import TYPE_CHECKING, Optional

from .._aux import FileHashResult, get_posts_responses
from ..core import get
from ..creators import Creator, CreatorsList
from ..discord import DiscordMessage
from ..files import File
from ..posts import ELEMENTS_PER_PAGE, Post, PostsList
from ..services import ServiceType

if TYPE_CHECKING:
    from datetime import datetime

    from ..services import ServiceLike

MAX_POSTS_LIMIT: int = 1000
"Arbitrary limit for posts to be queried with auxiliar functions."


def get_creators() -> CreatorsList:
    """
    Gets ALL the creators.
    """

    response = get("/creators.txt")
    creators = []

    for creator_fields in response.json():
        creators.append(get_creator(creator_fields.get("service"),
                                    creator_fields.get("id")))

    return creators


def get_posts(query: Optional[str]=None,
              max_posts: Optional[int]=None,
              before: Optional["datetime"]=None,
              since: Optional["datetime"]=None) -> PostsList:
    """
    Gets all posts that coincide with the given parameters.

    query: A query string to use in the search.
    max_posts: The max number of posts to look through. This is NOT necessarily the number of
               posts to enter the lists.
    before: Include only posts before this date.
    since: Include only posts after and including this date.
    """

    if max_posts is not None and (max_posts <= 0 or max_posts > MAX_POSTS_LIMIT):
        raise ValueError("max_posts must be an integer greater than zero but lower than "
                         f"{MAX_POSTS_LIMIT}, not '{max_posts}'")

    if max_posts is None:
        max_posts = ELEMENTS_PER_PAGE

    response_bodies = get_posts_responses(endpoint="/posts",
                                          query=query,
                                          max_posts=max_posts)
    posts = []

    for post_fields in response_bodies:
        published_str = post_fields["published"]
        if ((before is not None and not Post.before_static(published_str, before)) or
            (since is not None and not Post.since_static(published_str, since))):
            continue

        post_fields.update(creator=get_creator(post_fields.get("service"),
                                               post_fields.get("user")))
        posts.append(Post.from_dict(**post_fields))

    return posts


def get_creator(service: "ServiceLike", creator_id: str) -> Optional[Creator]:
    """
    Tries to retrieve a creator with the given ID and service.
    Returns `None` if it does not find it.
    """

    return Creator.from_profile(service, creator_id)


def get_creator_links(service: "ServiceLike", creator_id: str) -> CreatorsList:
    """
    Retrieves a list that is the other accounts of a creator, should it have any in
    other services, for example.
    """

    return get_creator(service, creator_id).other_links()


def get_file_hash(hash: str) -> FileHashResult:
    """
    Search a file by hash. Also tries to retrieve posts where such file is present.
    """

    response = get(f"/search_hash/{hash}")

    if response.status_code == 404:
        return FileHashResult.empty()

    body = response.json()

    ext = body.get("ext")

    file = File(name=f"{hash}{ext}",
                path=f"/data/{hash[0:2]}/{hash[2:4]}/{hash}{ext}",
                content_type=body.get("mime"))

    posts_list = []
    posts_res = body.get("posts", None)
    posts = (posts_res if posts_res is not None else [])
    for post_fields in posts:
        post_fields.update(creator=get_creator(post_fields.get("service"),
                                               post_fields.get("user")))
        posts_list.append(Post.from_dict(**post_fields))

    msgs_list = []
    msgs_res = body.get("discord_posts", None)
    msgs = (msgs_res if msgs_res is not None else [])
    for msg_fields in msgs:
        creator = get_creator(service=ServiceType.DISCORD,
                              creator_id=msg_fields.get("server"))
        msg_fields.update(parent_channel=creator.get_channel(msg_fields.get("channel")),
                          content=msg_fields.get("substring", ""))
        msgs_list.append(DiscordMessage.from_dict(**msg_fields))


    return FileHashResult(file=file, posts=posts_list, disc=msgs_list)


def get_app_version() -> str:
    """
    Retrieves the last commit hash of the API.
    """

    return get("/app_version").text
