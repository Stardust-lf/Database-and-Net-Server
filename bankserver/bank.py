#!/usr/bin/env python3
# Copyright (c) 2008-11 Qtrac Ltd. All rights reserved.
# This program or module is free software: you can redistribute it and/or
# modify it under the terms of the GNU General Public License as published
# by the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version. It is provided for educational
# purposes and is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU
# General Public License for more details.

import collections
import pickle
import socket
import struct
import sys
import Console

Address = ["localhost", 9653]
AccountTuple = collections.namedtuple("AccountTuple", "holder phone balance")


class SocketManager:

    def __init__(self, address):
        self.address = address

    def __enter__(self):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.connect(self.address)
        return self.sock

    def __exit__(self, *ignore):
        self.sock.close()


def main():
    if len(sys.argv) > 1:
        Address[0] = sys.argv[1]
    call = dict(c=new_account, i=increase_balance, d=decrease_balance,
                a=get_account_details, s=stop_server, q=quit)
    menu = ("(C)reate (I)ncrement (D)ecrement (A)ccount "
            "(S)top server  (Q)uit")
    valid = frozenset("cidasq")
    previous_license = None
    while True:
        action = Console.get_menu_choice(menu, valid, "c", True)
        previous_license = call[action](previous_license)


def retrieve_account_details(previous_license):
    license = Console.get_string("Account Number", "number",
                                 previous_license)
    if not license:
        return previous_license, None
    license = license.upper()
    ok, *data = handle_request("GET_ACCOUNT_DETAILS", license)
    if not ok:
        print(data[0])
        return previous_license, None
    return license, AccountTuple(*data)


def get_account_details(previous_license):
    license, account = retrieve_account_details(previous_license)
    if account is not None:
        print("Account " + str(license) + " Details: ")
        print("Holder: {holder}\nPhone Number: {phone}\n"
              "Current Balance: {balance}".format(license, **account._asdict()))
    return license


def increase_balance(previous_license):
    license, account = retrieve_account_details(previous_license)
    if account is None:
        return previous_license
    balance = Console.get_float("Account", "balance",
                                  account.balance, 0)

    if balance == 0:
        return license
    elif round(balance,2) != balance:
        print("The balance contains up to two decimal places")
        return license
    ok, *data = handle_request("INCREASE_BALANCE", license, balance)
    if not ok:
        print(data[0])
    else:
        print("BALANCE successfully increased")
    return license

def decrease_balance(previous_license):
    license, account = retrieve_account_details(previous_license)
    if account is None:
        return previous_license
    balance = Console.get_float("Account", "balance",
                                  account.balance, 0)
    if balance== 0:
        return license
    elif round(balance,2) != balance:
        print("The balance contains up to two decimal places")
        return license
    ok, *data = handle_request("DECREASE_BALANCE", license, balance)
    if not ok:
        print(data[0])
    else:
        print("BALANCE successfully decreased")
    return license


def new_account(previous_license):
    license = Console.get_string("Number", "number")
    if not license:
        return previous_license
    license = license.upper()
    holder = Console.get_string("Account Holder", "holder")
    if not holder:
        return previous_license
    phone = Console.get_string("Phone Number", "phone")
    if not phone:
        return previous_license
    elif len(phone) != 9:
        print("The phone number should be nine digits")
        return previous_license
    balance = Console.get_float("Balance", "balance",0.00,0)
    if round(balance,2) != balance:
        print("The balance contains up to two decimal places")
        return previous_license
    ok, *data = handle_request("NEW_ACCOUNT", license, holder,
                               phone, balance)
    if not ok:
        print(data[0])
    else:
        print("Car {0} successfully registered".format(license))
    return license


def quit(*ignore):
    sys.exit()


def stop_server(*ignore):
    handle_request("SHUTDOWN", wait_for_reply=False)
    sys.exit()


def handle_request(*items, wait_for_reply=True):
    SizeStruct = struct.Struct("!I")
    data = pickle.dumps(items, 3)

    try:
        with SocketManager(tuple(Address)) as sock:
            sock.sendall(SizeStruct.pack(len(data)))
            sock.sendall(data)
            if not wait_for_reply:
                return
            size_data = sock.recv(SizeStruct.size)
            size = SizeStruct.unpack(size_data)[0]
            result = bytearray()
            while True:
                data = sock.recv(4000)
                if not data:
                    break
                result.extend(data)
                if len(result) >= size:
                    break
        return pickle.loads(result)
    except socket.error as err:
        print("{0}: is the server running?".format(err))
        sys.exit(1)


main()
