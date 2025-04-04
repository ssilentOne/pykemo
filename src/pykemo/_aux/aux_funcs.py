"""
Auxiliar functions module.
"""

from asyncio import gather
from collections.abc import Coroutine
from datetime import datetime
from typing import TYPE_CHECKING, Any, Callable, Optional, TypeAlias, Union

if TYPE_CHECKING:
    from typing import Iterable

    from aiohttp import ClientResponse

    from ..core import UrlLike
    from ..discord import DiscordMessage
    from ..files import FileDict
    from ..posts import Post
    from ..sessions import KemoSession
    from ..tags import Tag, TagLike

DateOrFmt: TypeAlias = Union[str, datetime]
ParamsTuples: TypeAlias = list[tuple[str, Union[str, int]]]
JsonBody: TypeAlias = dict # Could have anything inside, really

DEFAULT_DATE_FMT: str = r"%Y-%m-%dT%H:%M:%S"
"The default date formatting to use."

MILI_DATE_FMT: str = rf"{DEFAULT_DATE_FMT}.%f"
"The default date, added miliseconds."

DEFAULT_PAGE_SIZE: int = 50
"The default page size to retrieve posts responses."


def sanitize_data_url(file_dict: "FileDict") -> "FileDict":
    """
    Appends the relative path of the file path with ``'/data'``.
    Returns the dict itself for convenience purposes.

    :param file_dict: A dict of the type ``dict[Literal['name', 'path'], str]``.

    :type file_dict: :type:`.FileDict`

    :return: The same dict, but with ``'/data'`` prefixed to the paths.
    :rtype: :type:`.FileDict`
    """

    file_path = file_dict.get("path", None)
    if file_path is not None:
        file_dict["path"] = f"/data{file_path}"

    return file_dict


def process_date(date: DateOrFmt, fmt: Optional[str]=None) -> datetime:
    """
    Process the date if it's a string, or use it as-is if it is already a datetime object.

    :param date: The date string in question.
    :param fmt: The format to use to process de date.

    :type fmt: Optional[:class:`str`]

    :return: A processed :class:`datetime.datetime` object.
    :rtype: :class:`datetime.datetime`
    """

    if isinstance(date, str):
        return datetime.strptime(date, (fmt if fmt is not None else DEFAULT_DATE_FMT))

    return date


def before_date(date1: DateOrFmt,
                date2: DateOrFmt,
                *,
                fmt1: Optional[str]=None,
                fmt2: Optional[str]=None) -> bool:
    """
    Compares if the dates (in string form) with `date1` < `date2`.

    :param date1: The first date.
    :param date2: The second date.
    :param fmt1: The format used to process `date1`.
    :param fmt2: The format used to process `date2`.

    :type date1: :class:`datetime.datetime`
    :type date2: :class:`datetime.datetime`
    :type fmt1: Optional[:class:`str`]
    :type fmt2: Optional[:class:`str`]

    :return: The result of ``date1 < date2``
    :rtype: :class:`bool`
    """

    return process_date(date1, fmt1) < process_date(date2, fmt2)


def since_date(date1: DateOrFmt,
               date2: DateOrFmt,
               *,
               fmt1: Optional[str]=None,
               fmt2: Optional[str]=None) -> bool:
    """
    Compares if the dates (in string form) with `date1` >= `date2`.

    :param date1: The first date.
    :param date2: The second date.
    :param fmt1: The format used to process `date1`.
    :param fmt2: The format used to process `date2`.

    :type date1: :class:`datetime.datetime`
    :type date2: :class:`datetime.datetime`
    :type fmt1: Optional[:class:`str`]
    :type fmt2: Optional[:class:`str`]

    :return: The result of ``date1 >= date2``
    :rtype: :class:`bool`
    """

    return process_date(date1, fmt1) >= process_date(date2, fmt2)


def sanitize_str(src: str,
                 forbidden: "Iterable",
                 target: str) -> str:
    """
    Replaces all characters in 'src' with 'target' if said char is in 'forbidden'.

    :param src: The source string to modify.
    :param forbidden: The characters to look for and potentially replace.
    :param target: The character to replace bad chars with.

    :type src: :class:`str`
    :type forbidden: :class:`Iterable`
    :type target: :class:`str`

    :return: A string with all bad characters replaced.
    :rtype: :class:`str`
    """

    cpy = src[:]
    for bad_char in forbidden:
        cpy = cpy.replace(bad_char, target)

    return cpy


async def add_session_to_post(
    post_task: Coroutine[Any, Any, "Post"],
    session: "KemoSession"
) -> "Post":
    """
    Resolves the task, and _then_ assigns a session to a resolved post.
    
    :param post_task: The task to be awaited.
    :param session: The session to assign.
    
    :type post_task: Coroutine[Any, Any, :class:`.Post`]
    :type session: :class:`.KemoSession`
    
    :return: The post, as it would be returned by the task, but with the session assigned.
    :rtype: :class:`.Post`
    """

    return (await post_task).set_underlying_session(session)


