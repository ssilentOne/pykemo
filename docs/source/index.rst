Welcome to Pykemo's documentation!
===================================

Pykemo is a Python library that effectively functions as a binding to the
`Kemono API <https://kemono.su/documentation/api>`_.

.. dropdown:: Examples

    .. dropdown:: Retrieving a creator

        You can create a :py:class:`.Creator` instance like so:

        .. tab-set::

            .. tab-item:: Using ServiceType

                .. code-block:: python

                    import asyncio
                    from pykemo import KemoSession, get_creator, ServiceType

                    async def main():
                        async with KemoSession() as s:
                            creator_id = "2658856"

                            creator = get_creator(ServiceType.FANBOX, creator_id, s)
                            print(creator)

                    asyncio.run(main())


            .. tab-item:: String literal

                .. code-block:: python

                    import asyncio
                    from pykemo import KemoSession, get_creator

                    async def main():
                        async with KemoSession() as s:
                            creator_id = "2658856"

                            creator = get_creator("fanbox", creator_id, s)
                            print(creator)

                    asyncio.run(main())

        And it will print:

        .. code-block::

            Creator(id='2658856', name='fumihiko', service=<ServiceType.FANBOX: 'fanbox'>)


    .. dropdown:: Fetching posts

        From there you can check its posts:

        .. tab-set::

            .. tab-item:: Last Posts

                .. code-block:: python

                    # Fetching last 5 posts
                    last_posts = await creator.posts(max_posts=5)

                    for post in last_posts:
                        print(post)


            .. tab-item::  Filter by Date

                .. code-block:: python

                    from datetime import datetime

                    # Every post from March 1st to 4rd
                    before = datetime(year=2025, month=3, day=4)
                    since = datetime(year=2025, month=3, day=1)
                    specific_posts = await creator.posts(before=before, since=since)

                    for post in specific_posts:
                        print(post)

        And it will show:

        .. code-block::

            Post(id='9484523', creator_id='2658856', service=<ServiceType.FANBOX: 'fanbox'>, title='白●ノ●ル（リクエストNTR）（と●の●ら撮影会修正）')
            Post(id='9482064', creator_id='2658856', service=<ServiceType.FANBOX: 'fanbox'>, title='と●の●ら（そ●友さん達と撮影会Vtuber）')
            Post(id='9481266', creator_id='2658856', service=<ServiceType.FANBOX: 'fanbox'>, title='ボテ注意常●ト●Vtuber')
            Post(id='9479140', creator_id='2658856', service=<ServiceType.FANBOX: 'fanbox'>, title='白●フ●キ（●やんけ①②）')
            ...


        *Alternatively,* you can also use the helper function :py:func:`.get_posts()`, which has the same parameters,
        for a search of all the recent posts of every creator.

        .. code-block:: python

            from pykemo import get_posts()

            async with KemoSession() as s:
                any_posts = await get_posts(max_posts=15, kemo_session=s)


    .. dropdown:: Downloading files

        Finally, you can downloads the files of any post, if there is any:

        .. tab-set::

            .. tab-item:: Manually

                .. code-block:: python

                    chosen_one = specific_posts[0]

                    for file in chosen_one.attachments:
                        await file.save("./download/", verbose=False)

            .. tab-item:: From Post

                .. code-block:: python

                    chosen_one = specific_posts[0]

                    await chosen_one.save("/download/*", verbose=True)

        .. note:: Use ``verbose=True`` to see the fancy progress bars.

    .. dropdown:: Ussing Accounts

        Pykemo supports an interface that allows you to login into your account. It automatically uses
        a dedicated session inside to persist your session key.

        .. tab-set::

            .. tab-item:: Consumer

                A normal user's account.

                .. code-block:: python

                    import asyncio
                    import os
                    from pykemo.general import login

                    async def main():
                        async with await login(os.environ["username"], os.environ["password"]) as acc:
                            creator = await acc.get_creator("fanbox", "2658856")
                            post = await creator.get_post("9441683")

                            await post.save("./path/to/download/*")

                    asyncio.run(main())

.. toctree::
    :caption: Table of Contents
    :maxdepth: 2

    Creators <pykemo/creators/creators.rst>
    Accounts <pykemo/accounts/account.rst>
    Discord Types <pykemo/discord/discord.rst>
    Enums <pykemo/enums/enums.rst>
    Exceptions <pykemo/exceptions/exceptions.rst>
    Files <pykemo/files/files.rst>
    Helper Types <pykemo/general/general.rst>
    Posts <pykemo/posts/posts.rst>
    Sessions <pykemo/sessions/sessions.rst>
    Tags <pykemo/tags/tags.rst>
    Creator Links Requests <pykemo/moderation/creator_links.rst>
