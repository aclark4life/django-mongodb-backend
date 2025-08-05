================================
Configuring Queryable Encryption
================================

Configuring Queryable Encryption in Django is similar to
:doc:`manual:core/queryable-encryption/quick-start` but with some additional
steps required for Django.

.. admonition:: Server-side Queryable Encryption

   This section describes how to configure server side Queryable
   Encryption in Django. For configuration of client side Queryable Encryption,
   please refer to this :ref:`FAQ question <queryable-encryption>`.

Prerequisites
-------------

In addition to :doc:`installing </intro/install>` and
:doc:`configuring </intro/configure>` Django MongoDB Backend,
you will need to install PyMongo with Queryable Encryption support::

    pip install django-mongodb-backend[encryption]

.. admonition:: Queryable Encryption Compatibility

   You can use Queryable Encryption on a MongoDB 7.0 or later replica
   set or sharded cluster, but not a standalone instance.
   :ref:`This table <manual:qe-compatibility-reference>` shows which MongoDB
   server products support which Queryable Encryption mechanisms.

.. _server-side-queryable-encryption-settings:

Settings
--------

Queryable Encryption in Django requires the use of an additional encrypted
database and Key Management Service (KMS) credentials as well as an encrypted
database router. Here's how to set it up in your Django settings.

::

    from django_mongodb_backend import parse_uri
    from pymongo.encryption_options import AutoEncryptionOpts

    DATABASES = {
        "default": parse_uri(
            DATABASE_URL,
            db_name="my_database",
        ),
    }

    DATABASES["encrypted"] = {
        "ENGINE": "django_mongodb_backend",
        "NAME": "my_encrypted_database",
        "OPTIONS": {
            "auto_encryption_opts": AutoEncryptionOpts(
                key_vault_namespace="my_encrypted_database.keyvault",
                kms_providers={"local": {"key": os.urandom(96)}},
            ),
            "directConnection": True,
        },
        "KMS_PROVIDERS": {},
        "KMS_CREDENTIALS": {},
    }

    class EncryptedRouter:
        def allow_migrate(self, db, app_label, model_name=None, **hints):
            # The encryption_ app's models are only created in the encrypted database.
            if app_label == "encryption_":
                return db == "encrypted"
            # Don't create other app's models in the encrypted database.
            if db == "encrypted":
                return False
            return None

        def kms_provider(self, model, **hints):
            return "local"

    DATABASE_ROUTERS = [EncryptedRouter()]

You are now ready to use server side :doc:`Queryable Encryption
</topics/queryable-encryption>` in your Django project.
