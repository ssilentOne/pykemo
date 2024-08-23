Welcome to Pykemo's documentation!
===================================

Pykemo is a Python library that effectively functions as a binding to the
`Kemono API <https://kemono.su/api/schema>`_.

.. dropdown:: Examples

    .. dropdown:: Retrieving a creator

        You can create a :py:class:`.Creator` instance like so:

        .. tab-set::

            .. tab-item:: Using ServiceType

                .. code-block:: python

                    from pykemo import get_creator, ServiceType

                    creator_id = "2658856"

                    creator = get_creator(ServiceType.FANBOX, creator_id)
                    print(creator)


            .. tab-item:: String literal

                .. code-block:: python

                    from pykemo import get_creator

                    creator_id = "2658856"

                    creator = get_creator("fanbox", creator_id)
                    print(creator)

        And it will print:

        .. code-block::

            Creator(id='2658856', name='fumihiko', service=<ServiceType.FANBOX: 'fanbox'>)


    .. dropdown:: Fetching posts

        From there you can check its posts:

        .. tab-set::

            .. tab-item:: Last Posts

                .. code-block:: python

                    # Fetching last 5 posts
                    last_posts = creator.posts(max_posts=5)

                    for post in last_posts:
                        print(post)


            .. tab-item::  Filter by Date

                .. code-block:: python

                    from datetime import datetime

                    # Every post from June 15th to July 23rd
                    before = datetime(year=2024, month=7, day=23)
                    since = datetime(year=2024, month=6, day=15)
                    specific_posts = creator.posts(before=before, since=since)

                    for post in specific_posts:
                        print(post)

        And it will show:

        .. code-block::

            Post(id='8104634', creator_id='2658856', service='fanbox', title='獅●ぼ●ん（気高いメスライオンが枕●業Vtuber）')
            Post(id='8101402', creator_id='2658856', service='fanbox', title='大●ス●ル（おっπ見せてほしいとお願いしたらVtuber線画）')
            Post(id='8100642', creator_id='2658856', service='fanbox', title='【閲覧注意】湊●く●（目の前で寝取られるVtuber線画）')
            Post(id='8100373', creator_id='2658856', service='fanbox', title='湊●く●（お料理中に襲われてVtuber線画）')
            ...


        *Alternatively,* you can also use the helper function :py:func:`.get_posts()`, which has the same parameters,
        for a search of all the recent posts of every creator.

        .. code-block:: python

            from pykemo import get_posts()

            any_posts = get_posts(max_posts=15)


    .. dropdown:: Downloading files

        Finally, you can downloads the files of any post, if there is any:

        .. tab-set::

            .. tab-item:: Manually

                .. code-block:: python

                    chosen_one = specific_posts[0]

                    for file in chosen_one.attachments:
                        file.save("./download/", verbose=False)

            .. tab-item:: From Post

                .. code-block:: python

                    chosen_one = specific_posts[0]

                    chosen_one.save("/download/*", verbose=True)

        .. note:: Use ``verbose=True`` to see the fancy progress bars.

.. toctree::
    :caption: Table of Contents
    :maxdepth: 2

    Creators <pykemo/creators/creators.rst>
    Discord Types <pykemo/discord/discord.rst>
    Enums <pykemo/enums/enums.rst>
    Exceptions <pykemo/exceptions/exceptions.rst>
    Files <pykemo/files/files.rst>
    Helper Types <pykemo/general/general.rst>
    Posts <pykemo/posts/posts>
