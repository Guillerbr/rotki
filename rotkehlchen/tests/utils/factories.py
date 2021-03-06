import base64
import random
import string

from eth_utils.address import to_checksum_address

from rotkehlchen.fval import FVal
from rotkehlchen.typing import ApiKey, ApiSecret
from rotkehlchen.utils.misc import ts_now


def make_random_bytes(size):
    return bytes(bytearray(random.getrandbits(8) for _ in range(size)))


def make_random_b64bytes(size):
    return base64.b64encode(make_random_bytes(size))


def make_random_uppercasenumeric_string(size):
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=size))


def make_random_positive_fval(max_num=1000000):
    return FVal(random.uniform(0, max_num))


def make_random_timestamp(start=1451606400, end=None):
    if end is None:
        end = ts_now()
    return random.randint(start, end)


def make_api_key() -> ApiKey:
    return ApiKey(make_random_b64bytes(128).decode())


def make_api_secret() -> ApiSecret:
    return ApiSecret(base64.b64encode(make_random_b64bytes(128)))


def make_ethereum_address():
    return to_checksum_address('0x' + make_random_bytes(20).hex())


UNIT_BTC_ADDRESS1 = '1BvBMSEYstWetqTFn5Au4m4GFg7xJaNVN2'
UNIT_BTC_ADDRESS2 = '1CounterpartyXXXXXXXXXXXXXXXUWLpVr'
UNIT_BTC_ADDRESS3 = '18ddjB7HWTVxzvTbLp1nWvaBxU3U2oTZF2'
