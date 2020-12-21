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


import copy
import os
import pickle
import socketserver
import struct
import threading
import bank_dbm

class Account:

    def __init__(self, account_number, holder, phone, balance):
        self.__account_number = account_number
        self.__holder = holder
        self.__phone = phone
        self.__balance = balance


    @property
    def holder(self):
        return self.__holder

    @property
    def phone(self):
        return self.__phone

    @property
    def balance(self):
        return self.__balance

    @property
    def account_number(self):
        return self.account_number

    @holder.setter
    def holder(self, holder):
        self.__holder = holder

    @phone.setter
    def phone(self,phone):
        self.__phone = phone

    @balance.setter
    def balance(self, balance):
        self.__balance = balance

    @account_number.setter
    def account_number(self,account_number):
        self.__account_number = account_number

class Finish(Exception): pass


class RequestHandler(socketserver.StreamRequestHandler):
    DatabaseLock = threading.Lock()
    CallLock = threading.Lock()
    Call = dict(
        GET_ACCOUNT_DETAILS=(
            lambda self, *args: self.get_account_details(*args)),
        INCREASE_BALANCE=(
            lambda self, *args: self.increase_balance(*args)),
        DECREASE_BALANCE=(
            lambda self, *args: self.decrease_balance(*args)),
        NEW_ACCOUNT=(
            lambda self,     *args: self.new_account(*args)),
        SHUTDOWN=lambda self, *args: self.shutdown(*args))
    filename = os.path.join(os.path.dirname(__file__), "bank.sdb")
    db = bank_dbm.connect(filename)

    def handle(self):
        SizeStruct = struct.Struct("!I")
        size_data = self.rfile.read(SizeStruct.size)
        size = SizeStruct.unpack(size_data)[0]
        data = pickle.loads(self.rfile.read(size))

        try:
            with RequestHandler.CallLock:
                function = self.Call[data[0]]
            reply = function(self, *data[1:])
        except Finish:
            return
        data = pickle.dumps(reply, 3)
        self.wfile.write(SizeStruct.pack(len(data)))
        self.wfile.write(data)

    def get_account_details(self, number):
        with RequestHandler.DatabaseLock:
            #account = copy.copy(self.Accounts.get(number, None))
            account = copy.copy(bank_dbm.get_account(self.db, number))
        if account is not None:
            customer = copy.copy(bank_dbm.get_customer(self.db,account[3]))
            if customer is not None:
                return (True, customer[0], customer[1], account[2])
        return (False, "This account is not registered")

    def increase_balance(self, number, balance):
        if balance < 0:
            return (False, "Cannot increase by a negative balance")
        with RequestHandler.DatabaseLock:
            oldBalance = bank_dbm.get_account(self.db,number)[2]
            if oldBalance is not None:
                newBalance = oldBalance + balance
                bank_dbm.update_balance(self.db,number,newBalance)
                return (True, "Increase balance successfully.")
        return (False, "This account is not registered")

    def decrease_balance(self, number, balance):
        if balance < 0:
            return (False, "Cannot decrease by a negative balance")
        with RequestHandler.DatabaseLock:
            oldBalance = bank_dbm.get_account(self.db, number)[2]
            if oldBalance is not None:
                newBalance = oldBalance - balance
                if newBalance<=0:
                    return (False, "Balance can not be negative")
                bank_dbm.update_balance(self.db, number, newBalance)
                return (True, "Decrease balance successfully.")
        return (False, "This account is not registered")

    def new_account(self, number, holder, phone, balance):
        if not number:
            return (False, "Cannot set an empty account")
        if not holder:
            return (False, "Cannot set an empty holder")
        if len(phone) != 9:
            return (False, "Cannot register account with invalid length phone number")
        if balance<0:
            return (False, "Cannot register account with negative balance")
            print('account is ' + bank_dbm.get_account(self.db,number))
        if bank_dbm.get_account(self.db,number) is None:
            bank_dbm.add_account(self.db, number, balance, holder, phone)
            return (True, None)
        return (False, "Cannot register duplicate number")

    def shutdown(self, *ignore):
        self.server.shutdown()
        bank_dbm.quit(self.db)
        raise Finish()


class BankServer(socketserver.ThreadingMixIn,
                            socketserver.TCPServer): pass


def main():
    server = None
    try:
        server = BankServer(("", 9653), RequestHandler)
        server.serve_forever()
    except Exception as err:
        print("ERROR", err)
    finally:
        if server is not None:
            server.shutdown()


main()
