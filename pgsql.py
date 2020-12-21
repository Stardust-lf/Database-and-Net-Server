import psycopg2
import sys
import Console

Port = 5432
Host = '127.0.0.1'
Database = 'fregrant'

def main():
    try:
        user = Console.get_string("please enter your username: ", default="postgres")
        password = Console.get_string("please enter your password")
        db = connect(user,password)
        print("opened db successfully")
    except Exception:
        print("Connect failed, please check your username and password.")
        return
    call = [new,delete,update,search,rollback,commit,quit]
    menu = ("(1)New (2)Delete (3)Update (4)Search (5)Rollback (6)Commit (7)Commit&Quit")
    valid=frozenset("1234567")
    while True:
        action = Console.get_menu_choice(menu, valid, "1", True)
        call[int(action)-1](db)

def connect(user,password):
    conn = psycopg2.connect(host=Host, port=Port, user=user, password=password, database=Database)
    return conn
def new(db):
    cursor = db.cursor()
    table = Console.get_string("please enter the table you want to insert into ", default='perfume')
    value = Console.get_string("please enter the values you want to insert(separated by \',\') ")
    if not table or not value:
        print('please enter table name and values.')
        db.commit()
        return
    try:
        print("insert into {0} values({1})".format(table,value))
        cursor.execute("insert into {0} values({1});".format(table,value))
    except Exception as err:
        print("Something error happens, please check and try again.")
        print(err)
    db.commit()
    return

def delete(user,password):
    conn = connect(user,password)
    cursor = conn.cursor()
    table = Console.get_string("please enter the table you want to delete from ", default='perfume')
    filt = Console.get_string("please input the filter:(format: key=value)")
    if not table or not filt:
        print("please enter table name and filter.")
        conn.commit()
        conn.close()
        return
    try:
        cursor.execute("delete from {0} where {1};".format(table,filt))
    except Exception as err:
        print("Something error happens, please check and try again.")
        print(err)
    conn.commit()
    conn.close()
    return

def update(user,password):
    conn = connect(user,password)
    cursor = conn.cursor()
    table = Console.get_string("please enter the table you want to update ", default='perfume')
    set = Console.get_string("please enter the update equation:(format: attr1=value1,attr2=value2) ", default='perfume')
    filt = input("please enter the judgement sentence you want to filter by:(format: key=value) ")
    if not table or not set or not filt:
        print("please enter table, equation and filter.")
        conn.commit()
        conn.close()
        return
    try:
        cursor.execute("update {0} set {1} where {3};".format(table,set,filt))
    except Exception as err:
        print("Something error happens, please check and try again.")
        print(err)
    conn.commit()
    conn.close()
    return

def search(db):
    cursor = db.cursor()
    table = Console.get_string("please enter the table you want to search ",default='perfume')
    row = Console.get_string("please enter the row you want to search on(format: value1,value2) ")
    filt = input("please enter the judgement sentence you want to filter by(format: key=value) ")
    if not table or not row or not filt:
        print("please enter table, row and filter.")
    try:
        cursor.execute("Select {0} from {1} where {2};".format(row,table,filt,))
    except Exception as err:
        print("Something error happens, please check and try again.")
        print(err)
        return
    rows = cursor.fetchall()
    for row in rows:
        print(row)
    return

def commit(db):
    try:
        db.commit()
    except Exception as err:
        print('Commit failed')
        print(err)
        return
    print('Commit data succeed')
    return

def rollback(db):
    try:
        db.rollback()
    except Exception as err:
        print('Rollback failed')
        print(err)
        return
    print('Rollback succeed')
    return

def quit(db):
    try:
        db.commit()
    except Exception as err:
        print("Commit data failed")
        print(err)
        return
    print("Commit data succeed")
    db.close()
    sys.exit()

main()

