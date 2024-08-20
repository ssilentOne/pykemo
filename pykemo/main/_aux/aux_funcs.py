"""
Auxiliar functions module.
"""

from datetime import datetime
from typing import TYPE_CHECKING, Optional, TypeAlias, Union

from grequests import map as async_map

from ..core import async_get, get

if TYPE_CHECKING:
    from requests import Response

    from ..core import UrlLike
    from ..files import FileDict

DateOrFmt: TypeAlias = Union[str, datetime]
ParamsFmtDict: TypeAlias = dict[str, Union[str, int]]

DEFAULT_DATE_FMT: str = r"%Y-%m-%dT%H:%M:%S"
"The default date formatting to use."

MILI_DATE_FMT: str = rf"{DEFAULT_DATE_FMT}.%f"
"The default date, added miliseconds."

ASYNC_FETCH_BATCH: int = 50
"""
Number of asynchronous request to make at a time in any given batch.
"""

DEFAULT_BATCH_SEND_SIZE: int = 10
"""
Inside the batch, how many asynchronous requests to send at a time.
"""


def sanitize_data_url(file_dict: "FileDict") -> "FileDict":
    """
    Appends the relative path of the file path with '/data'.
    Returns the dict itself for convenience purposes.
    """

    file_path = file_dict.get("path", None)
    if file_path is not None:
        file_dict["path"] = f"/data{file_path}"

    return file_dict


def process_fmt(fmt: Optional[str], /) -> str:
    "Converts the format to a default one if it is not present."

    return (fmt if fmt is not None else DEFAULT_DATE_FMT)


def process_date(date: DateOrFmt, fmt: Optional[str]) -> datetime:
    "Process the date if it is a string, or uses as-is if it is already a datetime object."

    if isinstance(date, str):
        return datetime.strptime(date, process_fmt(fmt))

    return date


def before_date(date1: DateOrFmt,
           date2: DateOrFmt,
           *,
           fmt1: Optional[str]=None,
           fmt2: Optional[str]=None) -> bool:
    "Compares if the dates (in string form) with date1 < date2"

    return process_date(date1, fmt1) < process_date(date2, fmt2)


def since_date(date1: DateOrFmt,
          date2: DateOrFmt,
          *,
          fmt1: Optional[str]=None,
          fmt2: Optional[str]=None) -> bool:
    "Compares if the dates (in string form) with date1 >= date2"

    return process_date(date1, fmt1) >= process_date(date2, fmt2)


def query_params(query: Optional[str]=None,
                 offset: Optional[int]=None,
                 stepping: int=0) -> ParamsFmtDict:
    "Formats a parameters dictionary to send with a response in messages queries."

    params = {}

    if query is not None:
        params.update(q=query)

    if offset is not None:
        if offset % stepping != 0:
            raise ValueError(f"Value for offset {offset} not valid."
                                f" Must be a multiple of {stepping}.")
        offset_val = offset


    params.update(o=offset_val)
    return params


def get_posts_responses(*,
                        endpoint: "UrlLike",
                        query: Optional[str]=None,
                        max_posts: Optional[int]=None,
                        page_stepping: int) -> list["Response"]:
    """
    Gets the responses of posts by page.
    """

    responses = []

    if max_posts is None: # Try to get ALL the posts
        cur_page = 0
        while True:
            page_response = get(endpoint,
                                params=query_params(query,
                                                    cur_page * page_stepping,
                                                    page_stepping))
            if page_response.status_code != 429:
                responses.extend(page_response.json())

            if  not page_response.json():
                break

            cur_page += 1

    else:
        n_pages = (max_posts // page_stepping) + 1 # one more for the surplus
        for page in range(n_pages):
            page_response = get(endpoint,
                                params=query_params(query,
                                                    page * page_stepping,
                                                    page_stepping))

            # by this point, one would expect this to be a list of posts
            if page_response.status_code != 429:
                responses.extend(page_response.json())

    return responses


def async_get_posts_responses(*,
                              endpoint: "UrlLike",
                              query: Optional[str]=None,
                              max_posts: Optional[int]=None,
                              page_stepping: int,
                              batch_send_size: Optional[int]=None) -> list["Response"]:
    """
    Gets the asynchronous responses of posts by page.
    """

    responses = []
    exit_flag = False
    send_size = (DEFAULT_BATCH_SEND_SIZE if batch_send_size is not None else batch_send_size)

    if max_posts is None: # Try to get ALL the posts
        cur_page = 0
        while not exit_flag:
            req_batch = []
            for _ in range(ASYNC_FETCH_BATCH):
                page_async_req = async_get(
                    endpoint,
                    params=query_params(query,
                                        cur_page * page_stepping,
                                        page_stepping))
                req_batch.append(page_async_req)
                cur_page += 1

            res_batch = async_map(req_batch, size=send_size)

            for page_response in res_batch:
                if page_response.status_code != 429:
                    responses.extend(page_response.json())
                    if not page_response.json():
                        exit_flag = True

    else:
        n_pages = (max_posts // page_stepping) + 1 # one more for the surplus
        req_batch = (async_get(endpoint,
                                params=query_params(query,
                                                    page * page_stepping,
                                                    page_stepping))
                    for page in range(n_pages))
        res_batch = async_map(req_batch, size=send_size)

        for res in res_batch:
            if res.status_code != 429:
                responses.extend(res.json())

    return responses
