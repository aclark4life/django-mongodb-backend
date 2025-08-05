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
                # "keyId": Binary(b" \x901\x89\x1f\xafAX\x9b*\xb1\xc7\xc5\xfdl\xa4", 4),
            },
            {
                "bsonType": "long",
                "path": "cc_number",
                "queries": {"queryType": "equality"},
                # "keyId": Binary(b"\x97\xb4\x9d\xb8\xd5\xa6Ay\x85\xfe\x00\xc0\xd4{\xa2\xff", 4),
            },
            {
                "bsonType": "decimal",
                "path": "account_balance",
                "queries": {"queryType": "range"},
                # "keyId": Binary(b"\xcc\x01-s\xea\xd9B\x8d\x80\xd7\xf8!n\xc6\xf5U", 4),
            },
        ]
    },
    "encryption__patientrecord": {
        "fields": [
            {
                "bsonType": "string",
                "path": "ssn",
                "queries": {"queryType": "equality"},
                # "keyId": Binary(b"\x14F\x89\xde\x8d\x04K7\xa9\x9a\xaf_\xca\x8a\xfb&", 4),
            },
            {
                "bsonType": "date",
                "path": "birth_date",
                "queries": {"queryType": "range"},
                # "keyId": Binary(b"@\xdd\xb4\xd2%\xc2B\x94\xb5\x07\xbc(ER[s", 4),
            },
            {
                "bsonType": "binData",
                "path": "profile_picture",
                "queries": {"queryType": "equality"},
                # "keyId": Binary(b"Q\xa2\xebc!\xecD,\x8b\xe4$\xb6ul9\x9a", 4),
            },
            {
                "bsonType": "int",
                "path": "patient_age",
                "queries": {"queryType": "range"},
                # "keyId": Binary(b"\ro\x80\x1e\x8e1K\xde\xbc_\xc3bi\x95\xa6j", 4),
            },
            {
                "bsonType": "double",
                "path": "weight",
                "queries": {"queryType": "range"},
                # "keyId": Binary(b"\x9b\xfd:n\xe1\xd0N\xdd\xb3\xe7e)\x06\xea\x8a\x1d", 4),
            },
        ]
    },
    "encryption__patient": {
        "fields": [
            {
                "bsonType": "int",
                "path": "patient_id",
                "queries": {"queryType": "equality"},
                # "keyId": Binary(b"\x8ft\x16:\x8a\x91D\xc7\x8a\xdf\xe5O\n[\xfd\\", 4),
            },
            {
                "bsonType": "string",
                "path": "patient_name",
                # "keyId": Binary(b"<\x9b\xba\xeb:\xa4@m\x93\x0e\x0c\xcaN\x03\xfb\x05", 4),
            },
            {
                "bsonType": "string",
                "path": "patient_notes",
                "queries": {"queryType": "equality"},
                # "keyId": Binary(b"\x01\xe7\xd1isnB$\xa9(gwO\xca\x10\xbd", 4),
            },
            {
                "bsonType": "date",
                "path": "registration_date",
                "queries": {"queryType": "equality"},
                # "keyId": Binary(b"F\xfb\xae\x82\xd5\x9a@\xee\xbfJ\xaf#\x9c:-I", 4),
            },
            {
                "bsonType": "bool",
                "path": "is_active",
                "queries": {"queryType": "equality"},
                # "keyId": Binary(b"\xb2\xb5\xc4K53A\xda\xb9V\xa6\xa9\x97\x94\xea;", 4),
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

    def test_show_schema_map(self):
        self.maxDiff = None
        out = StringIO()
        call_command(
            "showfieldsmap",
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
