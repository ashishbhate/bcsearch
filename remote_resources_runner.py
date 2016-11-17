"""
Get addresses (and corresponding private keys) from a remote resource
(directory.io) and check if they have a non-zero balance using remote resources
(blockr.io, blockonomics.co etc.). If a non-zero balance address is found,
it is printed on screen, saved to a file, and a pushbullet notification is
sent.
"""
import sys
import time
import traceback

from bcsearch.addresses import get_addresses_directoryio
from bcsearch.balances import get_balances
from bcsearch.utils import pb_notify

while True:
    try:
        print("==== Start ====")

        addresses_dict = get_addresses_directoryio()
        if addresses_dict is None:
            print("* directory.io is unreachable!")
            time.sleep(10)
            continue

        addresses = list(addresses_dict.keys())

        balances = get_balances(addresses)
        if balances is None:
            print("* No balances could be obtained!")
            time.sleep(10)
            continue

        for addr, balance in balances.items():
            if balance != 0:
                privkey = addresses_dict[addr]
                print(balance, addr, privkey)

                with open("remote_found_balances", "a") as fp:
                    fp.write(str(balance) + " " + addr + " " + privkey + "\n")

                pb_notify("FOUND" + str(balance) + "!",
                          addr + " : " + privkey)

        print("==== End ====")

    except Exception:
        # Catch everything except KeyboardIterrupt and SystemExit
        traceback.print_exc()
        pb_notify('Exception in remote runner: Quitting', '')
        sys.exit(1)
