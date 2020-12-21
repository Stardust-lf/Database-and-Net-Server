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

import os
import sqlite3
import sys
import Util

DISPLAY_LIMIT = 20

def connect(filename):
    create = not os.path.exists(filename)
    db = sqlite3.connect(filename,check_same_thread=False)
    if create:
        cursor = db.cursor()
        cursor.execute("CREATE TABLE customer ("
                       "id INTEGER PRIMARY KEY AUTOINCREMENT UNIQUE NOT NULL, "
                       "name TEXT NOT NULL, "
                       "phone_number INTEGER NOT NULL);")
        cursor.execute("CREATE TABLE account ("
                       "id INTEGER PRIMARY KEY AUTOINCREMENT UNIQUE NOT NULL, "
                       "account_number INTEGER UNIQUE NOT NULL, "
                       "balance FLOAT NOT NULL, "
                       "customer_id INTEGER NOT NULL, "
                       "FOREIGN KEY(customer_id) REFERENCES customer);")
        db.commit()
    return db


def add_account(db,account_number,balance,holder,phone_number):
    customer_id = get_and_set_holder(db,holder,phone_number)
    cursor = db.cursor()
    cursor.execute("INSERT INTO account "
                   "(account_number, balance, customer_id) "
                   "VALUES (?, ?, ?)",
                   (account_number, balance, customer_id))
    db.commit()


def get_and_set_holder(db, holder,phone_number):
    director_id = get_holder_id(db, holder)
    if director_id is not None:
        return director_id
    cursor = db.cursor()
    cursor.execute("INSERT INTO customer (name,phone_number) VALUES (?,?)",
                   (holder,phone_number))
    db.commit()
    return get_holder_id(db,holder)

def get_account(db,number):
    cursor = db.cursor()
    cursor.execute("SELECT id,account_number,balance,customer_id from account WHERE account_number=?", (number,))
    fields = cursor.fetchone()
    return fields

def get_customer(db,id):
    cursor = db.cursor()
    cursor.execute("SELECT name,phone_number from customer WHERE id=?",(id,))
    fields = cursor.fetchone()
    return fields

def get_holder_id(db, name):
    cursor = db.cursor()
    cursor.execute("SELECT id FROM customer WHERE name=?",
                   (name,))
    fields = cursor.fetchone()
    return fields[0] if fields is not None else None

def update_balance(db,number,newBalance):
    cursor = db.cursor()
    cursor.execute("UPDATE account SET balance =? WHERE account_number=?",(newBalance,number,))
    db.commit()

def account_count(db):
    cursor = db.cursor()
    cursor.execute("SELECT COUNT(*) FROM customer")
    return cursor.fetchone()[0]

def quit(db):
    if db is not None:
        count = account_count(db)
        db.commit()
        db.close()
        print("Saved {0} account{1}".format(count, Util.s(count)))
    sys.exit()