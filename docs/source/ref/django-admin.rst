===================
Management commands
===================

Django MongoDB Backend includes some :doc:`Django management commands
<django:ref/django-admin>`.

Required configuration
======================

To make these commands available, you must include ``"django_mongodb_backend"``
in the :setting:`INSTALLED_APPS` setting.

Available commands
==================

``createcachecollection``
-------------------------

.. django-admin:: createcachecollection

    Creates the cache collection for use with the :doc:`database cache backend
    </topics/cache>` using the information from your :setting:`CACHES` setting.

    .. django-admin-option:: --database DATABASE

        Specifies the database in which the cache collection(s) will be created.
        Defaults to ``default``.


``createencryptedfieldsmap``
----------------------------

.. django-admin:: createencryptedfieldsmap

    Creates an encrypted fields map that can be used with `encrypted_fields_map`
    in :class:`~pymongo.encryption_options.AutoEncryptionOpts` to configure
    client-side Queryable Encryption.

    .. django-admin-option:: --database DATABASE

        Specifies the database to use.
        Defaults to ``default``.
