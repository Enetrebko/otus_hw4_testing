import unittest
import api
from tests.testutils import cases
from datetime import datetime, timedelta


class TestFields(unittest.TestCase):
    @cases(
        [
            [True, True, 3],
            [True, True, {3}],
            [True, True, [3]],
            [True, False, None]
        ]
    )
    def test_charfield_invalid(self, case):
        required, nullable, value = case
        with self.assertRaises(ValueError):
            field = api.CharField(required=required, nullable=nullable)
            field.__set__(field, value)

    @cases(
        [
            [True, True, '3'],
            [True, True, ''],
        ]
    )
    def test_charfield_valid(self, case):
        required, nullable, value = case
        field = api.CharField(required=required, nullable=nullable)
        field.__set__(field, value)
        self.assertEqual(field.value, value)

    @cases(
        [
            [True, True, 3],
            [True, True, [3]],
            [True, False, None]

        ]
    )
    def test_argumentsfield_invalid(self, case):
        required, nullable, value = case
        with self.assertRaises(ValueError):
            field = api.ArgumentsField(required=required, nullable=nullable)
            field.__set__(field, value)

    @cases(
        [
            [True, True, {'key': '3'}]
        ]
    )
    def test_argumentsfield_valid(self, case):
        required, nullable, value = case
        field = api.ArgumentsField(required=required, nullable=nullable)
        field.__set__(field, value)
        self.assertEqual(field.value, value)

    @cases(
        [
            [True, True, 3],
            [True, True, '3'],
            [True, False, None]
        ]
    )
    def test_emailfield_invalid(self, case):
        required, nullable, value = case
        with self.assertRaises(ValueError):
            field = api.EmailField(required=required, nullable=nullable)
            field.__set__(field, value)

    @cases(
        [
            [True, True, '@']
        ]
    )
    def test_emailfield_valid(self, case):
        required, nullable, value = case
        field = api.EmailField(required=required, nullable=nullable)
        field.__set__(field, value)
        self.assertEqual(field.value, value)

    @cases(
        [
            [True, True, 3],
            [True, True, '3'],
            [True, False, None]
        ]
    )
    def test_phonefield_invalid(self, case):
        required, nullable, value = case
        with self.assertRaises(ValueError):
            field = api.PhoneField(required=required, nullable=nullable)
            field.__set__(field, value)

    @cases(
        [
            [True, True, '71111111111'],
            [True, True, 71111111111],
        ]
    )
    def test_phonefield_valid(self, case):
        required, nullable, value = case
        field = api.PhoneField(required=required, nullable=nullable)
        field.__set__(field, value)
        self.assertEqual(field.value, value)

    @cases(
        [
            [True, True, '2020.08.23'],
            [True, True, '2020.08.32'],
            [True, True, '08.23.2020'],
            [True, True, 3],
            [True, True, 'aaa'],
            [True, False, None]
        ]
    )
    def test_datefield_invalid(self, case):
        required, nullable, value = case
        with self.assertRaises(ValueError):
            field = api.DateField(required=required, nullable=nullable)
            field.__set__(field, value)

    @cases(
        [
            [True, True, '23.08.2020']
        ]
    )
    def test_datefield_valid(self, case):
        required, nullable, value = case
        field = api.DateField(required=required, nullable=nullable)
        field.__set__(field, value)
        self.assertEqual(field.value, value)


    @cases(
        [
            [True, True, '2020.08.23'],
            [True, True, '2020.08.32'],
            [True, True, '08.23.2020'],
            [True, True, 3],
            [True, True, 'aaa'],
            [True, False, None]
        ]
    )
    def test_birthdayfield_invalid(self, case):
        required, nullable, value = case
        with self.assertRaises(ValueError):
            field = api.BirthDayField(required=required, nullable=nullable)
            field.__set__(field, value)

    def test_too_old_for_this_shit(self):
        value = (datetime.now() - timedelta(365 * 70 + 1)).strftime('%d.%m.%Y')
        with self.assertRaises(ValueError):
            field = api.BirthDayField()
            field.__set__(field, value)

    @cases(
        [
            [True, True, '23.08.2020']
        ]
    )
    def test_birthdayfield_valid(self, case):
        required, nullable, value = case
        field = api.BirthDayField(required=required, nullable=nullable)
        field.__set__(field, value)
        self.assertEqual(field.value, value)

    @cases(
        [
            [True, True, 3],
            [True, True, {1}],
            [True, True, [1]],
            [True, True, '1'],
            [True, False, None]
        ]
    )
    def test_genderfield_invalid(self, case):
        required, nullable, value = case
        with self.assertRaises(ValueError):
            field = api.GenderField(required=required, nullable=nullable)
            field.__set__(field, value)

    @cases(
        [
            [True, True, 0],
            [True, True, 1],
            [True, True, 2],
            [False, True, None]
        ]
    )
    def test_genderfield_valid(self, case):
        required, nullable, value = case
        field = api.GenderField(required=required, nullable=nullable)
        field.__set__(field, value)
        self.assertEqual(field.value, value)

    @cases(
        [
            [True, True, []],
            [True, True, ['3']],
            [True, True, {3}],
            [True, True, [1, '1']],
            [True, False, None]
        ]
    )
    def test_clientidsfield_invalid(self, case):
        required, nullable, value = case
        with self.assertRaises(ValueError):
            field = api.ClientIDsField(required=required, nullable=nullable)
            field.__set__(field, value)

    @cases(
        [
            [True, True, [1]]
        ]
    )
    def test_clientidsfield_valid(self, case):
        required, nullable, value = case
        field = api.ClientIDsField(required=required, nullable=nullable)
        field.__set__(field, value)
        self.assertEqual(field.value, value)
