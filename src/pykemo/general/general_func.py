"""
Module for auxiliar functions.
"""

from asyncio import gather
from typing import TYPE_CHECKING, Iterable, Optional, TypeAlias, Union

from .._aux import (
    FileHashResult,
    add_session_to_message,
    add_session_to_post,
    before_date,
    get_posts_responses_bodies,
    since_date,
)
from ..accounts import AccountRole, Admin, Consumer, Moderator
from ..creators import Creator, CreatorsList
from ..discord import DiscordMessage
from ..exceptions import AlreadyLoggedIn, InvalidLogin, LoginError
from ..files import File
from ..posts import ELEMENTS_PER_PAGE, Post, PostsList
from ..services import ServiceType
from ..sessions import KemoSession

if TYPE_CHECKING:
    from datetime import datetime
    from os import PathLike

    from ..posts import PostID
    from ..services import ServiceLike
    from ..tags import TagLike

AccountType: TypeAlias = Union[Consumer, Moderator, Admin]

MAX_POSTS_LIMIT: int = 1000
"Arbitrary limit for posts to be queried with auxiliar functions."


async def get_creators(kemo_session: KemoSession) -> CreatorsList:
    """
    Gets all the creators.

    .. warning:: There is currently no limitations to this function. It will really try to fetch
                 **ALL the creators on the site**. If you do not explicitly need this, do not use
                 it.

    :param kemo_session: The Kemono Session to use.

    :type kemo_session: :class:`.KemoSession`

    :returns: The list of all creators.
    :rtype: list[:class:`.Creator`]
    """

    response = await kemo_session.get("/creators.txt")
    creators_tasks = []

    async for creator_fields in response.json():
        creators_tasks.append(get_creator(creator_fields.get("service"),
                                          creator_fields.get("id")),
                                          kemo_session)

    return await gather(*creators_tasks)


async def get_posts(query: Optional[str]=None,
                    *,
                    max_posts: int=ELEMENTS_PER_PAGE,
                    before: Optional["datetime"]=None,
                    since: Optional["datetime"]=None,
                    tags: Optional[list["TagLike"]]=None,
                    kemo_session: KemoSession) -> PostsList:
    """
    Gets all posts that coincide with the given parameters.

    :param query: A query string to use in the search.
    :param max_posts: The max number of posts to look through. This is NOT necessarily
                      the number of posts to enter the lists.
    :param before: Include only posts before this date, defaults to ``None``.
    :param since: Include only posts after and including this date, defaults to ``None``.
    :param tags: The tags to filter the search by, defaults to ``None``.
    :param kemo_session: The Kemono Session to use.

    :type query: Optional[:class:`str`]
    :type max_posts: :class:`int`
    :type before: Optional[:class:`datetime.datetime`]
    :type since: Optional[:class:`datetime.datetime`]
    :type tags: list[:type:`.TagLike`], optional
    :type kemo_session: :class:`.KemoSession`

    :return: The list of posts of the query.
    :rtype: list[:class:`.Post`]
    """

    if max_posts is not None and (max_posts <= 0 or max_posts > MAX_POSTS_LIMIT):
        raise ValueError("max_posts must be an integer greater than zero but lower than "
                         f"{MAX_POSTS_LIMIT}, not '{max_posts}'")

    posts_tasks = []

    for post_fields in await get_posts_responses_bodies(
        endpoint="/posts",
        query=query,
        max_posts=max_posts,
        page_stepping=ELEMENTS_PER_PAGE,
        tags=tags,
        post_process=(lambda fields: fields["posts"]),
        kemo_session=kemo_session
    ):
        # -- filter by date --
        published_str = post_fields["published"]
        if ((before is not None and not before_date(published_str, before)) or
            (since is not None and not since_date(published_str, since))):
            continue
        # --------------------

        post_fields.update(creator=await get_creator(post_fields.get("service"),
                                                     post_fields.get("user"),
                                                     kemo_session))
        posts_tasks.append(add_session_to_post(Post.from_dict(**post_fields), kemo_session))

    return await gather(*posts_tasks)


