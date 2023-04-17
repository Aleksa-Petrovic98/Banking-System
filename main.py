import itertools
import numbers

from TimeZone import TimeZone
from datetime import datetime
from collections import namedtuple

import unittest

Confirmation = namedtuple('Confirmation', 'account_number transaction_code transaction_id time_utc time')


class Account:
    account_numbers = {}
    last_account_number = 0
    _monthly_interest_rate = 0.05

    transaction_counter = itertools.count(100)

    _transaction_types = {
        'deposit': 'D',
        'withdraw': 'W',
        'declined': 'X',
        'balance': 'B'
    }

    def __init__(self, first_name, last_name, balance=0, timezone=None):

        self._account_number = Account.last_account_number + 1
        Account.last_account_number += 1

        self._first_name = first_name
        self._last_name = last_name
        self._balance = balance

        if timezone is None:
            timezone = TimeZone('UTC', 0, 0)
        self._timezone = timezone

    # Getters and Setters

    # Account number only getter, should be set in __init__

    @property
    def account_number(self):
        return self._account_number

    @property
    def first_name(self):
        return self._first_name

    @first_name.setter
    def first_name(self, new_name):
        self.first_name = Account.validate_name(new_name, 'First Name')

    @property
    def last_name(self):
        return self._last_name

    @last_name.setter
    def last_name(self, new_name):
        self.last_name = Account.validate_name(new_name, 'First Name')

    @staticmethod
    def validate_name(name, field_title):
        if name is None or len(str(name).strip()) == 0:
            raise ValueError(f'{field_title} cannot be empty')
        return str(name).strip()

    # Time Zone Offset
    @property
    def timezone(self):
        return self._timezone

    @timezone.setter
    def timezone(self, value):
        if not isinstance(value, TimeZone):
            raise ValueError("Must be valid timezone")
        self._timezone = value

    def generate_confirmation(self, transaction_type):
        pass

    @property
    def balance(self):
        return self._balance

    @classmethod
    def get_interest_rate(cls):
        return cls._monthly_interest_rate

    @classmethod
    def set_interest_rate(cls, value):
        if not isinstance(value, numbers.Real):
            raise ValueError('Interest Rate must be a Real Nnumbers')

        if value < 0:
            raise ValueError("Interest Rate cannot be negative")
        cls._monthly_interest_rate = value

    # Functions

    def make_transaction(self):
        return self.generate_confirmation_code('dummy')

    def deposit(self, amount):
        if not isinstance(amount, numbers.Real):
            raise ValueError("Deposit value must be a real number.")
        if amount <= 0:
            raise ValueError("Deposit cannot be negative")

        transaction_code = self._transaction_types['deposit']

        conf_code = self.generate_confirmation_code(transaction_code)

        self._balance += amount

        return conf_code

    def withdraw(self, amount):
        accepted = False
        if self.balance - amount < 0:
            # insufficient funds - we'll reject this transaction
            transaction_code = Account._transaction_types['rejected']
        else:
            transaction_code = Account._transaction_types['withdraw']
            accepted = True

        conf_code = self.generate_confirmation_code(transaction_code)

        # Doing this here in case there's a problem generating a confirmation code
        # - do not want to modify the balance if we cannot generate a transaction code successfully
        if accepted:
            self._balance -= amount

        return conf_code

    def add_interest(self):
        self._balance = self._balance + self._balance * Account._monthly_interest_rate
        return self._balance

    def generate_confirmation_code(self, transaction_type):
        dt_str = datetime.utcnow().strftime('%Y%m%d%H%M%S')
        return f'{transaction_type}-{self._account_number}-{dt_str}-{next(Account.transaction_counter)}'

    def __str__(self):
        return f'{self.first_name} {self.last_name} balance: {self._balance} account number: {self._account_number}'

    @staticmethod
    def parse_confirmation_code(confirmation_code, preferred_time_zone=None):
        # dummy-A100-20190303032020-101
        split_confirmation_code = confirmation_code.split('-')

        if len(split_confirmation_code) != 4:
            raise ValueError("Invalid confiramtion code")

        transaction_code, account_number, raw_dt_utc, transaction_id = split_confirmation_code

        if preferred_time_zone is None:
            preferred_time_zone = TimeZone('UTC', 0, 0)

        try:
            dt_utc = datetime.strptime(raw_dt_utc, '%Y%m%d%H%M%S')

        except ValueError as ex:
            raise ValueError("Invalid transaction datetime")

        dt_preferred = dt_utc + preferred_time_zone.offset
        dt_preferred_str = f"{dt_preferred.strftime('%Y-%m-%d %H: %M: %S')} ({preferred_time_zone.name})"

        return Confirmation(account_number, transaction_code, transaction_id, dt_utc.isoformat(), dt_preferred_str)


