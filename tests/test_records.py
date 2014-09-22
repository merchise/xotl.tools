# -*- encoding: utf-8 -*-
#----------------------------------------------------------------------
# test_records
#----------------------------------------------------------------------
# Copyright (c) 2014 Merchise Autrement and Contributors
# All rights reserved.
#
# This is free software; you can redistribute it and/or modify it under the
# terms of the LICENCE attached (see LICENCE file) in the distribution
# package.
#
# Created on 2014-09-22

from __future__ import (division as _py3_division,
                        print_function as _py3_print,
                        unicode_literals as _py3_unicode,
                        absolute_import as _py3_abs_import)


import unittest
from xoutil.records import record, datetime_reader


class _table(record):
    ID = 0
    _id_reader = lambda val: int(val)


class person(_table):
    NAME = 1
    LASTNAME = 2
    BIRTHDATE = 3

    _birthdate_reader = datetime_reader('%Y-%m-%d')

    @property
    def current_age(self):
        from datetime import datetime
        today = datetime.today()
        return self.age_when(today)

    def age_when(self, today):
        res = today - self.birthdate
        return int(res.days//365.25)


class TestRecords(unittest.TestCase):
    def test_records(self):
        from datetime import datetime
        _manu = ('1', 'Manuel', 'Vazquez', '1978-10-21')
        manu = person(_manu)

        self.assertEqual(1, person.get_field(_manu, person.ID))
        self.assertEqual(1, manu.id)
        self.assertEqual(11, manu.age_when(datetime(1989, 10, 21)))
        self.assertEqual(35, manu.age_when(datetime(2014, 9, 22)))

    def test_descriptor(self):
        class INVOICE(record):
            ID = 0
            REFERER = 1

            # The following attribute will be overwritten by the fields
            # descriptor for REFERER.
            referer = 'overwritten'

        assert INVOICE.referer and INVOICE.id
        line = (1, 'MVA.98')
        self.assertEqual(INVOICE.get_field(line, INVOICE.ID), 1)
        invoice = INVOICE(line)
        self.assertEqual(invoice.referer, 'MVA.98')
        self.assertEqual(invoice[INVOICE.REFERER], invoice.referer)

    def test_readers(self):
        from datetime import datetime, timedelta

        class INVOICE(record):
            ID = 0
            REFERER = 1
            CREATED_DATETIME = 2
            UPDATE_DATETIME = 3
            _DATETIME_FORMAT = '%Y-%m-%d %H:%M:%S.%f'

            @staticmethod
            def _created_datetime_reader(value):
                return datetime.strptime(value, INVOICE._DATETIME_FORMAT)

            # implicit staticmethod
            def _update_datetime_reader(value):
                return datetime.strptime(value, INVOICE._DATETIME_FORMAT)

        today = datetime.now()
        yesterday = today - timedelta(days=1)
        tomorrow = today + timedelta(days=1)
        line = (1, 'MVA.98',
                yesterday.strftime(INVOICE._DATETIME_FORMAT),
                tomorrow.strftime(INVOICE._DATETIME_FORMAT))
        self.assertEqual(
            INVOICE.get_field(line, INVOICE.CREATED_DATETIME),
            yesterday
        )
        self.assertEqual(
            INVOICE.get_field(line, INVOICE.UPDATE_DATETIME),
            tomorrow
        )

        invoice = INVOICE(line)
        self.assertEqual(invoice.created_datetime, yesterday)
        self.assertEqual(invoice.update_datetime, tomorrow)
