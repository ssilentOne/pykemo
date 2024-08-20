"""
Files module.
"""

from typing import TYPE_CHECKING, Optional, Union
from tqdm import tqdm
from pathlib import Path

from ..core import UrlType, get

if TYPE_CHECKING:
    from os import PathLike

    from ..core import UrlLike

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
                 server: int=3) -> None:
        """
        Initializes a File. It may not have downloaded content yet, and merely be a
        placeholder for its URL.

        name: The name of the file.
        path: The relative path of the file's location.
        content_type: The MIME type of the file. May be unitialized to be inferred later
                      from the download.
        server: Which server to refer to. Different files may be in different servers, which
                do affect the URL prefix.
        """

        self._name: "PathLike" = name
        self._rel_path: "UrlLike" = f"/data{path}"

        self._content_type: Optional[str] = content_type
        self._server: int = server


    @classmethod
    def from_dict(cls, **fields) -> "File":
        """
        Initializes a file from a response fields.
        """

        return cls(
            name=fields.get("name"),
            path=fields.get("path")
        )


    def __str__(self) -> str:
        "Represents the File class in a string."

        return repr(self)
    

    def __repr__(self) -> str:
        "Represents a File as-is."

        return f"<File '{self.name}' in '{self._rel_path}'>"


    @property
    def name(self) -> "PathLike":
        "Gives the name of the file."

        return self._name

    
    @property
    def content_type(self) -> str:
        "Gives the MME type of the file content. Might be `None` if not downloaded yet."

        return self._content_type


    @property
    def url(self) -> "UrlLike":
        "Gives the URL of the file."

        return f"{UrlType.DATA.format(i=self._server)}{self._rel_path}"


    def _is_text_mode(self) -> bool:
        """
        Tries to detect if the content is a text file.
        """

        return self.content_type is not None and self.content_type.startswith("text")


    def save(self,
             path: Union["PathLike", Path]="",
             force: bool=True,
             verbose: bool=False,
             chunk_size: int=4096) -> bool:
        """
        Tries to save the file to a given path.

        path: The path in which to save the file.
        force: If another file is found, overwrite it.
        verbose: Wether to track progress.
        chunk_size: The size (in bytes) of the chunks to download at a time (usually a power of 2).
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
        
        response = get(self._rel_path, url_type=UrlType.DATA.format(i=self._server), stream=True)

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
