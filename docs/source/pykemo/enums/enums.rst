Enums Reference
===============

Services
--------

The special :py:class:`enum.Enum` for dealing with services.

.. autoclass:: pykemo.services.services_enum.ServiceType
    :members:
    :show-inheritance:


API Versions
------------

The internal API "versions" to use in the endponts.

The endpoints require to append strings like ``"/v1"`` or ``"/v2"`` before the endpoint, and
this enum can be used to abstract that part on many of the relevant functions.

.. autoclass:: pykemo.core.api_version.APIVersion
    :members:
    :show-inheritance:


URLs
----

When dealing with the URLs of types.

.. autoclass:: pykemo.core.urltypes.UrlType
    :members:
    :show-inheritance:


Account Roles
-------------

The clearance rank a specific account has.

.. autoclass:: pykemo.accounts.role.AccountRole
    :members:
    :show-inheritance:


Creator Link Request Status
---------------------------

The current status of a creator link request.

.. autoclass:: pykemo.moderation.requests.creator_lnk_status.CreatorLinkStatus
    :members:
    :show-inheritance:
