"""
Tags module.
"""

from asyncio import gather
from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Iterable, Literal, Optional, Self, TypeAlias, Union

from .._aux import add_session_to_tag

if TYPE_CHECKING:
    from ..sessions import KemoSession

TagName: TypeAlias = str
TagLike: TypeAlias = Union["Tag", TagName]
_RawTagsDict: TypeAlias = dict[Literal["tag", "post_value"], Union[str, int]]
TagsDict: TypeAlias = dict[str, int]
TagsResult: TypeAlias = Union[list["Tag"], TagsDict]


@dataclass
class Tag:
    """
    A tag is a simple categorization of content, given a name.

    :param value: The value of the tag.
    :param post_count: How many posts have this tag.

    :type value: :class:`str`
    :type post_count: :class:`int`
    """

    value: TagName
    post_count: int

    __kemo_session: Optional["KemoSession"] = field(default=None, init=False, repr=False)


    @classmethod
    async def from_dict(cls, **fields) -> Self:
        """
        Initializes a Tag instance from a response fields.

        :return: A tag instance.
        :rtype: :class:`.Tag`
        """

        return cls(
            value=fields.get("tag"),
            post_count=fields.get("post_count")
        )


    @classmethod
    async def all(cls, ks: "KemoSession", *, as_dict: bool=False) -> TagsResult:
        """
        Gets all the tags found on the site. `Might take a while`.

        :param session: The session instance.
        :param as_dict: Wether to return a dictionary with the tags names as keys and their post
                        counts as values, defaults to ``False``.
        
        :type session: :class:`.KemoSession`
        :type as_dict: :class:`bool`, optional

        :return: A list with all tags that were found, or a dictionary of their values; according to ``as_dict``.
        :rtype: :type:`.TagsResult`
        """

        search_res = await ks.get("/posts/tags")

        if search_res.status != 200:
            return ({} if as_dict else [])

        return await cls.process_tag_response((await search_res.json()).get("tags"), as_dict=as_dict)


    @classmethod
    async def with_name(cls,
                        name: str,
                        ks: "KemoSession",
                        *,
                        cache: Optional[TagsDict]=None) -> Optional[Self]:
        """
        Tries to retrieve a tag with a given name. It may not exist.

        :param name: The name to search for.
        :param session: The session instance.
        :param cache: An optional dict to consult the tags from.

        :type name: :class:`str`
        :type session: :class:`.KemoSession`
        :type cache: Optional[:type:`.TagsDict`]

        :return: The tag in question, or ``None`` if it was not found.
        :rtype: Optional[:class:`.Tag`]
        """

        all_tags = (await cls.all(ks, as_dict=True) if cache is None else cache)

        if name not in all_tags:
            return None

        tag_fields = dict(
            tag=name,
            post_count=all_tags[name]
        )
        return await add_session_to_tag(cls.from_dict(**tag_fields), ks)


    @classmethod
    async def from_names(cls,
                        names: Iterable[str],
                        ks: "KemoSession",
                        *,
                        cache: Optional[TagsDict]=None) -> list[Self]:
        """
        Tries to retrieve tags based on their names.

        :param names: The names to search for.
        :param session: The session instance.
        :param cache: An optional dict to consult the tags from.

        :type names: Iterable[:class:`str`]
        :type session: :class:`.KemoSession`
        :type cache: Optional[:type:`.TagsDict`]

        :return: The tags in question.
        :rtype: Optional[:class:`.Tag`]
        """

        all_tags = (await cls.all(ks, as_dict=True) if cache is None else cache)
        tags_tasks = []

        for tag_name in names:
            tags_tasks.append(cls.with_name(tag_name, ks, cache=all_tags))

        return await gather(*tags_tasks)


    @staticmethod
    def _flatten_tag_dict(raw_tags: list[_RawTagsDict]) -> TagsDict:
        """
        Tries to flatten the info about the tags into a dict with their names as keys, and
        their post counts as values.
        
        :param raw_tags: The unprocessed tags, as they come in the response.
        
        :type raw_tags: :class:`list[_RawTagsDict]`, optional
        
        :return: The tags' dict already processed and falttened.
        :rtype: :type:`.TagsDict`
        """

        tag_dict = {}

        for tag_fields in raw_tags:
            tag_dict[tag_fields.get("tag")] = tag_fields.get("post_count")

        return tag_dict


    @classmethod
    async def process_tag_response(cls,
                                   raw_tag_response: _RawTagsDict,
                                   *,
                                   as_dict: bool=False) -> TagsResult:
        """
        Tries to process the tags either into a list or a dictionary.
        
        :param raw_tag_response: The raw tags, as they come in the response.
        :param as_dict: Wether to return a dictionary with the tags names as keys and their post
                        counts as values, defaults to ``False``.

        :type raw_tag_response: :type:`_RawTagsDict`
        :type as_dict: :class:`bool`, optional
        
        :return: A list of tags, or a dictionary of names/post counts.
        :rtype: :type:`.TagsResult`
        """

        if as_dict:
            return cls._flatten_tag_dict(raw_tag_response)

        tag_tasks = []

        for tag_fields in raw_tag_response:
            tag_tasks.append(add_session_to_tag(cls.from_dict(**tag_fields)))

        return await gather(*tag_tasks)


    def set_underlying_session(self, ks: "KemoSession") -> Self:
        """
        Quietly sets the session which the tag uses for its requests.
        
        :param session: The session instance.
        
        :type session: :class:`.KemoSession`

        :return: The same instance of the tag, for convenience.
        :rtype: :class:`.Tag`
        """

        self.__kemo_session = ks
        return self

