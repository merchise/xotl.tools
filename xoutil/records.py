#!/usr/bin/env python
# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Copyright (c) Merchise Autrement [~º/~] and Contributors
# All rights reserved.
#
# This is free software; you can do what the LICENCE file allows you to.
#

'''Records definitions.

A record allows to describe plain external data and a simplified model to
*read* it.  The main use of records is to represent data that is read from a
`CSV  file <305>`:pep:.

See the `record`:class: class to find out how to use it.

'''

from __future__ import (division as _py3_division,
                        print_function as _py3_print,
                        absolute_import as _py3_abs_import)


from xoutil.symbols import Unset
from xoutil.future.functools import lru_cache


@lru_cache()
def field_descriptor(field_name):
    '''Returns a read-only descriptor for `field_name`.'''
    class descriptor:
        def __get__(self, instance, owner):
            if instance:
                return owner.get_field(instance._raw_data,
                                       owner._rec_fields[field_name])
            else:
                return self
    return descriptor


class _record_type(type):
    @staticmethod
    def _is_rec_definition(attr, val=Unset):
        result = not attr.startswith('_') and attr.upper() == attr
        if val is not Unset:
            from numbers import Integral
            from xoutil.eight import string_types
            isi = isinstance
            result = result and (isi(val, Integral) or isi(val, string_types))
        return result

    @staticmethod
    def is_reader(attr, func, fields=None):
        from xoutil.future.types import FunctionType
        attr = attr.lower()
        good_name = attr.startswith('_') and attr.endswith('_reader')
        good_type = isinstance(func, (FunctionType, staticmethod))
        return good_name and good_type

    def __new__(cls, name, bases, attrs):
        def static(f):
            return f if isinstance(f, staticmethod) else staticmethod(f)

        cls_fields = {attr: val for attr, val in attrs.items()
                      if cls._is_rec_definition(attr, val)}
        descriptors = {attr.lower(): field_descriptor(attr)()
                       for attr in cls_fields}
        readers = {attr.lower(): static(func) for attr, func in attrs.items()
                   if cls.is_reader(attr, func)}
        new_attrs = dict(attrs, **descriptors)
        new_attrs.update(readers)
        result = super().__new__(cls, name, bases, new_attrs)
        # Make a copy, or else the super-class attribute gets contaminated
        fields = dict(getattr(result, '_rec_fields', {}))
        index = dict(getattr(result, '_rec_index', {}))
        fields.update(cls_fields)
        if len(fields) != len({val for val in fields.values()}):
            msg = ('Duplicated field index definition in class "%s"' % name)
            import logging
            logger = logging.getLogger(__name__)
            logger.error(msg)
            logger.debug(fields)
            raise TypeError(msg)
        result._rec_fields = fields
        index.update({val: attr for attr, val in cls_fields.items()})
        result._rec_index = index
        return result

    def get_field(self, raw_data, field):
        from xoutil.symbols import Undefined
        field_name = self._rec_index[field]
        try:
            value = raw_data[field]
        except (IndexError, KeyError):
            value = Undefined
        reader_name = '_%s_reader' % field_name.lower()
        reader = getattr(self, reader_name, None)
        if reader:
            return reader(value)
        else:
            return value


class record(metaclass=_record_type):
    '''Base record class.

    Records allow to represent a sequence or mapping of values extracted from
    external sources into a dict-like Python value.

    The first use-case for this abstraction is importing data from a `CSV file
    <305>`:pep:.  You could represent each line as an instance of a properly
    defined record.

    An instance of a record would represent a single `line` (or row) from the
    external data source.

    Records are expected to declare `fields`.  Each field must be a
    CAPITALIZED valid identifier like::

        >>> class INVOICE(record):
        ...     ID = 0
        ...     REFERENCE = 1

    Fields must be integers or plain strings.  Fields must not begin with an
    underscore ("_").  External data lines are required to support indexes of
    those types.

    You could use either the classmethod `get_field`:func: to get the value of
    field in a single line (data as provided by the external source)::

        >>> line = (1, 'AA20X138874Z012')
        >>> INVOICE.get_field(line, INVOICE.REFERENCE)
        'AA20X138874Z012'

    You may also have an instance::

        >>> invoice = INVOICE(line)
        >>> invoice.reference
        'AA20X138874Z012'

    .. note:: Instances attributes are renamed to lowercase.  So you **must**
       not create any other attribute that has the same name as a field in
       lowercase, or else it will be overwritten.

    You could define `readers` for any field.  For instance if you have a
    "CREATED_DATETIME" field you may create a "_created_datetime_reader"
    function that will be used to parse the raw value of the instance into an
    expected type.  See the `included readers builders below
    <included-readers>`:ref:.

    Readers are always cast as `staticmethods`, whether or not you have
    explicitly stated that fact::

        >>> from dateutil import parser
        >>> class BETTER_INVOICE(INVOICE):
        ...     CREATED_TIME = 2
        ...     _created_time_reader = lambda val: parser.parse(val)

        >>> line = (1, 'AA20X138874Z012', '2014-02-17T17:29:21.965053')
        >>> BETTER_INVOICE.get_field(line, BETTER_INVOICE.CREATED_TIME)
        datetime.datetime(2014, 2, 17, 17, 29, 21, 965053)

    .. warning:: Creating readers for fields defined in super classes is not
       directly supported.  To do so, you **must** declare the reader as a
       staticmethod yourself.

    .. note:: Currently there's no concept of relationship between rows in
       this model.  We are evaluating whether by placing a some sort of
       context into the `kwargs` argument would be possible to write readers
       that fetch other instances.

    '''

    def __init__(self, raw_data):
        self._raw_data = raw_data

    def __repr__(self):
        cls = type(self)
        return '%s(%r)' % (cls.__name__, self._raw_data)

    def __getitem__(self, field_index):
        return type(self).get_field(self._raw_data, field_index)


