import sqlite3
import csv
import os
from os import listdir
from os.path import isfile, join

if not os.path.exists("files/"):
    os.makedirs("files/")
db_connection = sqlite3.connect('expenses.sqlite')
cur = db_connection.cursor()

def db_make():
    cur.execute('''CREATE TABLE IF NOT EXISTS Categories
        (id INTEGER PRIMARY KEY, cat_name TEXT UNIQUE)''')
    cur.execute("INSERT OR IGNORE INTO Categories (cat_name) VALUES ('uncategorised')")
    cur.execute('''CREATE TABLE IF NOT EXISTS Payees
        (id INTEGER PRIMARY KEY, payee_name TEXT UNIQUE, cat_id INTEGER)''')
    cur.execute('''CREATE TABLE IF NOT EXISTS Transactions
        (id INTEGER PRIMARY KEY, date DATE, payee_id INTEGER, value FLOAT)''')
    db_connection.commit()

def db_add(table, values):
    if table == "categories":
        cur.execute('''INSERT OR IGNORE INTO Categories (cat_name)
            VALUES (?)''', (memoryview(values.encode()), ))
    elif table == "payees":
        cur.execute('''INSERT OR IGNORE INTO Payees (payee_name, cat_id)
            VALUES (?, 1)''', (memoryview(values.encode()), ))
    elif table == "transactions":
        if not trans_get(values):
            cur.execute('''INSERT INTO Transactions (date, payee_id, value)
                VALUES (?, ?, ?)''',
                (memoryview(values["date"].encode()),
                memoryview(str(values["payee_id"]).encode()),
                memoryview(str(values["value"]).encode()),))

def id_get(table, value):
    if table == "payees":
        cur.execute("SELECT id FROM Payees WHERE payee_name = ?",
            (memoryview(value.encode()), ))
    elif table == "categories":
        cur.execute("""SELECT id FROM Categories WHERE cat_name = ?""",
            (memoryview(value.encode()),))
    return cur.fetchone()[0]

def trans_get(values):
    cur.execute("SELECT id FROM Transactions WHERE date = ? AND payee_id = ? AND value = ? ",
        (memoryview(values["date"].encode()),
        memoryview(str(values["payee_id"]).encode()),
        memoryview(str(values["value"]).encode()),))
    return cur.fetchone()

def nocat_file_make():
    cur.execute("SELECT * FROM Categories")
    cats = cur.fetchall()
    cur.execute("SELECT payee_name FROM Payees WHERE cat_id = 1")
    no_cat_payees = cur.fetchall()
    with open("files/new_cats.csv", "w") as f:
        f.write("payee,cat")
        for p in no_cat_payees:
            f.write("\n{0}".format(p[0].decode()))
    with open("categories_list.csv", "w") as f:
        for cat in cats:
            if cat[0] == 1:
                f.write(str(cat[0]) + "," + cat[1])
            else:
                f.write("\n" + str(cat[0]) + "," + cat[1].decode())

def cat_assign():
    with open("files/new_cats.csv") as f:
        payee_dict = csv.DictReader(f)
        for payee in payee_dict:
            if payee["payee"] != "uncategorised" and payee["cat"]:
                db_add("categories", payee["cat"])
                cat_id = id_get("categories", payee["cat"])
                cur.execute("UPDATE Payees SET cat_id=? WHERE payee_name=?",
                    (memoryview(str(cat_id).encode()), memoryview(payee["payee"].encode())))
                db_connection.commit()

def trans_dict_make(heads, data, payee_column):
    base_dict = {h:v for h, v in (zip(heads, data))}
    if base_dict["paid in"]:
        base_dict["value"] = float(base_dict["paid in"][1:])
    elif base_dict["paid out"]:
        base_dict["value"] = float(base_dict["paid out"][1:]) * (-1)
    if "Android" in base_dict[payee_column]:
        ind = base_dict[payee_column].index("Android")
        base_dict[payee_column] = base_dict[payee_column][:ind]
    db_add("payees", base_dict[payee_column])
    base_dict["payee_id"] = id_get("payees", base_dict[payee_column])
    return base_dict

def read_files():
    exp_files = [f for f in listdir("files") if isfile(join("files", f))]
    for fle in exp_files:
        if fle == "new_cats.csv":
            cat_assign()
        else:
            with open("files/{0}".format(fle)) as f:
                exp_reader = csv.reader(f)
                for row in exp_reader:
                    if "Account Name:" in row:
                        if row[1][-4:] == "1066" or row[1][-4:] == "4731":
                            payee_column = "description"
                        elif row[1][-4:] == "4150":
                            payee_column = "transactions"
                    elif "Date" in row:
                        heads = [h.lower() for h in row]
                    else:
                        try:
                            int(row[0][:2])
                        except:
                            continue
                        current_transaction = trans_dict_make(heads, row, payee_column)
                        db_add("transactions", current_transaction)
                        db_connection.commit()
            os.remove("files/{0}".format(fle))
    nocat_file_make()

db_make()
read_files()
