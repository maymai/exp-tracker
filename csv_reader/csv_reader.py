"""
This script takes a csv file and uses its contents to create a list of
dictionaries representing transactions.

CSV files used are based on nationwide bank statements. Headers are hardcoded
 on _remove_existing function.

 This script's main function is
 write_csv - which creates a new csv with all transactions gathered as well as
 return a list of dictionaries with the same transactions
"""
import csv
import re
import os
import pickle
from word_cutter import word_cutter


def _read_csv(file):
    """
    :param file: string - filepath with or without ".csv"
    :return: iterator - of rows in the file as dictionaries
    """
    if file[-4:] != ".csv":
        file += ".csv"
    return csv.DictReader(open(file))


def fix_file(file):
    """
    makes a csv file compliant with script
    removes any rows before initial headers
    replaces original file with edited one
    :param file: string - csv filepath
    """
    with open(file, newline='') as csvfile:
        final_list = []
        r = csv.reader(csvfile, delimiter=',', quotechar='|')
        start = False
        while not start:
            row = r.__next__()
            if row:
                if "Date" in row[0]:
                    start = True
                    final_list.append(row)
        for row in r:
            final_list.append(row)
    with open(file, "w") as f:
        for row in final_list:
            f.write(",".join(row) + "\n")


def _fix_headers(transaction_list):
    """
    removes whitespace strings from headers and removes unused fields from transaction
    :param transaction_list: list of dictionaries
    :return: list of dictionaries with normalised headers, header that contain payee description
    """
    new_transaction_list = []
    payee_header = None
    for transaction in transaction_list:
        new_transaction = {}
        if transaction.get("Description"):
            remove = "Transaction type"
            payee_header = "Description"
        elif transaction.get("Transactions"):
            remove = "Location"
            payee_header = "Transactions"
        elif transaction.get("Name"):
            remove = None
            payee_header = "Name"
        else:
            return None
        for item in transaction:
            if item != remove:
                new_transaction[re.sub("ï»¿", "", item)] = re.sub("Â", "", transaction[item]).lstrip()
        new_transaction_list.append(new_transaction)
    return new_transaction_list, payee_header


def _get_transactions_list(file):
    """
    reads a file and return a dictionary with header:row values
    :param file: string - filepath with or without ".csv"
    :return: list of dictionaries (header:value) for each row on csv file with
    headers formatted, header that contain payee description
    """
    transactions = []
    reader = _read_csv(file)
    for row in reader:
        transactions.append(dict(row))
    transactions, payee_header = _fix_headers(transactions)
    return transactions, payee_header


def _merge_transactions(old_transactions, new_transactions):
    """
    takes 2 lists of dictionaries, rename headers to match, remove duplicates and
    return 1 list of dictionaries
    :param old_transactions: list of dictionaries or string with csv filepath
        (csv created by this script previously)
    :param new_transactions: list of dictionaries or string with csv filepath
        (csv containing new statement for processing)
    :return: list of dictionaries
    """
    # verifying new and old transactions
    new_payee_header = None
    if type(old_transactions) == str:
        old_transactions, old_payee_header = _get_transactions_list(old_transactions)
    elif type(old_transactions) != list:
        return None
    if type(new_transactions) == str:
        new_transactions, new_payee_header = _get_transactions_list(new_transactions)
    elif type(new_transactions) != list:
        return None
    # change headers to match
    old_new_realtionship = {"Date": "Date", "Name": new_payee_header, "Paid in": "Paid in", "Paid out": "Paid out"}
    new_h_trans = []
    for trans in new_transactions:
        h_trans = {}
        for h in old_new_realtionship:
            h_trans[h] = trans.get(old_new_realtionship[h])
        new_h_trans.append(h_trans)
    # format new payees
    for transaction in new_h_trans:
        transaction["Name"] = word_cutter.format_payee(transaction["Name"])
    # create new list with all old transactions and append only new transactions
    final_transactions = old_transactions.copy()
    for n in new_h_trans:
        add_me = True
        for existing_trans in final_transactions:
            if n == {"Name": existing_trans["Name"], "Date": existing_trans["Date"],
                     "Paid in": existing_trans["Paid in"], "Paid out": existing_trans["Paid out"]}:
                # have to specify keys since some may have the extra key 'Pay category'
                add_me = False
                break
        if add_me:
            final_transactions.append(n)
    # add category key to payees
    for transaction in final_transactions:
        if not transaction.get("Pay category"):
            payee = transaction.get("Name")
            for t in final_transactions:
                if word_cutter.get_similarity(t["Name"], payee) > 0.75 and t.get("Pay category"):
                    transaction["Pay category"] = t["Pay category"]
                    break
            if not transaction.get("Pay category"):
                transaction["Pay category"] = ""
    return final_transactions


def create_final_transaction_list(new_file):
    """
    duplicates _merge_transactions looks for previously created csv and final list is
    written on csv file
    :param new_file: string - bank statement csv filepath
    :return: list of dictionaries
    """
    filename = "final_transactions.csv"
    if not os.path.isfile(filename):
        old_file = []
    else:
        old_file = filename
    final_transactions = _merge_transactions(old_file, new_file)
    if final_transactions:
        with open(filename, "w", newline='') as file:
            headers = list(final_transactions[0].keys())
            headers.sort()
            writer = csv.DictWriter(file, fieldnames=headers)
            writer.writeheader()
            for transaction in final_transactions:
                writer.writerow(transaction)
    _set_categories(filename)
    return final_transactions


def _set_categories(filename):
    """
    review transactions csv and create a category: list of payees dictionary
    which is saved on a pickle file
    :return: categories dictionary
    """
    pickle_file = "categories"
    if not os.path.isfile(pickle_file):
        categories = {}
    else:
        with open(pickle_file, "rb") as pf:
            categories = pickle.load(pf)
    transactions = _read_csv(filename)
    for transaction in transactions:
        if transaction["Pay category"]:
            if not categories.get(transaction["Pay category"]):
                categories[transaction["Pay category"]] = [transaction["Name"]]
            else:
                if transaction["Name"] not in categories[transaction["Pay category"]]:
                    add_me = True
                    for payee in categories[transaction["Pay category"]]:
                        if word_cutter.get_similarity(payee, transaction["Name"]) > 0.80:
                            add_me = False
                            break
                    if add_me:
                        categories[transaction["Pay category"]].append(transaction["Name"])
    for cat in categories:
        print(cat + ": " + str(categories[cat]))
    with open(pickle_file, "wb") as pf:
        pickle.dump(categories, pf)
