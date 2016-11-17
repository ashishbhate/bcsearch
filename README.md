A set of python modules to generate bitcoin addresses (and corresponding
private keys) and to check if the generated addresses have a non-zero balance.


`bcsearch.addresses` contains functions to get addresses and keys.

`bcsearch.balances` contains functions to get balances.

`bcsearch.constants` contains settings and secrets that will
need to be overridden.

`bcsearch.utils` contains utility functions.

For examples see `local_resources_runner.py` and `remote_resources_runner.py`

`remote_resources_runner.py` only uses external resources to fetch addresses
and check balances. There is no setup required besides a python3 environment
with the requirements from `requirements.txt` installed.

`local_resources_runner.py` only uses local resources to fetch addresses
and check balances. It needs vanitygen (https://github.com/samr7/vanitygen)
to generate addresses and keys, and bitcoind built with address indexes
(see https://bitcore.io/guides/bitcoin/) to check balances.


Make sure the `bcsearch` folder is in `sys.path` so that the module is
importable.


Only `python3` is supported. Requirements are in `requirements.txt`