async def get_post(service: "ServiceLike",
                   post_id: "PostID",
                   kemo_session: KemoSession) -> Optional[Post]:
    """
    Tries to fetch a post by its service and ID, automatically searching for its creator.
    
    :param service: The service the post falls under.
    :param post_id: The ID of the specific post.
    :param kemo_session: The Kemono Session to use.
    
    :type service: :type:`.ServiceLike`
    :type post_id: :type:`.PostID`
    :type kemo_session: :class:`.KemoSession`
    
    :return: The loaded post, if it was found. If not, returns ``None``.
    :rtype: Optional[:class:`.Post`]
    """

    res = await kemo_session.get(f"/{service}/post/{post_id}")

    if res.status == 404:
        return None

    creator_id = (await res.json()).get("artist_id")
    creator = await get_creator(service, creator_id, kemo_session)

    return await creator.get_post(post_id)


async def get_creator(service: "ServiceLike",
                      creator_id: str,
                      kemo_session: KemoSession) -> Optional[Creator]:
    """
    Tries to retrieve a creator with the given ID and service.

    :param service: The service of the creator.
    :param creator_id: The ID of the creator.
    :param kemo_session: The Kemono Session to use.

    :type service: :type:`.ServiceLike`
    :type creator_Id: :class:`str`
    :type kemo_session: :class:`.KemoSession`

    :return: The creator instance, if found. Otherwise returns ``None``.
    :rtype: Optional[:class:`.Creator`]
    """

    return await Creator.from_profile(service, creator_id, kemo_session)


async def get_creator_links(service: "ServiceLike", creator_id: str) -> CreatorsList:
    """
    Retrieves a list that is the other accounts of a creator, should it have any with
    other services, for example.

    :param service: The service of the creator.
    :param creator_id: The ID of the creator.

    :type service: :type:`.ServiceLike`
    :type creator_Id: :class:`str`

    :return: A list of the creators associated with this one.
    :rtype: list[:class:`.Creator`]
    """

    links = []
    creator = await get_creator(service, creator_id)

    if creator is not None:
        links.extend(await creator.other_links())

    return links


async def random_post(session: KemoSession) -> Optional[Post]:
    """
    Tries to retrieve a random post from the site.

    :param session: The Kemono Session to use for the request.

    :type session: :class:`.KemoSession`

    :return: If a creator is found, retrieve and create a :class:`.Post` instance, otherwise return ``None``.
    :rtype: Optional[:class:`.Post`]
    """

    post_res = await session.get("/posts/random")

    if post_res.status != 200:
        return None

    post_fields = await post_res.json()
    service = post_fields.get('service')
    creator_id = post_fields.get('artist_id')

    post_exists = await session.get(f"/{service}/user/{creator_id}/post/{post_fields.get('post_id')}")

    if post_exists.status == 404:
        return None

    fields = (await post_exists.json()).get("post")
    fields.update(creator=(await get_creator(service, creator_id, session)))

    return await add_session_to_post(Post.from_dict(**fields), session)


async def get_file_hash(hash: str, kemo_session: KemoSession) -> FileHashResult:
    """
    Search a file by hash. Also tries to retrieve posts where such file is present.

    :param hash: The query hash to search with.
    :param session: The Kemono Session to use.

    :type hash: :class:`str`
    :type session: :class:`.KemoSession`

    :return: The result of the query.
    :rtype: :class:`.FileHashResult`
    """

    response = await kemo_session.get(f"/search_hash/{hash}")

    if response.status == 404:
        return FileHashResult.empty()

    body = await response.json()

    ext = body.get("ext")

    file = File(name=f"{hash}{ext}",
                path=f"/data/{hash[0:2]}/{hash[2:4]}/{hash}{ext}",
                content_type=body.get("mime"))

    posts_tasks = []
    posts_res = body.get("posts", None)
    posts = (posts_res if posts_res is not None else [])
    for post_fields in posts:
        post_fields.update(creator=await get_creator(post_fields.get("service"),
                                                     post_fields.get("user")))
        posts_tasks.append(add_session_to_post(Post.from_dict(**post_fields), kemo_session))

    msgs_tasks = []
    msgs_res = body.get("discord_posts", None)
    msgs = (msgs_res if msgs_res is not None else [])
    for msg_fields in msgs:
        creator = await get_creator(service=ServiceType.DISCORD,
                                    creator_id=msg_fields.get("server"))
        msg_fields.update(parent_channel=await creator.get_channel(msg_fields.get("channel")),
                          content=msg_fields.get("substring", ""))
        msgs_tasks.append(add_session_to_message(DiscordMessage.from_dict(**msg_fields),
                                                 kemo_session))


    return FileHashResult(
        file=file,
        posts=await gather(*posts_tasks),
        disc=await gather(*msgs_tasks)
    )


