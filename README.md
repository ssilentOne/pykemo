
██████╗░██╗░░░██╗██╗░░██╗███████╗███╗░░░███╗░█████╗░ <br/>
██╔══██╗╚██╗░██╔╝██║░██╔╝██╔════╝████╗░████║██╔══██╗ <br/>
██████╔╝░╚████╔╝░█████═╝░█████╗░░██╔████╔██║██║░░██║ <br/>
██╔═══╝░░░╚██╔╝░░██╔═██╗░██╔══╝░░██║╚██╔╝██║██║░░██║ <br/>
██║░░░░░░░░██║░░░██║░╚██╗███████╗██║░╚═╝░██║╚█████╔╝ <br/>
╚═╝░░░░░░░░╚═╝░░░╚═╝░░╚═╝╚══════╝╚═╝░░░░░╚═╝░╚════╝░ <br/>
<hr/>
<img alt="pyk_logo.png" align="left" src="media/img/pykemo_logo.png" height=128 width=128 />

[![Latest tag](https://img.shields.io/github/v/tag/ssilentOne/pykemo?label=release)](https://github.com/ssilentOne/pykemo/releases/latest)
[![Docs](https://readthedocs.org/projects/pykemo/badge/?version=latest)](https://pykemo.readthedocs.io/en/latest/?badge=latest)
![linter](https://github.com/ssilentOne/pykemo/actions/workflows/linter.yml/badge.svg)
![Tests](https://github.com/ssilentOne/pykemo/actions/workflows/tests.yml/badge.svg)
![stars](https://img.shields.io/github/stars/ssilentOne/pykemo?label=Stars&style=social)
![views](https://img.shields.io/github/watchers/ssilentOne/pykemo?label=Views&style=social)

Python library binding to the [Kemono API](https://kemono.su/documentation/api).

<br/>
<br/>
<br/>
<br/>
<br/>

It has the following features:

* **All HTTP requests logic abstracted behind Python  types.** You can interact with the API
using custom classes like `Creator` or `Post`. The library revolves around the `KemoSession` type.
    - _This means that for downloading files there is already an interface_ (`File`) _for that._

* **OS Independent.** Being pure-python, the library works on Windows, MacOS and Linux alike.
    - _That being said,_ it **is** possible that [some dependencies](https://pypi.org/project/aiohttp/#files)
    require a specific build depending on the platform.

* **Asynchronous request for performance boosts.** With the use of async programming, the requests
are all made _concurrently_.

* **Ready to install.** Rather than installing from source, the [releases](https://github.com/ssilentOne/pykemo/releases)
have each its own wheels to distribute at your leisure.

<hr style="height:1px; width:35%" />

* [Examples](#examples)
    - [_Retrieving a Creator_](#retrieving-a-creator)
    - [_Fetching Posts_](#fetching-posts)
    - [_Downloading Files_](#downloading-files)
    - [_Loggin into an Account_](#login-into-an-account)
* [Dependencies](#dependencies)
* [Documentation](#documentation)
* [How to Install](#how-to-install)
    - [Using Wheels](#using-wheels)
    - [From Source](#from-source)

<hr style="height:1px; width:35%" />

# Examples

### Retrieving a creator

You can create a `Creator` instance like so:

```py
import asyncio
from pykemo import KemoSession, get_creator, ServiceType

async def main():
    session = KemoSession()
    creator_id = "2658856"

    async with session:
        creator = await get_creator(ServiceType.FANBOX, creator_id, session)

        # This works as well
        creator2 = await get_creator("fanbox", creator_id, session)

        print(creator)

asyncio.run(main())
```

And it will print:
```
Creator(id='2658856', name='fumihiko', service=<ServiceType.FANBOX: 'fanbox'>)
```

### Fetching posts

From there you can check its posts:
```py
from datetime import datetime

# Fetching last 5 posts
last_posts = await creator.posts(max_posts=5)

# Every post from March 1st to 4rd
before = datetime(year=2025, month=3, day=4)
since = datetime(year=2025, month=3, day=1)
specific_posts = await creator.posts(before=before, since=since)

for post in specific_posts:
    print(post)
```
And it will show:
```
Post(id='9484523', creator_id='2658856', service=<ServiceType.FANBOX: 'fanbox'>, title='白●ノ●ル（リクエストNTR）（と●の●ら撮影会修正）')
Post(id='9482064', creator_id='2658856', service=<ServiceType.FANBOX: 'fanbox'>, title='と●の●ら（そ●友さん達と撮影会Vtuber）')
Post(id='9481266', creator_id='2658856', service=<ServiceType.FANBOX: 'fanbox'>, title='ボテ注意常●ト●Vtuber')
Post(id='9479140', creator_id='2658856', service=<ServiceType.FANBOX: 'fanbox'>, title='白●フ●キ（●やんけ①②）')
...
```

_Alternatively,_ you can also use the helper function `get_posts()`, which has the same parameters,
for a search of all the recent posts of every creator.
```py
from pykemo import get_posts

async with KemoSession() as s:
    any_posts = await get_posts(max_posts=15, kemo_session=s)
```

### Downloading files

Finally, you can downloads the files of any post, if there is any:
```py
chosen_one = specific_posts[0]

for file in chosen_one.attachments:
    await file.save("./download/", verbose=False)

# You can even download from the post itself
await chosen_one.save("/download/*", verbose=True)
```
> ***Note:** Use `verbose=True` to see the fancy progress bars.*

### Login into an Account

Pykemo supports an interface that allows you to login into your account. It automatically uses
a dedicated session inside to persist your session key:
```py
import asyncio
import os
from pykemo.general import login

async def main():
    async with await login(os.environ["username"],
                           os.environ["password"]) as acc:
        creator = await acc.get_creator("fanbox", "2658856")
        post = await creator.get_post("9441683")

        await post.save("./path/to/download/*")

asyncio.run(main())
```

<hr style="height:3px; width:50%" />

# Dependencies

The [dependencies](./requirements.txt) are as follows:

| Name | Version | Rationale |
| :-: | :-: | :-: |
| [aiohttp](https://pypi.org/project/aiohttp/) | 3.11.13 | For doing asynchronous HTTP requests. |
| [tqdm](https://pypi.org/project/tqdm/) | 4.66.4 | QoL library for showing fancy loading bars in downloads. |

<hr style="height:3px; width:50%" />

# Documentation

All the docs for every version of pykemo are [here](https://pykemo.readthedocs.io/en/latest/).

<hr style="height:3px; width:50%" />

# How to Install

> Please note that you may still need to install the [dependencies](#dependencies) separately beforehand. Pykemo needs them to properly function.

## Using wheels

You may visit the latest [release](https://github.com/ssilentOne/pykemo/releases/latest) and
download the wheel (`*.whl`) file. <br/>
Then, you can install it with `pip` like any other package:
```console
$ pip install pykemo-0.6.2-py3-none-any.whl
```

## From source
If you prefer nightly instances, you may also download this repo as a source and install that to
have the latest versions _(it may not be stable)_.
And even, supposing you have `git`installed, you can download and install from the URL:
```console
$ pip install git+https://github.com/ssilentOne/pykemo.git
```

<br/>
