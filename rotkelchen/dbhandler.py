import time
import os
from pysqlcipher3 import dbapi2 as sqlcipher

from rotkelchen.constants import SUPPORTED_EXCHANGES
from rotkelchen.fval import FVal
from rotkelchen.errors import AuthenticationError, InputError


# https://stackoverflow.com/questions/4814167/storing-time-series-data-relational-or-non
# http://www.sql-join.com/sql-join-types
class DBHandler(object):

    def __init__(self, user_data_dir, username, password):
        self.conn = sqlcipher.connect(os.path.join(user_data_dir, 'rotkehlchen.db'))
        self.conn.text_factory = str
        self.conn.executescript('PRAGMA key="{}"; pragma kdf_iter=64000;'.format(password))
        self.conn.execute('PRAGMA foreign_keys=ON')
        cursor = self.conn.cursor()
        try:
            cursor.execute(
                'CREATE TABLE IF NOT EXISTS timed_balances ('
                '    time INTEGER, currency VARCHAR[12], amount DECIMAL, usd_value DECIMAL'
                ')'
            )
        except sqlcipher.DatabaseError:
            raise AuthenticationError('Wrong password while decrypting the database')
        cursor.execute(
            'CREATE TABLE IF NOT EXISTS timed_location_data ('
            '    time INTEGER, location VARCHAR[24], usd_value DECIMAL'
            ')'
        )
        cursor.execute(
            'CREATE TABLE IF NOT EXISTS timed_unique_data ('
            '    time INTEGER, net_usd DECIMAL'
            ')'
        )
        cursor.execute(
            'CREATE TABLE IF NOT EXISTS exchange_credentials ('
            '    name VARCHAR[24], api_key TEXT, api_secret TEXT'
            ')'
        )
        cursor.execute(
            'CREATE TABLE IF NOT EXISTS blockchain_accounts ('
            '    blockchain VARCHAR[24], account TEXT NOT NULL PRIMARY KEY'
            ')'
        )
        cursor.execute(
            'CREATE TABLE IF NOT EXISTS eth_tokens ('
            '    token VARCHAR[24] NOT NULL PRIMARY KEY'
            ')'
        )
        cursor.execute(
            'CREATE TABLE IF NOT EXISTS current_balances ('
            '    asset VARCHAR[24] NOT NULL PRIMARY KEY, amount DECIMAL'
            ')'
        )
        self.conn.commit()

    def add_multiple_balances(self, balances):
        """Execute addition of multiple balances in the DB

        balances should be a list of tuples each containing:
        (time, asset, amount, usd_value)"""
        cursor = self.conn.cursor()
        cursor.executemany(
            'INSERT INTO timed_balances('
            '    time, currency, amount, usd_value) '
            ' VALUES(?, ?, ?, ?)',
            balances
        )
        self.conn.commit()

    def add_multiple_location_data(self, location_data):
        """Execute addition of multiple location data in the DB

        location_data should be a list of tuples each containing:
        (time, location, usd_value)"""
        cursor = self.conn.cursor()
        cursor.executemany(
            'INSERT INTO timed_location_data('
            '    time, location, usd_value) '
            ' VALUES(?, ?, ?)',
            location_data
        )
        self.conn.commit()

    def add_timed_unique_data(self, time, net_usd):
        cursor = self.conn.cursor()
        cursor.execute(
            'INSERT INTO timed_unique_data(time, net_usd) VALUES (?, ?)',
            (time, net_usd)
        )
        self.conn.commit()

    def write_owned_tokens(self, tokens):
        """Execute addition of multiple tokens in the DB

        tokens should be a list of token symbols
        (time, location, usd_value)"""
        cursor = self.conn.cursor()
        cursor.executemany(
            'INSERT INTO eth_tokens(token) VALUES (?)',
            [(t,) for t in tokens]
        )
        self.conn.commit()

    def get_owned_tokens(self):
        cursor = self.conn.cursor()
        query = cursor.execute(
            'SELECT token FROM eth_tokens;'
        )
        query = query.fetchall()
        return [q[0] for q in query]

    def add_blockchain_account(self, blockchain, account):
        cursor = self.conn.cursor()
        cursor.execute(
            'INSERT INTO blockchain_accounts(blockchain, account) VALUES (?, ?)',
            (blockchain, account)
        )
        self.conn.commit()

    def remove_blockchain_account(self, blockchain, account):
        cursor = self.conn.cursor()
        cursor.execute(
            'DELETE FROM blockchain_accounts WHERE '
            'blockchain = ? and account = ?;', (blockchain, account)
        )
        self.conn.commit()

    def add_fiat_balance(self, currency, amount):
        cursor = self.conn.cursor()
        # We don't care about previous value so this simple insert or replace should work
        cursor.execute(
            'INSERT OR REPLACE INTO current_balances(asset, amount) VALUES (?, ?)',
            (currency, amount)
        )
        self.conn.commit()

    def remove_fiat_balance(self, currency):
        cursor = self.conn.cursor()
        cursor.execute(
            'DELETE FROM current_balances WHERE asset = ?;', (currency,)
        )
        self.conn.commit()

    def get_fiat_balances(self):
        cursor = self.conn.cursor()
        query = cursor.execute(
            'SELECT asset, amount FROM current_balances;'
        )
        query = query.fetchall()

        result = {}
        for entry in query:
            result[entry[0]] = entry[1]
        return result

    def get_blockchain_accounts(self):
        """Returns a dictionary with keys being blockchains and values being
        lists of accounts"""
        cursor = self.conn.cursor()
        query = cursor.execute(
            'SELECT blockchain, account FROM blockchain_accounts;'
        )
        query = query.fetchall()
        result = {}

        for entry in query:
            if entry[0] not in result:
                result[entry[0]] = []

            result[entry[0]].append(entry[1])

        return result

    def remove(self):
        cursor = self.conn.cursor()
        cursor.execute('DROP TABLE IF EXISTS timed_balances')
        cursor.execute('DROP TABLE IF EXISTS timed_location_data')
        cursor.execute('DROP TABLE IF EXISTS timed_unique_data')
        self.conn.commit()

    def write_balances_data(self, data):
        ts = int(time.time())
        balances = []
        locations = []

        for key, val in data.items():
            if key in ('location', 'net_usd'):
                continue

            balances.append((
                ts,
                key,
                str(val['amount']),
                str(val['usd_value']),
            ))

        for key, val in data['location'].items():
            locations.append((
                ts, key, str(val['usd_value'])
            ))

        self.add_multiple_balances(balances)
        self.add_multiple_location_data(locations)
        self.add_timed_unique_data(ts, str(data['net_usd']))

    def add_exchange(self, name, api_key, api_secret):
        if name not in SUPPORTED_EXCHANGES:
            raise InputError('Unsupported exchange {}'.format(name))

        cursor = self.conn.cursor()
        cursor.execute(
            'INSERT INTO exchange_credentials (name, api_key, api_secret) VALUES (?, ?, ?)',
            (name, api_key, api_secret)
        )
        self.conn.commit()

    def remove_exchange(self, name):
        cursor = self.conn.cursor()
        cursor.execute(
            'DELETE FROM exchange_credentials WHERE name =?', (name,)
        )
        self.conn.commit()

    def get_exchange_secrets(self):
        cursor = self.conn.cursor()
        result = cursor.execute(
            'SELECT name, api_key, api_secret FROM exchange_credentials;'
        )
        result = result.fetchall()
        secret_data = {}
        for entry in result:
            name = entry[0]
            secret_data[name] = {
                'api_key': str(entry[1]),
                'api_secret': str(entry[2])
            }

        return secret_data