async def get_api_version(kemo_session: KemoSession) -> str:
    """
    Convenience function to get the last hash of the current API version.

    :param kemo_session: The Kemono Session to use.

    :type kemo_session: :class:`.KemoSession`

    :return: The last commit hash of the API.
    :rtype: :class:`str`
    """

    res = await kemo_session.get("/app_version")
    return await res.text()


def _get__account_type_by_role(role: AccountRole) -> AccountType:
    """
    Gives an account class based on the role passed. If the type is not recognized,
    :class:`.Consumer` will be used.
    
    :param role: The role name.
    
    :type role: :class:`.AccountRole`
    
    :return: Any of the possible account types. `i.e.` a :class:`.Consumer`, :class:`.Moderator`, :class:`.Admin`, etc.
    :rtype: :type:`.AccountType`
    """

    match role:
        case AccountRole.CONSUMER:
            return Consumer

        case AccountRole.MODERATOR:
            return Moderator

        case AccountRole.ADMINISTRATOR:
            return Admin

        case _:
            return Consumer


async def login(
        user: str,
        password: str,
    ) -> AccountType:
    """
    An alias for logging an automatically deciding which account rank is returned.

    :param user: The username to try to login with.
    :param password: The password to try to login with.

    :type user: :class:`str`
    :type password: :class:`str`

    :raises InvalidLogin: The login had incorrect data.
    :raises AlreadyLoggedIn: The user is already logged in.
    :raises LoginError: Another error ocurred.

    :return: Any of the possible account types, already logged-in.
    :rtype: :type:`.AccountType`
    """

    session = KemoSession()
    login_res = await session.post("/authentication/login", json=dict(username=user, password=password))
    res_json = await login_res.json()

    # invalid due to user errors
    if login_res.status == 400:
        session.close()
        raise InvalidLogin(res_json.get("error", "The login is invalid due to user errors"))

    # already logged in
    if login_res.status == 409:
        session.close()
        raise AlreadyLoggedIn(res_json.get("error", "The user is already logged in"))

    # another unknown error
    if login_res.status != 200:
        session.close()
        raise LoginError(res_json.get("error", "An unexpected error ocurred during the login"))

    res_json.update(session=session)
    acc_type = _get__account_type_by_role(res_json.get("role", None))
    return await acc_type.from_dict(**res_json)


async def register(
        user: str,
        password: str
    ) -> Consumer:
    """
    An alias for registering an account. Is is assumed each new account is born as a consumer.
    """

    return await Consumer.register(user, password)


async def save_posts(path: "PathLike",
                     posts: Iterable[Post],
                     *,
                     force: bool=True,
                     verbose: bool=True) -> bool:
    """
    Tries to save many posts in bulk.

    .. warning:: The connection may close in between if it takes too long, but
    it reconnects automatically.

    :param path: The path to be used to save all the contents of the posts.
    :param posts: The posts to be saved.
    :param force: Wether to overwrite existing files, defaults to ``True``
    :param verbose: Wether to track progress, defaults to ``True``

    :type path: :class:`.PathLike`
    :type posts: Iterable[:class:`.Post`]
    :type force: :class:`bool`, optional
    :type verbose: :class:`bool`, optional
    
    :return: ``True`` if `all` downloads were sucessful, or ``False`` if not.
    :rtype: :class:`bool`
    """

    download_tasks = []

    for (i, post) in enumerate(posts):
        download_tasks.append(post.save(path, force=force, verbose=verbose,
                                        pos=i, verbose_children=False))

    return all(await gather(*download_tasks))
