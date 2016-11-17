from multiprocessing.dummy import Pool as ThreadPool
import random
import time

import requests


def get_balances_bitcoind(addresses, username, password,
                          url="http://127.0.0.1", port=8332):
    """
    Returns only non-zero balances
    """
    print("* Using bitcoind to query {} addresses".format(len(addresses)))
    balances = {}
    balances_list = []
    url = url + ":" + str(port)
    headers = {'content-type': 'application/json'}

    # Making separate requests for each address is surprisingly only a few
    # seconds slower (in total) than making a single request with all
    # addresses.  # It's also easier to recover incase of a bad address from
    # vanitygen.
    def _get_balance(address):
        payload = {
            "method": "getaddressbalance",
            "params": [{"addresses": [address]}],
            "jsonrpc": "2.0",
            "id": 0,
        }

        response = requests.post(url, json=payload, headers=headers,
                                 auth=(username, password))

        if response.status_code != 200:
            return (address, 0)

        data = response.json()
        return (address, data["result"]["balance"])

    pool = ThreadPool(4)
    balances_list = pool.map(_get_balance, addresses)
    pool.close()
    pool.join()

    for addr, bal in balances_list:
        if bal != 0:
            balances[addr] = bal

    return balances


def get_balances_blockr(addresses):
    """
    blockr.io
    blockr only allows a max of 20 addresses per request
    """
    print("* Using blockr.io to query {} addresses".format(len(addresses)))
    BLOCKR_BALANCE_ENDPOINT = "http://btc.blockr.io/api/v1/address/balance/{addresses}"  # NOQA

    addrs = ','.join(addresses)
    response = requests.get(BLOCKR_BALANCE_ENDPOINT.format(addresses=addrs))
    if response.status_code != 200:
        print("** Blockr sent bad server reponse: ", response.status_code)
        return None

    data = response.json()
    if data["status"] != "success":
        print("** Blockr sent bad data reponse: ", data["status"])
        return None

    balances = {}
    for each in data["data"]:
        balances[each["address"]] = each["balance"]

    return balances


def get_balances_blockonomics(addresses):
    """
    blockonomics.co
    Max 50 addresses per request
    """
    print("* Using blockonomics.co to query {} addresses".format(len(addresses)))  # NOQA
    BLOCKONOMICS_BALANCE_ENDPOINT = "https://www.blockonomics.co/api/balance"
    addrs = " ".join(addresses)
    response = requests.post(BLOCKONOMICS_BALANCE_ENDPOINT,
                             json={"addr": addrs})
    if response.status_code != 200:
        print("** blockonomics sent bad server reponse: ",
              response.status_code)
        return None

    balances = {}
    data = response.json()
    for each in data["response"]:
        balances[each["addr"]] = each["confirmed"] + each["unconfirmed"]

    return balances


def get_balances_blockexplorer(addresses):
    """
    blockexplorer.com
    NOT HOOKED UP
    """
    print("* blockexplorer.com not yet supported")
    return None


def get_balances_blockchain(addresses):
    """
    blockchain.info
    NOT HOOKED UP
    """
    print("* blockchain.info not yet supported")
    return None


def get_balances_chain(addresses):
    """
    chain.so
    NOT HOOKED UP
    Has a 5 reqs/sec limit. And doesnt like more than 5 continuous requests
    in a short period of time.
    """
    print("* Using chain.so to query {} addresses - one at a time".format(len(addresses)))  # NOQA

    CHAINS_BALANCE_ENDPOINT = "https://chain.so/api/v2/get_address_balance/BTC/{address}"  # NOQA
    balances = {}
    i = 0
    for addr in addresses:
        i += 1
        response = requests.get(CHAINS_BALANCE_ENDPOINT.format(address=addr))
        if response.status_code != 200:
            print("** Chain sent bad server reponse: ", response.status_code)
            print("** Query number: ", i)
            return None

        data = response.json()
        if data["status"] != "success":
            print("** Chain sent bad data reponse: ", data["status"])
            return None

        balances[data["data"]["address"]] = \
            data["data"]["confirmed_balance"] + \
            data["data"]["unconfirmed_balance"]

        # 0.2 is 5 reqs/second. Using 0.3 just in case.
        time.sleep(0.3)

    return balances

# blockchain.info -> Gives sum of all addresses instead of of each address
# blockexplorer.com -> one address at a time
# toshi.io -> one address at a time
# chain.so -> one address at a time; 5 reqs/sec; doesnt like continuous requests  # NOQA
# kaiko.com -> one address at a time


SOURCES = {"blockr.io": get_balances_blockr,
           "blockonomics.co": get_balances_blockonomics}

MAX_ADDRS = {"blockr.io": 20,
             "blockonomics.co": 50}

AVAILABLE_SOURCES = set(["blockr.io", "blockonomics.co"])


def _get_random_source(available_sources):
    return random.sample(available_sources, 1)[0]


def _get_addresses(remaining_addresses, source):
    if len(remaining_addresses) > MAX_ADDRS[source]:
        addresses = remaining_addresses[:MAX_ADDRS[source]]
        remaining_addresses = list(set(remaining_addresses)-set(addresses))
    else:
        addresses = remaining_addresses
        remaining_addresses = list(set(remaining_addresses)-set(addresses))

    return remaining_addresses, addresses


def get_balances(addresses, use_source=None):

    remaining_addresses = addresses[:]
    all_balances = {}
    available_sources = AVAILABLE_SOURCES.copy()

    while remaining_addresses:
        if use_source is None or use_source not in available_sources:
            source = _get_random_source(available_sources)
        else:
            source = use_source

        remaining_addresses, addresses = _get_addresses(remaining_addresses,
                                                        source)

        balances = SOURCES[source](addresses)

        while balances is None:
            available_sources.remove(source)

            if not available_sources:
                break

            remaining_addresses.extend(addresses)
            source = _get_random_source(available_sources)
            remaining_addresses, addresses = _get_addresses(
                remaining_addresses, source
            )
            balances = SOURCES[source](addresses)

        if not available_sources:
            return all_balances
        else:
            if balances is not None:
                all_balances.update(balances)

        time.sleep(10)

    return all_balances
