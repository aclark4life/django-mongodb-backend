===
FAQ
===

This page contains a list of some frequently asked questions.

Performance
===========

Querying across relational fields like :class:`~django.db.models.ForeignKey` and :class:`~django.db.models.ManyToManyField` is really slow. Is there a way to improve the speed of these joins?
-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

Not really. Joins use MongoDB's :doc:`$lookup
<manual:reference/operator/aggregation/lookup>` operator, which doesn't perform
well with large tables.

The best practice for modeling relational data in MongoDB is to instead use
:doc:`embedded models <topics/embedded-models>`.

Troubleshooting
===============

Debug logging
-------------

To troubleshoot MongoDB connectivity issues, you can enable :doc:`PyMongo's
logging <pymongo:examples/logging>` using :doc:`Django's LOGGING setting
<django:topics/logging>`.

This is a minimal :setting:`LOGGING` setting that enables PyMongo's ``DEBUG``
logging::

    LOGGING = {
        "version": 1,
        "disable_existing_loggers": False,
        "handlers": {
            "console": {
                "class": "logging.StreamHandler",
            },
        },
        "loggers": {
            "pymongo": {
                "handlers": ["console"],
                "level": "DEBUG",
            },
        },
    }

``dumpdata`` fails with ``CommandError: Unable to serialize database``
----------------------------------------------------------------------

If running ``manage.py dumpdata`` results in ``CommandError: Unable to
serialize database: 'EmbeddedModelManager' object has no attribute using'``,
see :ref:`configuring-database-routers-setting`.

.. _queryable-encryption:

Queryable Encryption
====================

What about client side configuration?
-------------------------------------

In the :doc:`Queryable Encryption how-to guide <howto/queryable-encryption>`,
server side Queryable Encryption configuration is covered.

Client side Queryable Encryption configuration requires that the entire schema
for encrypted fields is known at the time of client connection.

Schema Map
~~~~~~~~~~

In addition to the
:ref:`settings described in the how-to guide <server-side-queryable-encryption-settings>`,
you will need to provide a ``schema_map`` to the ``AutoEncryptionOpts``.

Fortunately, this is easy to do with Django MongoDB Backend. You can use
the ``showfieldsmap`` management command to generate the schema map
for your encrypted fields, and then use the results in your settings.

To generate the schema map, run the following command in your Django project:
::

    python manage.py showfieldsmap

.. note:: The ``showfieldsmap`` command is only available if you have the
    ``django_mongodb_backend`` app included in the :setting:`INSTALLED_APPS`
    setting.

Settings
~~~~~~~~

Now include the generated schema map in your Django settings.

::

    …
    DATABASES["encrypted"] = {
        …
        "OPTIONS": {
            "auto_encryption_opts": AutoEncryptionOpts(
                …
                schema_map= {
                    "encryption__patientrecord": {
                        "fields": [
                            {
                                "bsonType": "string",
                                "path": "ssn",
                                "queries": {"queryType": "equality"},
                                "keyId": Binary(b"\x14F\x89\xde\x8d\x04K7\xa9\x9a\xaf_\xca\x8a\xfb&", 4),
                            },
                        }
                    },
                    # Add other models with encrypted fields here
                },
            ),
            …
        },
        …
    }

You are now ready to use client side :doc:`Queryable Encryption </topics/queryable-encryption>` in your Django project.
