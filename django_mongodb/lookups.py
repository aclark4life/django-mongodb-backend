from django.db import NotSupportedError
from django.db.models.fields.related_lookups import In, MultiColSource, RelatedIn
from django.db.models.lookups import BuiltinLookup, IsNull, PatternLookup, UUIDTextMixin

from .query_utils import process_lhs, process_rhs


def builtin_lookup(self, compiler, connection):
    lhs_mql = process_lhs(self, compiler, connection)
    value = process_rhs(self, compiler, connection)
    return connection.mongo_operators[self.lookup_name](lhs_mql, value)


def in_(self, compiler, connection):
    if isinstance(self.lhs, MultiColSource):
        raise NotImplementedError("MultiColSource is not supported.")
    return builtin_lookup(self, compiler, connection)


def is_null(self, compiler, connection):
    if not isinstance(self.rhs, bool):
        raise ValueError("The QuerySet value for an isnull lookup must be True or False.")
    lhs_mql = process_lhs(self, compiler, connection)
    return connection.mongo_operators["isnull"](lhs_mql, self.rhs)


def pattern_lookup_prep_lookup_value(self, value):
    if hasattr(self.rhs, "as_mql"):
        # If value is a column reference, escape regex special characters.
        # Analogous to PatternLookup.get_rhs_op() / pattern_esc.
        for find, replacement in (("\\", r"\\"), ("%", r"\%"), ("_", r"\_")):
            value = {"$replaceAll": {"input": value, "find": find, "replacement": replacement}}
    else:
        # If value is a literal, remove percent signs added by
        # PatternLookup.process_rhs() for LIKE queries.
        if self.lookup_name in ("startswith", "istartswith"):
            value = value[:-1]
        elif self.lookup_name in ("endswith", "iendswith"):
            value = value[1:]
        elif self.lookup_name in ("contains", "icontains"):
            value = value[1:-1]
    return value


def uuid_text_mixin(self, compiler, connection):  # noqa: ARG001
    raise NotSupportedError("Pattern lookups on UUIDField are not supported.")


def register_lookups():
    BuiltinLookup.as_mql = builtin_lookup
    In.as_mql = RelatedIn.as_mql = in_
    IsNull.as_mql = is_null
    PatternLookup.prep_lookup_value_mongo = pattern_lookup_prep_lookup_value
    UUIDTextMixin.as_mql = uuid_text_mixin
