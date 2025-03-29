Accounts Reference
==================

The accounts interface provides a way to login, register and modify user specific data
with the Kemono API.

Account Types
-------------

The types of different accounts, by rank.

.. autoclass:: pykemo.accounts.kinds.cons.Consumer
    :members:
    :inherited-members:
    :exclude-members: from_dict


.. autoclass:: pykemo.accounts.kinds.mod.Moderator
    :members:
    :inherited-members:
    :exclude-members: from_dict


.. autoclass:: pykemo.accounts.kinds.admin.Admin
    :members:
    :inherited-members:
    :exclude-members: from_dict


Account View
------------

A simplified view of an account, purely for seeing basic data.

.. autoclass:: pykemo.accounts.view.AccountView
    :members:
    :exclude-members: from_dict