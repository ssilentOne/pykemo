"""
Posts module.
"""

from asyncio import run as asyncio_run
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import TYPE_CHECKING, Optional, TypeAlias, Union

from tqdm.asyncio import tqdm_asyncio

from .._aux import DEFAULT_DATE_FMT, MILI_DATE_FMT, sanitize_data_url, sanitize_str
from ..comments import Comment
from ..core import UrlType, get
from ..files import BAR_WIDTH, File, FilesList
from ..services import ServiceType
from .post_revisions import PostRevision

if TYPE_CHECKING:
    from os import PathLike

    from ..core import UrlLike
    from ..creators import Creator
    from ..services import ServiceLike
    from ..sessions import KemoSession

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

    :type id: :class:`str`
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
    """

    id: str
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

    # unloaded fields
    _comments: CommentsList = field(default_factory=list, init=False, repr=False)
    __comm_loaded: bool = field(default=False, init=False, repr=False)

    _flagged: bool = field(default=False, init=False, repr=False)
    __flag_loaded: bool = field(default=False, init=False, repr=False)

    _revisions: PostRevsList = field(default_factory=list, init=False, repr=False)
    __revs_loaded: bool = field(default=False, init=False, repr=False)

    __kemo_session: Optional["KemoSession"] = field(default=False, init=False, repr=False)


    @classmethod
    def from_dict(cls, **fields) -> "Post":
        """
        Initializes a Post instance from a response fields.

        :return: A post instance.
        :rtype: :class:`.Post`
        """

        post_fields = fields["post"]

        added_field = post_fields.get("added", None)
        added = (datetime.strptime(added_field, MILI_DATE_FMT)
                 if added_field is not None
                 else None)
        
        edited_field = post_fields.get("edited", None)
        edited = (datetime.strptime(edited_field, DEFAULT_DATE_FMT)
                 if edited_field is not None
                 else None)
        
        file_dict = post_fields.get("file")
        attachments = post_fields.get("attachments")

        return cls(
            id=post_fields.get("id"),
            creator_id=post_fields.get("user"),
            service=ServiceType(post_fields.get("service")),
            title=post_fields.get("title").strip(),
            content=post_fields.get("content", ""),
            substring=post_fields.get("substring", ""),
            embed=post_fields.get("embed", {}),
            shared_file=post_fields.get("shared_file", False),
            added=added,
            published=datetime.strptime(post_fields.get("published"), DEFAULT_DATE_FMT),
            edited=edited,
            file=(File.from_dict(**sanitize_data_url(file_dict)) if file_dict else None),
            attachments=[File.from_dict(**sanitize_data_url(attachment_fields))
                         for attachment_fields in attachments],
            creator=post_fields.get("creator", None),
            is_revision=post_fields.get("is_revision", False)
        )


    @property
    def comments(self) -> CommentsList:
        """
        :return: The comments of the post.
        :rtype: list[:class:`.Comment`]
        """

        if not self.__comm_loaded:
            self.__comm_loaded = True
            self._comments = self.fetch_comments()

        return self._comments

    @property
    def flagged(self) -> bool:
        """
        :return: Wether the post is flagged for reimport.
        :rtype: :class:`bool`
        """

        if not self.__flag_loaded and not self.is_revision:
            self.__flag_loaded = True
            self._flagged = self._fetch_flagged()

        return self._flagged


    @property
    def revisions(self) -> PostRevsList:
        """
        :return: All the revisions of this post.
        :rtype: list[:class:`.PostRevision`]
        """

        if not self.__revs_loaded and not self.is_revision:
            self.__revs_loaded = True
            self._revisions = self._fetch_revisions()

        return self._revisions


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


    def set_underlying_session(self, ks: "KemoSession") -> "Post":
        """
        Quietly sets the session which the post uses for its requests.
        
        :param session: The session instance.
        
        :type session: :class:`.KemoSession`

        :return: The same instance of the post, for convenience.
        :rtype: :class:`.Creator`
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


    def save(self,
             path: Union["PathLike", Path, None]=None,
             force: bool=True,
             verbose: bool=True) -> bool:
        """
        Tries to save all the files in the post. Even if one file fails, it still tries to download
        the rest.

        :param path: The optional path where to store all the files. If it ends with '/*', it
                     will use its default name inside such folder.
        :param force: Wether to overwrite existing files
        :param verbose: Wether to track progress.

        :type path: :class:`PathLike` | :class:`Path` | ``None``
        :type force: :class:`bool`
        :type verbose: :class:`bool`

        :return: ``True`` if the download of `all` files was successful, or ``False`` if not.
        :rtype: :class:`bool`
        """

        files = self._all_files
        if verbose:
            if not files:
                print(f"Post '{self.title}' doesn't have attachments to download. Ignoring...")
                return True

        san_title = self.sanitized_title()

        if path is None:
            path = Path(san_title)
        elif isinstance(path, str) and path.endswith("/*"):
            path = Path(path[:-2]) / san_title
        elif not isinstance(path, Path):
            path = Path(path)

        path.mkdir(parents=True, exist_ok=True)

        return asyncio_run(self._save_task(files, path, force, verbose))


    async def _save_task(self,
                         files: FilesList,
                         path: Union["PathLike", Path, None]=None,
                         force: bool=True,
                         verbose: bool=True) -> bool:
        """
        Wrapper for saving files as a coroutine.

        :param files: The list of files to download.
        :param path: The optional path where to store all the files. If it ends with '/*', it
                     will use its default name inside such folder.
        :param force: Wether to overwrite existing files
        :param verbose: Wether to track progress.

        :type files: list[:class:`.File`]
        :type path: :class:`PathLike` | :class:`Path` | ``None``
        :type force: :class:`bool`
        :type verbose: :class:`bool`

        :return: ``True`` if the download of `all` files was successful, or ``False`` if not.
        :rtype: :class:`bool`
        """

        results = await tqdm_asyncio.gather(*(file.co_save(path, force=force, verbose=verbose)
                                                for file in files),
                                            desc=f"Post '{self.title}'",
                                            ncols=BAR_WIDTH,
                                            unit="file",
                                            position=0,
                                            smoothing=1.0,
                                            colour="blue")

        return all(results)


    def fetch_comments(self) -> CommentsList:
        """
        Fetches the comments of the post.
    
        .. warning:: This is designed for internal purposes, as it is recommended to use the :attr:`.comments` property instead. However, it can also be used as-is to prevent using a potentially outdated field.

        :return: A list of the comments of this post.
        :rtype: list[:class:`.Comment`]
        """

        response = (get if self.__kemo_session is None else self.__kemo_session.get)(f"/{self.service}/user/{self.creator_id}/post/{self.id}/comments")
        comments = []

        for comment_fields in response.json():
            comment_fields.update(creator=self.creator, post=self)
            comments.append(Comment.from_dict(**comment_fields))

        return comments

    def _fetch_flagged(self) -> bool:
        """
        .. warning:: `(for internal purposes)`
        Checks with a request if a post is flagged for reimport.
        According to the docs, it should have status code of 200 if it is flagged, and
        404 if it's not.

        :return: Wether or not the post is flagged for reimport.
        :rtype: :class:`bool`
        """

        response = (get if self.__kemo_session is None else self.__kemo_session.get)(f"/{self.service}/user/{self.creator_id}/post/{self.id}/flag")
        return response.status_code == 200


    def _fetch_revisions(self) -> PostRevsList:
        """
        .. warning:: `(for internal purposes)`
        Fetches a request all the revisions of the post.

        :return: All the revisions of this post, if any.
        :rtype: list[:class:`.PostRevision`]
        """

        response = (get if self.__kemo_session is None else self.__kemo_session.get)(f"/{self.service}/user/{self.creator_id}/post/{self.id}/revisions")
        revisions = []

        for revs_fields in response.json():
            revs_fields.update(creator=self.creator, is_revision=True)
            subpost = Post.from_dict(**revs_fields).set_underlying_session(self.__kemo_session)

            revs_fields.update(post=subpost)
            revisions.append(PostRevision.from_dict(**revs_fields))

        return revisions
