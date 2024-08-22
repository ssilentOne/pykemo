
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

Python library binding to the [Kemono API](https://kemono.su/api/schema).

<br/>
<br/>
<br/>

It has the following features:

* **All HTTP requests logic abstracted behind Python  types.** You can interact with the API
using custom classes like `Creator` or `Post`.
    - _This means that for downloading files there is already an interface_ (`File`) _for that._

* **OS Independent.** Being pure-python, the library works on Windows, MacOS and Linux alike.

* **Asynchronous request for performance boosts.** Though it's recommended to use along a session
cookie, to get around the server's DDOS issues.

* **Ready to install.** Rather than installing from source, the [releases](https://github.com/ssilentOne/pykemo/releases)
have each its own wheels to distribute at your leisure.

<hr style="height:1px; width:35%" />

* [Examples](#examples)
* [Dependencies](#dependencies)
* [Documentation](#documentation)
* [How to Install](#how-to-install)

<hr style="height:1px; width:35%" />

# Examples

### Retrieving a creator

You can create a `Creator` instance like so:

```py
from pykemo import get_creator, ServiceType

creator_id = "2658856"

creator = get_creator(ServiceType.FANBOX, creator_id)

# This works as well
creator2 = get_creator("fanbox", creator_id)

print(creator)
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
last_posts = creator.posts(max_posts=5)

# Every post from June 15th to July 23rd
before = datetime(year=2024, month=7, day=23)
since = datetime(year=2024, month=6, day=15)
specific_posts = creator.posts(before=before, since=since)

for post in specific_posts:
    print(post)
```
And it will show:
```
Post(id='8104634', creator_id='2658856', service='fanbox', title='獅●ぼ●ん（気高いメスライオンが枕●業Vtuber）')
Post(id='8101402', creator_id='2658856', service='fanbox', title='大●ス●ル（おっπ見せてほしいとお願いしたらVtuber線画）')
Post(id='8100642', creator_id='2658856', service='fanbox', title='【閲覧注意】湊●く●（目の前で寝取られるVtuber線画）')
Post(id='8100373', creator_id='2658856', service='fanbox', title='湊●く●（お料理中に襲われてVtuber線画）')
...
```

_Alternatively,_ you can also use the helper function `get_posts()`, which has the same parameters,
for a search of all the recent posts of every creator.
```py
from pykemo import get_posts()

any_posts = get_posts(max_posts=15)
```

### Downloading files

Finally, you can downloads the files of any post, if there is any:
```py
chosen_one = specific_posts[0]

for file in chosen_one.attachments:
    file.save("./download/", verbose=False)

# You can even download from the post itself
chosen_one.save("/download/*", verbose=True)
```
***Note:** Use `verbose=True` to see the fancy progress bars.*

<hr style="height:3px; width:50%" />

# Dependencies

The [dependencies](./requirements.txt) are as follows:

| Name | Version | Rationale |
| :-: | :-: | :-: |
| [grequests](https://pypi.org/project/grequests/) | 0.7.0 | For doing the asynchronous requests. |
| [requests](https://pypi.org/project/requests/) | 2.32.3 | The base library for doing HTTP requests. |
| [tqdm](https://pypi.org/project/tqdm/) | 4.66.4 | QoL library for showing fancy loading bars in downloads. |

<hr style="height:3px; width:50%" />

# Documentation

All the docs for every version of pykemo are hosted on **ReadTheDocs**:

* link: https://pykemo.readthedocs.io/en/latest/

<hr style="height:3px; width:50%" />

# How to Install

## Using wheels

You may visit the latest [release](https://github.com/ssilentOne/pykemo/releases/latest) and
download the wheel (`*.whl`) file. <br/>
Then, you can install it with `pip` like any other package:
```console
$ pip install pykemo-0.5.1-py3-none-any.whl
```

## From source
You may download this repo as a source and install that. And even, supposing you have `git`
installed, you can download and install from the URL:
```console
$ pip install git+https://github.com/ssilentOne/pykemo.git
```

<br/>