a = Account("John", "Clease", 100)

print(Account.get_interest_rate())



def run_tests(test_class):
    suite = unittest.TestLoader().loadTestsFromTestCase(test_class)
    runner = unittest.TextTestRunner(verbosity=2)
    runner.run(suite)


class TestAccount(unittest.TestCase):

    def test_create_timezone(self):
        tz = TimeZone('ABC', -1, -30)
        self.assertEqual('ABC', tz.name)
        self.assertEqual(timedelta(hours=-1, minutes=-30), tz.offset)

    def test_timezones_equal(self):
        tz1 = TimeZone('ABC', -1, -30)
        tz2 = TimeZone('ABC', -1, -30)
        self.assertEqual(tz1, tz2)

    def test_timezones_not_equal(self):
        tz = TimeZone('ABC', -1, -30)

        test_timezones = (
            TimeZone('DEF', -1, -30),
            TimeZone('ABC', -1, 0),
            TimeZone('ABC', 1, -30)
        )
        for i, test_tz in enumerate(test_timezones):
            with self.subTest(test_number=i):
                self.assertNotEqual(tz, test_tz)

    def test_create_account(self):
        account_number = 'A100'
        first_name = 'FIRST'
        last_name = 'LAST'
        tz = TimeZone('TZ', 1, 30)
        balance = 100.00

        a = Account(account_number, first_name, last_name, tz, balance)
        self.assertEqual(account_number, a.account_number)
        self.assertEqual(first_name, a.first_name)
        self.assertEqual(last_name, a.last_name)
        self.assertEqual(first_name + ' ' + last_name, a.full_name)
        self.assertEqual(tz, a.timezone)
        self.assertEqual(balance, a.balance)

    def test_create_account_blank_first_name(self):
        account_number = 'A100'
        first_name = ''
        last_name = 'LAST'
        tz = TimeZone('TZ', 1, 30)
        balance = 100.00

        with self.assertRaises(ValueError):
            a = Account(account_number, first_name, last_name, tz, balance)

    def test_create_account_negative_balance(self):
        account_number = 'A100'
        first_name = 'FIRST'
        last_name = 'LAST'
        tz = TimeZone('TZ', 1, 30)
        balance = -100.00

        with self.assertRaises(ValueError):
            a = Account(account_number, first_name, last_name, tz, balance)

    def test_account_deposit_ok(self):
        account_number = 'A100'
        first_name = 'FIRST'
        last_name = 'LAST'
        balance = 100.00

        a = Account(account_number, first_name, last_name, initial_balance=balance)
        conf_code = a.deposit(100)
        self.assertEqual(200, a.balance)
        self.assertIn('D-', conf_code)

    def test_account_deposit_negative_amount(self):
        account_number = 'A100'
        first_name = 'FIRST'
        last_name = 'LAST'
        balance = 100.00

        a = Account(account_number, first_name, last_name, initial_balance=balance)
        with self.assertRaises(ValueError):
            conf_code = a.deposit(-100)

    def test_account_withdraw_ok(self):
        account_number = 'A100'
        first_name = 'FIRST'
        last_name = 'LAST'
        balance = 100.00

        a = Account(account_number, first_name, last_name, initial_balance=balance)
        conf_code = a.withdraw(20)
        self.assertEqual(80, a.balance)
        self.assertIn('W-', conf_code)

    def test_account_withdraw_overdraw(self):
        account_number = 'A100'
        first_name = 'FIRST'
        last_name = 'LAST'
        balance = 100.00

        a = Account(account_number, first_name, last_name, initial_balance=balance)
        conf_code = a.withdraw(200)
        self.assertIn('X-', conf_code)
        self.assertEqual(balance, a.balance)

run_tests(TestAccount)

