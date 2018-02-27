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
        (cat_id INTEGER PRIMARY KEY, cat_name TEXT UNIQUE)''')
    cur.execute("INSERT OR IGNORE INTO Categories (cat_name) VALUES ('uncategorised')")
    cur.execute('''CREATE TABLE IF NOT EXISTS Payees
        (payee_id INTEGER PRIMARY KEY, payee_name TEXT UNIQUE, cat_id INTEGER)''')
    cur.execute('''CREATE TABLE IF NOT EXISTS Transactions
        (trans_id INTEGER PRIMARY KEY, date DATE, payee_id INTEGER, value FLOAT)''')
    db_connection.commit()

def db_add(table, values):
    if table == "categories":
        cur.execute('''INSERT OR IGNORE INTO Categories (cat_name)
            VALUES ('{val}')'''.format(val=values))
    elif table == "payees":
        cur.execute('''INSERT OR IGNORE INTO Payees (payee_name, cat_id)
            VALUES ('{val}', 1)'''.format(val=values))
    elif table == "transactions":
        if not trans_get(values):
            cur.execute('''INSERT INTO Transactions (date, payee_id, value)
                VALUES ('{date}', {pay}, {val})'''.format(date=values["date"],\
                pay=values["payee_id"], val=values["value"]))

def id_get(table, value):
    if table == "payees":
        cur.execute("SELECT payee_id FROM Payees WHERE payee_name = '{val}'".format(val=value))
    elif table == "categories":
        cur.execute("""SELECT cat_id FROM Categories WHERE cat_name = '{val}'""".format(val=value))
    got_id = cur.fetchone()
    return got_id[0]

def trans_get(values):
    cur.execute("SELECT trans_id FROM Transactions WHERE date = '{date}' AND payee_id = {pay} AND value = {val}".format(\
        date=values["date"],pay=values["payee_id"],val=values["value"]))
    return cur.fetchone()

def trans_join():
    cur.execute("""SELECT Transactions.date, Transactions.value, Payees.payee_name, Categories.cat_name
        FROM Transactions
        INNER JOIN Payees ON Payees.payee_id = Transactions.payee_id
        INNER JOIN Categories ON Categories.cat_id = Payees.cat_id""")
    return cur.fetchall()

def trans_by_cat(cat):
    cat_t = []
    all_t = trans_join()
    for t in all_t:
        if cat in t:
            cat_t.append(t)
    return cat_t

def cat_trans():
    cats = cat_get()
    t_by_cats = {}
    for cat in cats:
        if not t_by_cats.get(cat):
            t_by_cats[cat] = []
        t_by_cats[cat] += trans_by_cat(cat[1])
    return(t_by_cats)

def cat_sum():
    t_by_cats = cat_trans()
    sum_by_cat = {}
    for cat in t_by_cats:
        cat_sum = 0
        for t in t_by_cats[cat]:
            cat_sum += t[1]
        sum_by_cat[cat[1]] = cat_sum
    return sum_by_cat

def cat_sum_by_month():
    t_by_cats = cat_trans()
    sum_by_cat = {}
    for cat in t_by_cats:
        for t in t_by_cats[cat]:
            month = t[0][3:-4]
            if not sum_by_cat.get(month):
                sum_by_cat[month] = {}
            if not sum_by_cat[month].get(cat[1]):
                sum_by_cat[month][cat[1]] = 0
            sum_by_cat[month][cat[1]] += t[1]
    return sum_by_cat

def cat_sum_by_year():
    t_by_cats = cat_trans()
    sum_by_cat = {}
    for cat in t_by_cats:
        print(cat)
        for t in t_by_cats[cat]:
            print(t)
            year = t[0][-4:]
            print(year)
            if not sum_by_cat.get(year):
                sum_by_cat[year] = {}
            if not sum_by_cat[year].get(cat[1]):
                sum_by_cat[year][cat[1]] = 0
            sum_by_cat[year][cat[1]] += t[1]
    return sum_by_cat

def cat_get():
    cur.execute("SELECT * FROM Categories")
    return cur.fetchall()

def nocat_file_make():
    cats = cat_get()
    cur.execute("SELECT payee_name FROM Payees WHERE cat_id = 1")
    no_cat_payees = cur.fetchall()
    with open("files/new_cats.csv", "w") as f:
        f.write("payee,cat")
        for p in no_cat_payees:
            f.write("\n{0}".format(p[0]))
    with open("categories_list.csv", "w") as f:
        for cat in cats:
            if cat[0] == 1:
                f.write(str(cat[0]) + "," + cat[1])
            else:
                f.write("\n" + str(cat[0]) + "," + str(cat[1]))

def cat_assign():
    with open("files/new_cats.csv") as f:
        payee_dict = csv.DictReader(f)
        for payee in payee_dict:
            if payee["cat"]:
                db_add("categories", payee["cat"])
                cat_id = id_get("categories", payee["cat"])
                cur.execute("UPDATE Payees SET cat_id={cat} WHERE payee_name='{pay}'".format(\
                    cat=cat_id, pay=payee["payee"]))
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
            heads = None
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
