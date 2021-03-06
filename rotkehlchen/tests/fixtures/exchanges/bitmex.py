import pytest

from rotkehlchen.exchanges.bitmex import Bitmex
from rotkehlchen.user_messages import MessagesAggregator

TEST_BITMEX_API_KEY = 'XY98JYVL15Zn-iU9f7OsJeVf'
TEST_BITMEX_API_SECRET = b'671tM6f64bt6KhteDakj2uCCNBt7HhZVEE7H5x16Oy4zb1ag'


@pytest.fixture
def mock_bitmex(database, inquirer):  # pylint: disable=unused-argument
    # API key/secret from tests cases here: https://www.bitmex.com/app/apiKeysUsage
    bitmex = Bitmex(
        api_key='LAqUlngMIQkIUjXMUreyu3qn',
        secret=b'chNOOS4KvNXR_Xq4k4c9qsfoKWvnDecLATCRlcBwyKDYnWgO',
        database=database,
        msg_aggregator=MessagesAggregator(),
    )

    bitmex.first_connection_made = True
    return bitmex


@pytest.fixture
def test_bitmex(database, inquirer):  # pylint: disable=unused-argument
    # API key/secret from tests cases here: https://www.bitmex.com/app/apiKeysUsage
    bitmex = Bitmex(
        api_key=TEST_BITMEX_API_KEY,
        secret=TEST_BITMEX_API_SECRET,
        database=database,
        msg_aggregator=MessagesAggregator(),
    )
    bitmex.uri = 'https://testnet.bitmex.com'
    return bitmex
