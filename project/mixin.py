from django.core.exceptions import NON_FIELD_ERRORS
from typing import Protocol


class ErrorFormProtocol(Protocol):
    _errors: dict
    error_class: type


class AddErrorMixin:
    def add_error(self: ErrorFormProtocol, field, msg):
        field = field or NON_FIELD_ERRORS
        if field in self._errors:
            self._errors[field].append(msg)
        else:
            self._errors[field] = self.error_class([msg])
