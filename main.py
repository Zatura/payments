import re
import unittest
import uuid

"""
Questions:


    1. Complete the `MiniVenmo.create_user()` method to allow our application to create new users.

    2. Complete the `User.pay()` method to allow users to pay each other. Consider the following: if user A is paying user B, user's A balance should be used if there's enough balance to cover the whole payment, if not, user's A credit card should be charged instead.

    3. Venmo has the Feed functionality, that shows the payments that users have been doing in the app. If Bobby paid Carol $5, and then Carol paid Bobby $15, it should look something like this


    Bobby paid Carol $5.00 for Coffee
    Carol paid Bobby $15.00 for Lunch

    Implement the `User.retrieve_feed()` and `MiniVenmo.render_feed()` methods so the MiniVenmo application can render the feed.

    4. Now users should be able to add friends. Implement the `User.add_friend()` method to allow users to add friends.
    5. Now modify the methods involved in rendering the feed to also show when user's added each other as friends.
"""

"""
MiniVenmo! Imagine that your phone and wallet are trying to have a beautiful
baby. In order to make this happen, you must write a social payment app.
Implement a program that will feature users, credit cards, and payment feeds.
"""


class UsernameException(Exception):
    pass


class PaymentException(Exception):
    pass


class CreditCardException(Exception):
    pass


class User:
    def __init__(self, username: str):
        self.credit_card_number = None
        self.balance = 0.0
        self.feed = []

        if self._is_valid_username(username):
            self.username = username
        else:
            raise UsernameException('Username not valid.')

    def __repr__(self):
        return f"User({self.username=}, {self.credit_card_number=}, {self.balance=})"

    def __eq__(self, other):
        return self.username == other.username and \
            self.credit_card_number == other.credit_card_number and \
            self.balance == other.balance

    def retrieve_feed(self):
        # TODO: add code here
        return self.feed

    def add_friend(self, new_friend):
        # TODO: add code here
        pass

    def add_to_balance(self, amount):
        self.balance += float(amount)

    def add_credit_card(self, credit_card_number):
        if self.credit_card_number is not None:
            raise CreditCardException('Only one credit card per user!')

        if self._is_valid_credit_card(credit_card_number):
            self.credit_card_number = credit_card_number

        else:
            raise CreditCardException('Invalid credit card number.')

    def pay(self, target, amount, note):
        """
        if user A is paying user B, user's A balance should be used if there's enough balance to cover the whole payment
        if not, user's A credit card should be charged instead.
        """
        amount = float(amount)
        if amount < self.balance:
            payment = self.pay_with_balance(target, amount, note)
        else:
            payment = self.pay_with_card(target, amount, note)
        self.feed.append(f"{self.username} paid {target.username} ${amount:.2f} for {note}")
        target.feed.append(f"{self.username} paid {target.username} ${amount:.2f} for {note}")
        return payment

    def pay_with_card(self, target, amount, note):
        amount = float(amount)

        if self.username == target.username:
            raise PaymentException('User cannot pay themselves.')

        elif amount <= 0.0:
            raise PaymentException('Amount must be a non-negative number.')

        elif self.credit_card_number is None:
            raise PaymentException('Must have a credit card to make a payment.')

        self._charge_credit_card(self.credit_card_number)
        payment = Payment(amount, self, target, note)
        target.add_to_balance(amount)

        return payment

    def pay_with_balance(self, target, amount, note):
        self.balance -= amount
        target.balance += amount
        return Payment(amount, self, target, note)

    def _is_valid_credit_card(self, credit_card_number):
        return credit_card_number in ["4111111111111111", "4242424242424242"]

    def _is_valid_username(self, username):
        return re.match('^[A-Za-z0-9_\\-]{4,15}$', username)

    def _charge_credit_card(self, credit_card_number):
        # magic method that charges a credit card thru the card processor
        pass


class Payment:

    def __init__(self, amount: float, actor: User, target: User, note: str):
        self.id = str(uuid.uuid4())
        self.amount = float(amount)
        self.actor = actor
        self.target = target
        self.note = note


class MiniVenmo:

    @staticmethod
    def create_user(username: str, balance: float, credit_card_number: str) -> User:
        user = User(username)
        user.credit_card_number = credit_card_number
        user.balance = balance
        return user

    @staticmethod
    def render_feed(feed):
        for row in feed:
            print(row)

    @classmethod
    def run(cls):
        venmo = cls()

        bobby = venmo.create_user("Bobby", 5.00, "4111111111111111")
        carol = venmo.create_user("Carol", 10.00, "4242424242424242")

        try:
            # should complete using balance
            bobby.pay(carol, 5.00, "Coffee")

            # should complete using card
            carol.pay(bobby, 15.00, "Lunch")
        except PaymentException as e:
            print(e)

        feed = bobby.retrieve_feed()
        venmo.render_feed(feed)

        bobby.add_friend(carol)


class TestUser(unittest.TestCase):

    def test_this_works(self):
        with self.assertRaises(UsernameException):
            raise UsernameException()

    def test_create_user(self):
        old_user = User(username="userA")
        old_user.credit_card_number = "4111111111111119"
        old_user.balance = 100.1

        new_user: User = MiniVenmo.create_user(username="userA", balance=100.1, credit_card_number="4111111111111119")

        self.assertEqual(new_user, old_user)

    def test_pay_with_balance(self):
        """
        if user A is paying user B, user's A balance should be used if there's enough balance to cover the whole payment
        """
        alice = MiniVenmo.create_user(username="Alice", balance=100, credit_card_number="4111111111111119")
        bob = MiniVenmo.create_user(username="Bobby", balance=200, credit_card_number="4999999999999999")

        payment = alice.pay(bob, 50.1, "")

        self.assertIsInstance(payment, Payment)
        self.assertEqual(alice.balance, 49.9)
        self.assertEqual(bob.balance, 250.1)

    def test_pay_with_creditcard(self):
        """
        if not, user's A credit card should be charged instead.
        """
        alice = MiniVenmo.create_user(username="Alice", balance=100, credit_card_number="4111111111111119")
        bob = MiniVenmo.create_user(username="Bobby", balance=200, credit_card_number="4999999999999999")

        payment = alice.pay(bob, 105, "")

        self.assertIsInstance(payment, Payment)
        self.assertEqual(alice.balance, 100)
        self.assertEqual(bob.balance, 305)

    def test_retrieve_feed(self):
        """
        3. Venmo has the Feed functionality, that shows the payments that users have been doing in the app.
        If Bobby paid Carol $5, and then Carol paid Bobby $15, it should look something like this

            Bobby paid Carol $5.00 for Coffee
            Carol paid Bobby $15.00 for Lunch
        """
        alice = MiniVenmo.create_user(username="Alice", balance=100, credit_card_number="4111111111111119")
        bobby = MiniVenmo.create_user(username="Bobby", balance=200, credit_card_number="4999999999999999")

        payment1 = alice.pay(bobby, 20, "Coffee")
        payment2 = bobby.pay(alice, 30, "Sandwich")

        self.assertEquals("Alice paid Bobby $20.00 for Coffee",  alice.retrieve_feed()[0])
        self.assertEquals("Bobby paid Alice $30.00 for Sandwich", alice.retrieve_feed()[1])


if __name__ == '__main__':
    unittest.main()