def isnull(val):
    '''Return True if `val` is null.

    Null values are None, the empty string and any False instance of
    `xoutil.symbols.boolean`:class:.

    Notice that 0, the empty list and other false values in Python are not
    considered null.  This allows that the CSV null (the empty string) is
    correctly treated while other sources that provide numbers (and 0 is a
    valid number) are not misinterpreted as null.

    '''
    from xoutil.symbols import boolean
    return val in (None, '') or (isinstance(val, boolean) and not val)


# Standard readers
def check_nullable(val, nullable):
    '''Check the restriction of nullable.

    Return True if the val is non-null.  If nullable is True and the val is
    null returns False.  If `nullable` is False and `val` is null, raise a
    ValueError.

    Test for null is done with function `isnull`:func:.

    '''
    null = isnull(val)
    if not null or nullable:
        return not null
    else:
        raise ValueError('NULL value was not expected here')


@lru_cache()
def datetime_reader(format, nullable=False, default=None, strict=True):
    '''Returns a datetime reader.

    :param format: The format the datetime is expected to be in the external
       data.  This is passed to `datetime.datetime.strptime`:func:.

    :param strict: Whether to be strict about datetime format.

    The reader works first by passing the value to strict
    `datetime.datetime.strptime`:func: function.  If that fails with a
    ValueError and strict is True the reader fails entirely.

    If strict is False, the worker applies different rules.  First if the
    `dateutil` package is installed its parser module is tried.  If `dateutil`
    is not available and nullable is True, return None; if nullable is False
    and default is not null (as in `isnull`:func:), return `default`,
    otherwise raise a ValueError.

    .. versionadded: 1.6.7  Add the `strict` argument.

    .. versionchanged: 1.6.7.1  Keep the meaning of null when testing for
       `default` if strict is False and dateutil is not available.

    '''
    try:
        from dateutil.parser import parse
    except ImportError:
        parse = None

    def reader(val):
        if check_nullable(val, nullable):
            from datetime import datetime
            try:
                return datetime.strptime(val, format)
            except ValueError:
                if strict:
                    raise
                elif parse:
                    return parse(val)
                else:
                    if nullable:
                        return None
                    elif not isnull(default):
                        return default
                    else:
                        raise ValueError
        else:
            return default
    return reader


@lru_cache()
def date_reader(format, nullable=False, default=None, strict=True):
    '''Return a date reader.

    This is similar to `datetime_reader`:func: but instead of returning a
    `datetime.datetime`:class: it returns a `datetime.date`.

    Actually this function delegates to `datetime_reader`:func: most of its
    functionality.

    .. versionadded: 1.6.8

    '''
    reader = datetime_reader(format, nullable=nullable, default=default,
                             strict=strict)

    def res(val):
        result = reader(val)
        if not isnull(result) and result is not default:
            return result.date()
        else:
            return result
    return res


@lru_cache()
def boolean_reader(true=('1', ), nullable=False, default=None):
    '''Returns a boolean reader.

    :param true: A collection of raw values considered to be True.  Only the
                 values in this collection will be considered True values.

    '''
    def reader(val):
        if check_nullable(val, nullable):
            return val in true
        else:
            return default
    return reader


@lru_cache()
def integer_reader(nullable=False, default=None):
    '''Returns an integer reader.'''
    def reader(val):
        if check_nullable(val, nullable):
            return int(val)
        else:
            return default
    return reader


@lru_cache()
def decimal_reader(nullable=False, default=None):
    '''Returns a Decimal reader.'''
    def reader(val):
        if check_nullable(val, nullable):
            from decimal import Decimal
            return Decimal(val)
        else:
            return default
    return reader


@lru_cache()
def float_reader(nullable=False, default=None):
    '''Returns a float reader.'''
    def reader(val):
        if check_nullable(val, nullable):
            return float(val)
        else:
            return default
    return reader


del lru_cache
