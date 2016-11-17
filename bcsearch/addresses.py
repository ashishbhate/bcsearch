import random
import re
import subprocess

from bs4 import BeautifulSoup
import requests


def get_addresses_directoryio():
    """
    Return a dict of [address]private_key from a random page from
    directory.io
    """
    URL_FMT = "http://directory.io/{page}"
    MAX_PAGES = 904625697166532776746648320380374280100293470930272690489102837043110636675  # NOQA

    addresses = {}
    page = random.randrange(1, MAX_PAGES)
    response = requests.get(URL_FMT.format(page=page))
    if response.status_code != 200:
        return None

    soup = BeautifulSoup(response.text, "html.parser")
    key_node = soup.find("pre", class_="keys")
    spans = key_node.find_all("span")
    i = 0
    for span in spans:
        i += 1
        if i % 2:
            text = span.get_text()
            _, private_key, address, _ = text.split()
            addresses[address] = private_key

    return addresses


def get_addresses_from_vanitygen(vanitygen_path, timeout=5):
    try:
        subprocess.run([vanitygen_path, "-k", "1"], stdout=subprocess.PIPE,
                       timeout=timeout, universal_newlines=True)
    except subprocess.TimeoutExpired as e:
        vg_out = e.stdout

    addresses = {}
    vg_out = vg_out.splitlines()
    address_sub = re.compile("Address")
    privkey_sub = re.compile("Privkey")
    for each_line in vg_out:
        if address_sub.match(each_line):
            address = each_line.split()[1]
        elif privkey_sub.match(each_line):
            addresses[address] = each_line.split()[1]

    return addresses
