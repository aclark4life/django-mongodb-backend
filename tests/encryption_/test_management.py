from io import StringIO

from bson import json_util
from django.core.management import call_command
from django.test import TransactionTestCase, modify_settings, override_settings

from .routers import TestEncryptedRouter

EXPECTED_ENCRYPTED_FIELDS_MAP = {
    "encryption__billing": {
        "fields": [
            {
                "bsonType": "string",
                "path": "cc_type",
                "queries": {"queryType": "equality"},
            },
            {
                "bsonType": "long",
                "path": "cc_number",
                "queries": {"queryType": "equality"},
            },
            {
                "bsonType": "decimal",
                "path": "account_balance",
                "queries": {"queryType": "range"},
            },
        ]
    },
    "encryption__patientrecord": {
        "fields": [
            {
                "bsonType": "string",
                "path": "ssn",
                "queries": {"queryType": "equality"},
            },
            {
                "bsonType": "date",
                "path": "birth_date",
                "queries": {"queryType": "range"},
            },
            {
                "bsonType": "binData",
                "path": "profile_picture",
                "queries": {"queryType": "equality"},
            },
            {
                "bsonType": "int",
                "path": "patient_age",
                "queries": {"queryType": "range"},
            },
            {
                "bsonType": "double",
                "path": "weight",
                "queries": {"queryType": "range"},
            },
        ]
    },
    "encryption__patient": {
        "fields": [
            {
                "bsonType": "int",
                "path": "patient_id",
                "queries": {"queryType": "equality"},
            },
            {
                "bsonType": "string",
                "path": "patient_name",
            },
            {
                "bsonType": "string",
                "path": "patient_notes",
                "queries": {"queryType": "equality"},
            },
            {
                "bsonType": "date",
                "path": "registration_date",
                "queries": {"queryType": "equality"},
            },
            {
                "bsonType": "bool",
                "path": "is_active",
                "queries": {"queryType": "equality"},
            },
            {"bsonType": "string", "path": "email", "queries": {"queryType": "equality"}},
        ]
    },
    "encryption__patientportaluser": {
        "fields": [
            {"bsonType": "string", "path": "ip_address", "queries": {"queryType": "equality"}},
            {"bsonType": "string", "path": "url", "queries": {"queryType": "equality"}},
        ]
    },
    "encryption__encryptednumbers": {
        "fields": [
            {"bsonType": "int", "path": "pos_bigint", "queries": {"queryType": "equality"}},
            {"bsonType": "int", "path": "pos_smallint", "queries": {"queryType": "equality"}},
            {"bsonType": "int", "path": "smallint", "queries": {"queryType": "equality"}},
        ]
    },
    "encryption__appointment": {
        "fields": [{"bsonType": "date", "path": "time", "queries": {"queryType": "equality"}}]
    },
}


@modify_settings(
    INSTALLED_APPS={"prepend": "django_mongodb_backend"},
)
@override_settings(DATABASE_ROUTERS=[TestEncryptedRouter()])
class EncryptedFieldTests(TransactionTestCase):
    databases = {"default", "encrypted"}
    available_apps = ["django_mongodb_backend", "encryption_"]

    def test_create_encrypted_fields_map(self):
        self.maxDiff = None
        out = StringIO()
        call_command(
            "createencryptedfieldsmap",
            "--database",
            "encrypted",
            verbosity=0,
            stdout=out,
        )
        # Remove keyIds since they are different for each run.
        output_json = json_util.loads(out.getvalue())
        for table in output_json:
            for field in output_json[table]["fields"]:
                del field["keyId"]
        # TODO: probably we don't need to test the entire mapping, otherwise it
        # requires updates every time a new model or field is added!
        self.assertEqual(EXPECTED_ENCRYPTED_FIELDS_MAP, output_json)