async def add_session_to_message(
    msg_task: Coroutine[Any, Any, "DiscordMessage"],
    session: "KemoSession"
) -> "DiscordMessage":
    """
    Resolves the task, and _then_ assigns a session to a resolved discord message.
    
    :param post_task: The task to be awaited.
    :param session: The session to assign.
    
    :type post_task: Coroutine[Any, Any, :class:`.DiscordMessage`]
    :type session: :class:`.KemoSession`
    
    :return: The message, as it would be returned by the task, but with the session assigned.
    :rtype: :class:`.DiscordMessage`
    """

    return (await msg_task).set_underlying_session(session)


async def add_session_to_tag(
        tag_task: Coroutine[Any, Any, "Tag"],
        session: "KemoSession"
) -> "Tag":
    """
    Resolves the task, and _then_ assigns a session to a resolved tag.
    
    :param post_task: The task to be awaited.
    :param session: The session to assign.
    
    :type post_task: Coroutine[Any, Any, :class:`.Tag`]
    :type session: :class:`.KemoSession`
    
    :return: The tag, as it would be returned by the task, but with the session assigned.
    :rtype: :class:`.Tag`
    """

    return (await tag_task).set_underlying_session(session)


def query_params(query: Optional[str]=None,
                 offset: Optional[int]=None,
                 stepping: int=DEFAULT_PAGE_SIZE,
                 tags: Optional[list["TagLike"]]=None) -> ParamsTuples:
    """
    .. warning:: `(for internal purposes)`
    Formats a parameters list to send with a response in messages queries.
    Such list has tuples of strings instead of a dictionary, to allow for duplicated keys.

    :param query: The search query string of the dict.
    :param offset: The search offset int of the dict.
    :param stepping: The stepping to which the search will be made.
    :param tags: The tags to filter the search by, defaults to ``None``.

    :type query: Optional[:class:`str`]
    :type offset: Optional[:class:`int`]
    :type stepping: :class:`int`
    :type tags: list[:type:`.TagLike`], optional

    :raises ValueError: If ``offset`` is not a multiple of ``stepping``.

    :return: A tuple already poblated with the parameters.
    :rtype: :type:`.ParamsFmtDict`
    """

    params = []

    if query is not None:
        params.append(("q", query))

    if offset is not None:
        if offset % stepping != 0:
            raise ValueError(f"Value for offset {offset} not valid."
                                f" Must be a multiple of {stepping}.")
        params.append(("o", offset))

    if tags is not None:
        for tag in tags:
            params.append(("tag", tag))

    return params


async def get_posts_responses_bodies(
        *,
        endpoint: "UrlLike",
        query: Optional[str]=None,
        max_posts: Optional[int]=None,
        page_stepping: int=DEFAULT_PAGE_SIZE,
        tags: Optional[list["TagLike"]]=None,
        post_process: Optional[Callable[[JsonBody], JsonBody]]=None,
        kemo_session: "KemoSession") -> list[JsonBody]:
    """
    Gets the responses of posts by page. The, it unpacks their bodies into a JSON-like dictionary.

    :param endpoint: The endpoint that the request will map to.
    :param query: A search query string to filter the results.
    :param max_posts: The max posts to fit into the final list. If not set, the minimum value possible will be used.
    :param page_stepping: The stepping of the paging.
    :param tags: The tags to filter the search by, defaults to ``None``.
    :param post_process: A small function to be applied after unpacking each response body.
    :param kemo_session: The session to make the requests with.

    :type endpoint: :type:`.UrlLike`
    :type query: Optional[:class:`str`]
    :type max_posts: Optional[:class:`int`]
    :type page_stepping: :class:`int`
    :type tags: list[:type:`.TagLike`], optional
    :type post_process: Optional[Callable[[:type:`.JsonBody`], :type:`.JsonBody`]]
    :type kemosession: :class:`.KemoSession`

    :return: A list of response bodies, to be further processed.
    :rtype: list[:type:`.JsonBody`]
    """

    async def unpack_json(task: Coroutine[Any, Any, "ClientResponse"]) -> JsonBody:
        res = await task

        if res is not None and res.status != 429:
            raw_body = await res.json()
            return (raw_body if post_process is None else post_process(raw_body))

        return {}

    tasks = []

    if max_posts is None:
        max_posts = page_stepping

    n_pages = (max_posts // page_stepping)
    if max_posts % page_stepping != 0:
        # if not exact amount, use one more page
        n_pages += 1
    for page in range(n_pages):
        page_coroutine = kemo_session.get(
            endpoint,
            params=query_params(query,
                                page * page_stepping,
                                page_stepping,
                                tags=tags)
        )

        tasks.append(unpack_json(page_coroutine))

    bodies = []

    # asyncio.gather() makes sure the order of the pages in the list is the same, even though
    # you have to wait for all of them to finish first
    for body in await gather(*tasks):
        # extend() is used instead of append() because each response is a list of bodies itself
        if body:
            bodies.extend(body)

    return bodies


def parse_tags(tags_str: str) -> list[str]:
    """
    Tries to separate tag names from a string of the style \"{tag1,tag2,tag3,...}\"
    
    :param tags_str: The tags unparsed string.
    
    :type tags_str: :class:`str`
    
    :return: A list of the parsed tags. Could be empty.
    :rtype: list[:class:`str`]
    """

    return tags_str.lstrip("{").rstrip("}").split(",")
