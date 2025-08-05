from bson import json_util
from django.apps import apps
from django.core.management.base import BaseCommand
from django.db import DEFAULT_DB_ALIAS, connections, router
from pymongo.encryption import ClientEncryption

from django_mongodb_backend.fields import has_encrypted_fields


class Command(BaseCommand):
    help = "Generate an `encrypted_fields_map` of encrypted fields for all encrypted"
    " models in the database for use with `AutoEncryptionOpts` in"
    " client configuration."

    def add_arguments(self, parser):
        parser.add_argument(
            "--database",
            default=DEFAULT_DB_ALIAS,
            help="Specify the database to use for generating the encrypted"
            "fields map. Defaults to the 'default' database.",
        )

    def handle(self, *args, **options):
        db = options["database"]
        connection = connections[db]
        encrypted_fields_map = {}
        for app_config in apps.get_app_configs():
            for model in app_config.get_models():
                db_table = model._meta.db_table
                if has_encrypted_fields(model):
                    fields = connection.schema_editor()._get_encrypted_fields_map(model)
                    client = connection.connection
                    ae = client._options.auto_encryption_opts
                    ce = ClientEncryption(
                        ae._kms_providers,
                        ae._key_vault_namespace,
                        client,
                        client.codec_options,
                    )
                    kms_provider = router.kms_provider(model)
                    master_key = connection.settings_dict.get("KMS_CREDENTIALS").get(kms_provider)
                    for field in fields["fields"]:
                        key_alt_name = f"{db_table}_{field['path']}"
                        data_key = ce.create_data_key(
                            kms_provider=kms_provider,
                            master_key=master_key,
                            key_alt_names=[key_alt_name],
                        )
                        field["keyId"] = data_key
                        field["keyAltName"] = key_alt_name
                    encrypted_fields_map[db_table] = fields
        self.stdout.write(json_util.dumps(encrypted_fields_map, indent=2))
