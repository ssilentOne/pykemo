"""
Posts module.
"""

from asyncio import gather
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import TYPE_CHECKING, Optional, Self, TypeAlias, Union

from tqdm.asyncio import tqdm_asyncio

from .._aux import (
    DEFAULT_DATE_FMT,
    MILI_DATE_FMT,
    add_session_to_post,
    sanitize_data_url,
    sanitize_str,
)
from ..comments import Comment
from ..core import UrlType
from ..files import BAR_WIDTH, File, FilesList
from ..services import ServiceType
from .post_revisions import PostRevision

if TYPE_CHECKING:
    from os import PathLike

    from ..core import UrlLike
    from ..creators import Creator
    from ..services import ServiceLike
    from ..sessions import KemoSession

PostID: TypeAlias = str
PostsList: TypeAlias = list["Post"]
CommentsList: TypeAlias = list[Comment]
PostRevsList: TypeAlias = list[PostRevision]

ELEMENTS_PER_PAGE: int = 50
"""
This is how the API ortganizes the posts and other things.
Each 'page' has fifty (50) elements at most.
"""


@dataclass(kw_only=True)
class Post:
    """
    Post with content.

    :param id: The ID of the post.
    :param creator_id: The creator's ID that owns the post content (not the user that uploaded it).
    :param service: The services that provides the content.
    :param title: The title of the post.
    :param content: The content string of the post.
    :param substring: The sub-string for the post description.
    :param embed: A dictionary denoting the embed.
    :param shared_file: Wether the post has a shared file.
    :param added: When was the post added.
    :param published: When was the post published.
    :param edited: When was the post last edited.
    :param file: The file that the posts uses when previewed.
    :param attachments: All the files under this post.
    :param creator: The creator of this post.
    :param is_revision: Flag to see if this post is a revision of another.
    :param prev_id: If available, the ID of the \"previous\" post.
    :param next_id: If available, the ID of the \"next\" post.

    :type id: :type:`.PostID`
    :type creator_id: :class:`str`
    :type service: :type:`.ServiceLike`
    :type title: :class:`str`
    :type content: :class:`str`
    :type substring: :class:`str`
    :type embed: :class:`dict`
    :type shared_file: :class:`bool`
    :type added: Optional[:class:`datetime.datetime`]
    :type published: :class:`datetime.datetime`
    :type edited: Optional[:class:`datetime.datetime`]
    :type file: Optional[:class:`.File`]
    :type attachments: list[:class:`.File`]
    :type creator: :class:`.Creator`
    :type is_revision: :class:`bool`
    :type prev_id: Optional[:type:`.PostID`]
    :type next_id: Optional[:type:`.PostID`]
    """

    id: PostID
    creator_id: str
    service: "ServiceLike"
    title: str
    content: str = field(repr=False)
    substring: str = field(repr=False)
    embed: dict = field(repr=False)
    shared_file: bool = field(repr=False)
    added: Optional[datetime] = field(default=None, repr=False)
    published: datetime = field(repr=False)
    edited: Optional[datetime] = field(default=None, repr=False)
    file: Optional[File] = field(default=None, repr=False)
    attachments: FilesList = field(default_factory=list, repr=False)
    creator: "Creator" = field(repr=False)
    is_revision: bool = field(default=False, repr=False)
    prev_id: Optional[PostID] = field(default=None, repr=False)
    next_id: Optional[PostID] = field(default=None, repr=False)

    # unloaded fields
    _comments: CommentsList = field(default_factory=list, init=False, repr=False)
    __comm_loaded: bool = field(default=False, init=False, repr=False)

    _flagged: bool = field(default=False, init=False, repr=False)
    __flag_loaded: bool = field(default=False, init=False, repr=False)

    _revisions: PostRevsList = field(default_factory=list, init=False, repr=False)
    __revs_loaded: bool = field(default=False, init=False, repr=False)

    __kemo_session: Optional["KemoSession"] = field(default=None, init=False, repr=False)


    @classmethod
    async def from_dict(cls, **fields) -> Self:
        """
        Initializes a Post instance from a response fields.

        :return: A post instance.
        :rtype: :class:`.Post`
        """

        added_field = fields.get("added", None)
        added = (datetime.strptime(added_field, MILI_DATE_FMT)
                 if added_field is not None
                 else None)
        
        edited_field = fields.get("edited", None)
        edited = (datetime.strptime(edited_field, DEFAULT_DATE_FMT)
                 if edited_field is not None
                 else None)

        file_dict = fields.get("file")
        attachments = fields.get("attachments")

        return cls(
            id=fields.get("id"),
            creator_id=fields.get("user"),
            service=ServiceType(fields.get("service")),
            title=fields.get("title").strip(),
            content=fields.get("content", ""),
            substring=fields.get("substring", ""),
            embed=fields.get("embed", {}),
            shared_file=fields.get("shared_file", False),
            added=added,
            published=datetime.strptime(fields.get("published"), DEFAULT_DATE_FMT),
            edited=edited,
            file=(await File.from_dict(**sanitize_data_url(file_dict)) if file_dict else None),
            attachments=await gather(*[File.from_dict(**sanitize_data_url(attachment_fields))
                         for attachment_fields in attachments]),
            creator=fields.get("creator", None),
            is_revision=fields.get("is_revision", False),
            prev_id=fields.get("prev", None),
            next_id=fields.get("next", None)
        )


    async def comments(self) -> CommentsList:
        """
        :return: The comments of the post.
        :rtype: list[:class:`.Comment`]
        """

        if not self.__comm_loaded:
            self.__comm_loaded = True
            self._comments = await self.fetch_comments()

        return self._comments

    async def flagged(self) -> bool:
        """
        :return: Wether the post is flagged for reimport.
        :rtype: :class:`bool`
        """

        if not self.__flag_loaded and not self.is_revision:
            self.__flag_loaded = True
            self._flagged = await self._fetch_flagged()

        return self._flagged


    async def revisions(self) -> PostRevsList:
        """
        :return: All the revisions of this post.
        :rtype: list[:class:`.PostRevision`]
        """

        if not self.__revs_loaded and not self.is_revision:
            self.__revs_loaded = True
            self._revisions = await self._fetch_revisions()

        return self._revisions


    async def prev_post(self) -> Optional[Self]:
        """
        Tries to load the previous post by its ID.

        :return: The post, already loaded; or ``None`` if it wasn't found.
        :rtype: Optional[:class:`.Post`]
        """

        return await self._fetch_other_post(self.prev_id)


    async def next_post(self) -> Optional[Self]:
        """
        Tries to load the next post by its ID.

        :return: The post, already loaded; or ``None`` if it wasn't found.
        :rtype: Optional[:class:`.Post`]
        """

        return await self._fetch_other_post(self.next_id)


    @property
    def url(self) -> "UrlLike":
        """
        :return: The full URL of the post.
        :rtype: :type:`.UrlLike`
        """

        return f"{UrlType.SITE}/{self.service}/user/{self.creator_id}/post/{self.id}"


    @property
    def _all_files(self) -> FilesList:
        """
        .. warning:: `(for internal purposes)`

        :return: Both the preview file and the attachments, if any.
        :rtype: list[:class:`.File`]
        """

        return ([self.file] if self.file is not None else []) + self.attachments


    def set_underlying_session(self, ks: "KemoSession") -> Self:
        """
        Quietly sets the session which the post uses for its requests.
        
        :param session: The session instance.
        
        :type session: :class:`.KemoSession`

        :return: The same instance of the post, for convenience.
        :rtype: :class:`.Post`
        """

        self.__kemo_session = ks
        for file in self._all_files:
            file.with_session(self.__kemo_session)
        return self


    def before(self, date: datetime) -> bool:
        """
        Verifies if the post was published before a certain date.

        :return: The result of ``Post.published < date``
        :rtype: :class:`bool`
        """

        return self.published < date


    def since(self, date: datetime) -> bool:
        """
        Verifies if the post was published since a certain date.

        :return: The result of ``Post.published >= date``
        :rtype: :class:`bool`
        """

        return self.published >= date


    def sanitized_title(self) -> "PathLike":
        """
        Converts the title of the post into one apt for a system filename.

        :return: A new path, already sanitized.
        :rtype: :class:`PathLike`
        """

        san = sanitize_str(self.title, "\\/:*?\"<>|", "")
        # It can't end on '.'
        return san.rstrip(".")


    async def save(self,
                   path: Union["PathLike", Path, None]=None,
                   *,
                   force: bool=True,
                   verbose: bool=True,
                   pos: int=0,
                   verbose_children: Optional[bool]=None) -> bool:
        """
        Tries to save all the files in the post. Even if one file fails, it still tries to download the rest.

        :param path: The optional path where to store all the files. If it ends with ``'/*'``, it
                     will use its default name inside such folder.
        :param force: Wether to overwrite existing files, defaults to ``True``
        :param verbose: Wether to track progress, defaults to ``True``
        :param pos: The position order of the progress bar, defaults to 0
        :param verbose_children: Wether to track progress for files, defaults to value of ``verbose``

        :type path: :class:`PathLike` | :class:`Path` | ``None``
        :type force: :class:`bool`, optional
        :type verbose: :class:`bool`, optional
        :type pos: :class:`int`, optional
        :type verbose_children: :class:`bool`, optional

        :return: ``True`` if the download of `all` files was successful, or ``False`` if not.
        :rtype: :class:`bool`
        """

        files = self._all_files
        verb_children = (verbose_children if verbose_children is not None else verbose)
        if verbose and not files:
            # a normal print() will overlap the progress bars
            tqdm_asyncio.write(f"Post '{self.title}' doesn't have attachments to download. Ignoring...")
            return True

        san_title = self.sanitized_title()

        if path is None:
            path = Path(san_title)
        elif isinstance(path, str) and path.endswith("/*"):
            path = Path(path[:-2]) / san_title
        elif not isinstance(path, Path):
            path = Path(path)

        path.mkdir(parents=True, exist_ok=True)

        results = await tqdm_asyncio.gather(*(file.save(path, force=force,
                                                        verbose=verb_children, show_order=pos+i+1)
                                             for (i, file) in enumerate(files)),
                                            miniters=1,
                                            desc=f"Post '{self.title}'",
                                            ncols=BAR_WIDTH,
                                            dynamic_ncols=True,
                                            unit="file",
                                            leave=True,
                                            position=pos,
                                            colour="blue")
        return all(results)


    async def fetch_comments(self) -> CommentsList:
        """
        Fetches the comments of the post.
    
        .. warning:: This is designed for internal purposes, as it is recommended to use the :meth:`.comments()` property instead. However, it can also be used as-is to prevent using a potentially outdated field.

        :return: A list of the comments of this post. Might be empty if there is n osession available.
        :rtype: list[:class:`.Comment`]
        """

        if self.__kemo_session is None:
            return []

        response = await self.__kemo_session.get(f"/{self.service}/user/{self.creator_id}/post/{self.id}/comments")
        comments_tasks = []

        async for comment_fields in response.json():
            comment_fields.update(creator=self.creator, post=self)
            comments_tasks.append(Comment.from_dict(**comment_fields))

        return await gather(*comments_tasks)


    async def _fetch_flagged(self) -> bool:
        """
        .. warning:: `(for internal purposes)`
        Checks with a request if a post is flagged for reimport.
        According to the docs, it should have status code of 200 if it is flagged, and
        404 if it's not.

        :return: Wether or not the post is flagged for reimport. If there is not a session assigned, it will return ``False``.
        :rtype: :class:`bool`
        """

        if self.__kemo_session is None:
            return False

        response = await self.__kemo_session.get(f"/{self.service}/user/{self.creator_id}/post/{self.id}/flag")
        return response.status == 200


    async def _fetch_revisions(self) -> PostRevsList:
        """
        .. warning:: `(for internal purposes)`
        Fetches a request all the revisions of the post.

        :return: All the revisions of this post, if any. If there is no session assigned, an empty list will be returned.
        :rtype: list[:class:`.PostRevision`]
        """

        if self.__kemo_session is None:
            return []

        response = await self.__kemo_session.get(f"/{self.service}/user/{self.creator_id}/post/{self.id}/revisions")
        revisions_tasks = []

        async def revision_from_post(fields: dict) -> PostRevision:
            fields.update(creator=self.creator, is_revision=True)
            subpost = await add_session_to_post(__class__.from_dict(**fields), self.__kemo_session)

            fields.update(post=subpost)
            return await PostRevision.from_dict(**fields)

        async for revs_fields in response.json():
            revisions_tasks.append(revision_from_post(revs_fields))

        return await gather(*revisions_tasks)


    async def _fetch_other_post(self, other_id: Optional[PostID]=None) -> Optional[Self]:
        """
        Tries to fetch another post of the same creator by ID.

        :param other_id: The given ID of the desired post, defaults to ``None``.

        :type other_id: :type:`.PostID`, optional

        :return: The post, already loaded; or ``None`` if it wasn't found.
        :rtype: Optional[:class:`.Post`]
        """

        if other_id is None:
            return None

        res = await self.__kemo_session.get(f"/{self.service}/user/{self.creator_id}/post/{other_id}")

        if res.status == 404:
            return None

        fields = (await res.json()).get("post")
        fields.update(creator=self.creator)

        return await add_session_to_post(Post.from_dict(**fields),
                                         self.__kemo_session)
