import itertools
class Account:
    account_numbers = {}
    last_account_number = 0
    monthly_interest_rate = 0.05

    transaction_counter = itertools.count(100)

    _transaction_type = {
        'deposit' : 'D',
        'withdraw' : 'W',
        'declined' : 'X',
        'balance' : 'B'
    }

    def __init__(self, first_name, last_name, time_zone_offset, balance=0):

        self._account_number = Account.last_account_number + 1
        Account.last_account_number += 1

        self._first_name = first_name
        self._last_name = last_name
        self._time_zone_offset = time_zone_offset
        self._balance = balance

    # Getters and Setters

    # Account number only getter, should be set in __init__

    @property
    def account_number(self):
        return self._account_number

    @property
    def first_name(self):
        return self._first_name

    @first_name.setter
    def first_name(self,new_name):
        self.first_name = Account.validate_name(new_name,'First Name')

    @property
    def last_name(self):
        return self._first_name

    @last_name.setter
    def last_name(self, new_name):
        self.last_name = Account.validate_name(new_name,'First Name')

    @staticmethod
    def validate_name(name, field_title):
        if  name is None or len(str(name).strip()) == 0:
            raise ValueError(f'{field_title} cannot be empty')
        return str(name).strip()

    # Time Zone Offset
    @property
    def time_zone_offset(self):
        return self._time_zone_offset

    @time_zone_offset.setter
    def time_zone_offset(self, time_zone_offset):
        self._time_zone_offset = time_zone_offset

    def generate_confirmation(self,transaction_type):


    @property
    def balance(self):
        return self._balance

    # Functions
    @staticmethod
    def make_transaction():
        new_transaction_id = next(Account.transaction_counter)
        return new_transaction_id

    def deposit(self, amount):
        self._balance += amount
        return self._balance

    def withdraw(self, amount):
        if self._balance - amount >= 0:
            self._balance -= amount
            return self._balance
        else:
            return ValueError("Insufficient Funds")

    def add_interest(self):
        self._balance = self._balance + self._balance*Account.monthly_interest_rate
        return self._balance

    def __str__(self):
        return f'{self.first_name} {self.last_name} balance: {self._balance} account number: {self._account_number}'

a = Account("Al","Pe",0,0)
b = Account("Ale","Pr",0,0)
print(a)
print(b)
a.deposit(500)
print(a)
print(a.add_interest())

print(a.withdraw(200))
