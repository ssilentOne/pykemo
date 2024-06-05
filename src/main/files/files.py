"""
Files module.
"""

from io import BytesIO, FileIO
from typing import TYPE_CHECKING, Optional, TypeAlias, Union
from pathlib import Path

from ..core import UrlType, get

if TYPE_CHECKING:
    from os import PathLike

    from ..core import UrlLike

FileContent: TypeAlias = Union[FileIO, BytesIO, None]
"""
The actual file. Might be empty if not downloaded yet.
"""


class File:
    "A normal file. It may very well be text or a binary type."

    def __init__(self,
                 name: "PathLike",
                 path: "PathLike") -> None:
        """
        Initializes a File. It may not have downloaded content yet, and merely be a
        placeholder for its URL.

        name: The name of the file.
        path: The relative path of the file's location.
        """

        self._name: "PathLike" = name
        self._rel_path: "UrlLike" = f"/data{path}"
        self._url: "UrlLike" = f"{UrlType.DATA}{self._rel_path}"

        self._content: FileContent = None
        self._content_type: Optional[str] = None


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
    def url(self) -> "UrlLike":
        "Gives the URL of the file."

        return self._url

    @property
    def content(self) -> FileContent:
        "Gives the underlying file of this object, or the lack thereof."

        return self._content
    
    @property
    def content_type(self) -> str:
        "Gives the MME type of the file content. Might be `None` if not downloaded yet."

        return self._content_type


    def downloaded(self) -> bool:
        "Determines if the files has been downloaded or not."

        return self.content is not None


    def download(self) -> bool:
        """
        Tries to download the file. Returns `True` if it is successful, or `False` if not.
        """

        response = get(self._rel_path, url_type=UrlType.DATA)
        self._content_type = response.headers.get("content-type", None)

        if self.content_type.startswith("text"):
            file_type = FileIO
        else:
            file_type = BytesIO

        self._content = file_type(response.content)
        self._content.seek(0) # To return the pointer to the start

        return True


    def save(self, path: Union["PathLike", Path]="", force: bool=True) -> bool:
        """
        Tries to save the file to a given path.

        path: The path in which to save the file.
        force: If another file is found, overwrite it.
        """

        if not self.downloaded():
            self.download()

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

        w_mode = f"w{'b' if isinstance(self.content, BytesIO) else ''}"

        with path.open(mode=w_mode) as file:
            file.write(self.content.read())
            self.content.seek(0)

        return True
