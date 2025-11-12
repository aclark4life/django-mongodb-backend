# Settings for django_mongodb_backend/tests when encryption is supported.
import os

from mongodb_settings import *  # noqa: F403
from pymongo.encryption import AutoEncryptionOpts

os.environ["LD_LIBRARY_PATH"] = os.environ["GITHUB_WORKSPACE"] + "/lib/"

DATABASES["encrypted"] = {  # noqa: F405
    "ENGINE": "django_mongodb_backend",
    "NAME": "djangotests_encrypted",
    "OPTIONS": {
        "auto_encryption_opts": AutoEncryptionOpts(
            key_vault_namespace="djangotests_encrypted.__keyVault",
            kms_providers={"local": {"key": os.urandom(96)}},
            crypt_shared_lib_path=os.environ["GITHUB_WORKSPACE"] + "/lib/mongo_crypt_v1.so",
        ),
        "directConnection": True,
    },
    "KMS_CREDENTIALS": {
        "aws": {
            "kms_provider": {
                "aws": {
                    "accessKeyId": os.environ.get("AWS_ACCESS_KEY_ID"),
                    "secretAccessKey": os.environ.get("AWS_SECRET_ACCESS_KEY"),
                }
            },
            "customer_master_key": {
                "key": os.environ.get("AWS_KEY_ARN"),
                "region": os.environ.get("AWS_KEY_REGION"),
            },
        },
        "azure": {
            "kms_provider": {
                "azure": {
                    "tenantId": os.environ.get("AZURE_TENANT_ID"),
                    "clientId": os.environ.get("AZURE_CLIENT_ID"),
                    "clientSecret": os.environ.get("AZURE_CLIENT_SECRET"),
                }
            },
            "customer_master_key": {
                "keyName": os.environ.get("AZURE_KEY_NAME"),
                "keyVaultEndpoint": os.environ.get("AZURE_KEY_VAULT_ENDPOINT"),
            },
        },
        "gcp": {
            "kms_provider": {
                "gcp": {
                    "email": os.environ.get("GCP_EMAIL"),
                    "privateKey": os.environ.get("GCP_PRIVATE_KEY"),
                }
            },
            "customer_master_key": {
                "projectId": os.environ.get("GCP_PROJECT_ID"),
                "location": os.environ.get("GCP_LOCATION"),
                "keyRing": os.environ.get("GCP_KEY_RING"),
                "keyName": os.environ.get("GCP_KEY_NAME"),
            },
        },
        "kmip": {
            "kms_provider": {"kmip": {"endpoint": os.environ.get("KMIP_KMS_ENDPOINT")}},
            "customer_master_key": {},
            "tls_options": {
                "kmip": {
                    "tlsCAFile": os.environ.get("KMIP_TLS_CA_FILE"),
                    "tlsCertificateKeyFile": os.environ.get("KMIP_TLS_CERT_FILE"),
                }
            },
        },
        "local": {
            "kms_provider": {"local": {"key": os.urandom(96)}},
            "customer_master_key": {},
        },
    },
}


class EncryptedRouter:
    def db_for_read(self, model, **hints):
        if model._meta.app_label == "encryption_":
            return "encrypted"
        return None

    db_for_write = db_for_read

    def allow_migrate(self, db, app_label, model_name=None, **hints):
        # The encryption_ app's models are only created in the encrypted
        # database.
        if app_label == "encryption_":
            return db == "encrypted"
        # Don't create other app's models in the encrypted database.
        if db == "encrypted":
            return False
        return None


DATABASE_ROUTERS.append(EncryptedRouter())  # noqa: F405
