"""
Files module.
"""

from typing import TYPE_CHECKING, Optional, Union, TypeAlias, Literal
from tqdm import tqdm
from pathlib import Path

from ..core import UrlType, get

if TYPE_CHECKING:
    from os import PathLike

    from ..core import UrlLike

FilesList: TypeAlias = list["File"]
FileDict: TypeAlias = dict[Literal["name", "path"], Union[str, "PathLike", "UrlLike"]]

BAR_WIDTH: int = 125
"""
The width of the progress bar in verbose mode.
"""


class File:
    "A normal file. It may very well be text or a binary type."

    def __init__(self,
                 name: "PathLike",
                 path: "PathLike",
                 content_type: Optional[str]=None,
                 url_source: "UrlLike"=UrlType.DATA,
                 server: int=3) -> None:
        """
        Initializes a File. It may not have downloaded content yet, and merely be a
        placeholder for its URL.

        :param name: The name of the file.
        :param path: The relative path of the file's location.
        :param content_type: The MIME type of the file. May be unitialized to be inferred
                             later from the download.
        :param url_source: The URL root to download from.
        :param server: Which server to refer to, if using the DATA url type. Different files
                       may be in different servers there, which do affect the URL prefix.

        :type name: :class:`PathLike`
        :type path: :class:`PathLike`
        :type content_type: Optional[:class:`str`]
        :type url_source: Optional[:type:`.UrlLike`]
        :type server: :class:`int`
        """

        self._name: "PathLike" = name
        self._rel_path: "UrlLike" = path

        self._content_type: Optional[str] = content_type
        self._url_root: "UrlLike" = url_source
        self._server: int = server

        if self._is_data(self._url_root):
            self._url_root = self._url_root.format(i=self._server)



    @classmethod
    def from_dict(cls, **fields) -> "File":
        """
        Initializes a File instance from a response fields.

        :return: A file instance.
        :rtype: :class:`.File`
        """

        return cls(
            name=fields.get("name"),
            path=fields.get("path")
        )


    def __str__(self) -> str:
        """
        :return: Represents the :class:`.File` class in a string.
        :rtype: :class:`str`
        """

        return repr(self)
    

    def __repr__(self) -> str:
        """
        :return: A representation of a :class:`.File` class as-is.
        :rtype: :class:`str`
        """

        return f"<File '{self.name}' in '{self._rel_path}'>"


    @staticmethod
    def _is_data(url: "UrlLike") -> bool:
        """
        .. warning:: `(for internal purposes)`
        Checks if the URL is of the DATA url type.

        :param url: The URL to evaluate.
        
        :type url: :type:`.UrlLike`

        :returns: The result of checking if the URL is of type :attr:`.UrlType.DATA`
        :rtype: :class:`bool`
        """

        return url == UrlType.DATA


    @property
    def name(self) -> "PathLike":
        """
        :return: The name of the file `(with extension)`.
        :rtype: :class:`PathLike`
        """

        return self._name

    
    @property
    def content_type(self) -> Optional[str]:
        """
        :return: The MIME type of the file content. Might be ``None`` if not downloaded yet.
        :rtype: Optional[:class:`str`]
        """

        return self._content_type


    @property
    def url(self) -> "UrlLike":
        """
        :return: The full URL of the file, where it's downloaded from.
        :rtype: :type:`.UrlLike`
        """

        return f"{self._url_root}{self._rel_path}"


    def _is_text_mode(self) -> bool:
        """
        Parses the MIME content type and tries to detect if the content is a text file.

        :return: ``True`` if the content is not binary, or ``False`` if it is.
        :rtype: :class:`bool`
        """

        return self.content_type is not None and self.content_type.startswith("text")


    def save(self,
             path: Union["PathLike", Path]="",
             force: bool=True,
             verbose: bool=False,
             chunk_size: int=4096) -> bool:
        """
        Tries to save the file to a given path.

        :param path: The path in which to save the file.
        :param force: If another file is found, overwrite it.
        :param verbose: Wether to track progress.
        :param chunk_size: The size `(in bytes)` of the chunks to download at a
                           time (usually a power of 2).

        :type path: :class:`PathLike` | :class:`Path`
        :type force: :class:`bool`
        :type verbose: :class:`bool`
        :type chunk_size: :class:`int`

        :return: Wether or not the download was successful.
        :rtype: :class:`bool`
        """

        if not path:
            path = Path(self.name)
        elif not isinstance(path, Path):
            path = Path(path)

        if not path.suffix or path.is_dir():
            path /= self.name

        if not path.exists():
            path.parent.mkdir(parents=True, exist_ok=True)
        elif path.exists() and not force:
            return False
        
        response = get(self._rel_path, url_type=self._url_root, stream=True)

        if self.content_type is None:
            self._content_type = response.headers.get("content-type", None)

        w_mode = f"w{'b' if not self._is_text_mode() else ''}"

        context = path.open(mode=w_mode)
        if verbose:
            context = tqdm.wrapattr(context,
                                    "write",
                                    miniters=1,
                                    desc=f"->\t{self.name}",
                                    total=int(response.headers.get("content-length", 0)),
                                    ncols=BAR_WIDTH,
                                    leave=False,
                                    position=1,
                                    smoothing=1.0,
                                    colour="green")

        with context as fout:
            for chunk in response.iter_content(chunk_size=chunk_size):
                fout.write(chunk)

        return True
