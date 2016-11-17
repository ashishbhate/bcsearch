"""
Get addresses (and corresponding private keys) from vanitygen and check if they
have a non-zero balance by querying a local bitcoind instance that has
addressindex support builtin. If a non-zero balance address is found,
it is printed on screen, saved to a file, and a pushbullet notification is
sent.
"""
import sys
import traceback

from monotonic import monotonic

from bcsearch.addresses import get_addresses_from_vanitygen
from bcsearch.balances import get_balances_bitcoind
from bcsearch.constants import (
    BITCOIND_RPC_PASSWORD, BITCOIND_RPC_USERNAME, VANITYGEN_PATH
)
from bcsearch.utils import pb_notify

while True:
    try:
        print("==========")
        start = monotonic()

        addresses_dict = get_addresses_from_vanitygen(VANITYGEN_PATH, 10)

        if addresses_dict is None:
            print("* vanitygen is borked!")
            continue

        addresses = list(addresses_dict.keys())

        balances = get_balances_bitcoind(addresses,
                                         BITCOIND_RPC_USERNAME,
                                         BITCOIND_RPC_PASSWORD)

        if balances is None:
            print("* No balances could be obtained!")
            continue

        for addr, balance in balances.items():
            if balance != 0:
                privkey = addresses_dict[addr]
                print(balance, addr, privkey)

                with open("found_balances", "a") as fp:
                    fp.write(str(balance) + " " + addr + " " + privkey + "\n")

                pb_notify("FOUND" + str(balance) + "!",
                          addr + " : " + privkey)

        end = monotonic()
        addresses_per_second = len(addresses)/(end - start)
        print("{0:.1f} addresses/second".format(addresses_per_second))

    except Exception as e:
        # Catch everything except KeyboardIterrupt and SystemExit
        traceback.print_exc()
        pb_notify('Exception in local runner: Quitting', '')
        sys.exit(1)
