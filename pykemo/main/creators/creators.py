"""
Creators module.
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import TYPE_CHECKING, Literal, Optional, TypeAlias, Union

from grequests import map as async_map

from ..announcements import Announcement
from ..core import UrlType, async_get, get
from ..fancards import Fancard
from ..posts import DEFAULT_DATE_FMT, ELEMENTS_PER_PAGE, Post, PostsList
from ..services import ServiceType

if TYPE_CHECKING:
    from requests import Response

    from ..core import UrlLike
    from ..services import ServiceLike

CreatorsList: TypeAlias = list["Creator"]
_CreatorFields: TypeAlias = Literal["id", "name", "service", "indexed", "updated",
                                    "public_id", "favorited"]
CreatorDict: TypeAlias = dict[_CreatorFields, Union[str, int, None]]
AnnouncementsList: TypeAlias = list[Announcement]
FancardsList: TypeAlias = list[Fancard]

ASYNC_FETCH_BATCH: int = 50
"""
Number of asynchronous request to make at a time in any given batch.
"""

DEFAULT_BATCH_SEND_SIZE: int = 10
"""
Inside the batch, how many asynchronous requests to send at a time.
"""


@dataclass(kw_only=True)
class Creator:
    """
    Container class for a creator.

    id: It is the ID of the creator.
    name: It is the given name of the creator.
    service: The service that provides the content.
    indexed: Datetime that expresses when the creator is indexed.
    updated: Datetime that expresses when the creator was last updated.
    favorited: A integer displaying how many have favorited this creator.
    """

    id: str
    name: Optional[str]
    service: ServiceType
    indexed: datetime = field(repr=False)
    updated: datetime = field(repr=False)
    public_id: Optional[str] = field(repr=False)
    favorited: Optional[int] = field(repr=False)

    #unloaded fields
    _announcements: AnnouncementsList = field(default_factory=list, init=False, repr=False)
    __ann_loaded: bool = field(default=False, init=False, repr=False)

    _fancards: FancardsList = field(default_factory=list, init=False, repr=False)
    __fanc_loaded: bool = field(default=False, init=False, repr=False)


    @classmethod
    def from_dict(cls, **fields: CreatorDict) -> "Creator":
        """
        Initializes a creator from a dictionary containing its properties.
        """

        date_fmt = rf"{DEFAULT_DATE_FMT}.%f"

        return cls(
            id=fields.get("id", None) or fields.get("user"),
            name=fields.get("name", None),
            service=ServiceType(fields.get("service")),
            indexed=datetime.strptime(fields.get("indexed"), date_fmt),
            updated=datetime.strptime(fields.get("updated"), date_fmt),
            public_id=fields.get("public_id", None),
            favorited=fields.get("favorited", None)
        )


    @classmethod
    def from_profile(cls, service: "ServiceLike", creator_id: str) -> Optional["Creator"]:
        """
        Retrieves a creator using its profile info.
        """

        creator_response = get(f"/{service}/user/{creator_id}/profile")

        if creator_response.status_code == 404:
            return None

        return Creator.from_dict(**creator_response.json())


    @staticmethod
    def query_params(query: Optional[str], offset: Optional[int]) -> dict[str, Union[str, int]]:
        "Processes and creates a dictionary that is the aprameters of a request."

        params = {}

        if query is not None:
            params.update(q=query)

        if offset is not None:
            if offset % ELEMENTS_PER_PAGE != 0:
                raise ValueError(f"Value for offset {offset} not valid."
                                 f" Must be a multiple of {ELEMENTS_PER_PAGE}.")

            params.update(o=offset)

        return params


    @property
    def announcements(self) -> AnnouncementsList:
        """
        Gets a list of the creator's announcements, if any. Mainly relevant for
        Patreon service.
        """

        if not self.__ann_loaded:
            self.__ann_loaded = True
            self._announcements = self._fetch_announcements()

        return self._announcements


    @property
    def fancards(self) -> FancardsList:
        """
        Gets a list of the fancards associated with this creator. If not from a Fanbox service,
        it will return an empty list instead.
        """

        if not self.__fanc_loaded:
            self.__fanc_loaded = True
            self._fancards = self._fetch_fancards()

        return self._fancards


    @property
    def url(self) -> "UrlLike":
        """
        Retrieves the URL of the creator.
        """

        return f"{UrlType.SITE}/{self.service}/user/{self.id}"


    def other_links(self) -> list["Creator"]:
        """
        Searches for other accounts of this creator.
        """

        link_response = get(f"/{self.service}/user/{self.id}/links")
        links = []

        for link_fields in link_response.json():
            creator = Creator.from_profile(link_fields.get("service"),
                                           link_fields.get("id"))
            if creator is not None:
                links.append(creator)

        return links


    @staticmethod
    def get_posts_responses(*,
                            endpoint: "UrlLike",
                            query: Optional[str]=None,
                            max_posts: Optional[int]=None) -> list["Response"]:
        """
        Gets the responses of posts by page.
        """

        responses = []

        if max_posts is None: # Try to get ALL the posts
            cur_page = 0
            while True:
                page_response = get(endpoint,
                                    params=Creator.query_params(query, cur_page * ELEMENTS_PER_PAGE))
                if page_response.status_code != 429:
                    responses.extend(page_response.json())

                if  not page_response.json():
                    break

                cur_page += 1

        else:
            n_pages = (max_posts // ELEMENTS_PER_PAGE) + 1 # one more for the surplus
            for page in range(n_pages):
                page_response = get(endpoint,
                                    params=Creator.query_params(query, page * ELEMENTS_PER_PAGE))

                # by this point, one would expect this to be a list of posts
                if page_response.status_code != 429:
                    responses.extend(page_response.json())

        return responses


    @staticmethod
    def async_get_posts_responses(*,
                                  endpoint: "UrlLike",
                                  query: Optional[str]=None,
                                  max_posts: Optional[int]=None,
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
                        params=Creator.query_params(query, cur_page * ELEMENTS_PER_PAGE))
                    req_batch.append(page_async_req)
                    cur_page += 1

                res_batch = async_map(req_batch, size=send_size)

                for page_response in res_batch:
                    if page_response.status_code != 429:
                        responses.extend(page_response.json())
                        if not page_response.json():
                            exit_flag = True

        else:
            n_pages = (max_posts // ELEMENTS_PER_PAGE) + 1 # one more for the surplus
            req_batch = (async_get(endpoint,
                                   params=Creator.query_params(query, page * ELEMENTS_PER_PAGE))
                        for page in range(n_pages))
            res_batch = async_map(req_batch, size=send_size)

            for res in res_batch:
                if res.status_code != 429:
                    responses.extend(res.json())

        return responses


    def posts(self,
              *,
              query: Optional[str]=None,
              max_posts: Optional[int]=None,
              before: Optional[datetime]=None,
              since: Optional[datetime]=None,
              asynchronous: bool=False) -> PostsList:
        """
        Retrieves posts under this creator. If the creator is from Discord, it won't retrieve any,
        as that service doesn't use 'posts'.

        query: The string to search for specific posts.
        max_posts: The max number of posts to look through. This is NOT necessarily the number of
                   posts to enter the lists.
        before: Include only posts before this date.
        since: Include only posts after and including this date.
        asynchronous: Wether to use asynchronous requests to maybe boost performance. It's really
                      only recommended with queries of no more than 350 posts. Too many queries
                      overwhelms the server and it actually slows the request down.
        """

        if max_posts is not None and max_posts <= 0:
            raise ValueError(f"max_posts must be an integer greater than zero, not '{max_posts}'")

        posts_req = (self.async_get_posts_responses if asynchronous else self.get_posts_responses)
        response_bodies = posts_req(endpoint=f"/{self.service}/user/{self.id}",
                                    query=query, max_posts=max_posts)
        posts_list = []

        for post_fields in response_bodies:
            published_str = post_fields["published"]
            if ((before is not None and not Post.before_static(published_str, before)) or
                (since is not None and not Post.since_static(published_str, since))):
                continue

            post_fields.update(creator=self)
            post = Post.from_dict(**post_fields)

            posts_list.append(post)

        return posts_list


    def get_post(self, post_id: str) -> Optional[Post]:
        """
        Get a specific post by its ID.
        """

        response = get(f"/{self.service}/user/{self.id}/post/{post_id}")

        if response.status_code == 404:
            return None

        return Post.from_dict(**response.json())


    def _fetch_announcements(self) -> AnnouncementsList:
        """
        Fetches a request with the creator's announcements.
        """

        response = get(f"/{self.service}/user/{self.id}/announcements")
        announcements = []

        for ann_fields in response.json():
            ann_fields.update(creator=self)
            announcements.append(Announcement.from_dict(**ann_fields))

        return announcements


    def _fetch_fancards(self) -> FancardsList:
        """
        Fetches a request with the creator's fancards.
        If the service is not Fanbox, it will return an empty list instead.
        """

        fancards = []

        if self.service == ServiceType.FANBOX:
            response = get(f"/{self.service}/user/{self.id}/fancards")

            for fancard_fields in response.json():
                fancard_fields.update(creator=self)
                fancards.append(Fancard.from_dict(**fancard_fields))

        return fancards
