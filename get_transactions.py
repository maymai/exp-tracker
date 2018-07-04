"""
This script reads all files from 'Statements' folder and merge
transactions into one dictionary and csv file removing any duplicates.

Duplicates are transactions that have the same date, payee and value.
"""
import os
from csv_reader import csv_reader


def get_transactions():
    """
    looks for all files in statements folder and aggregate them to transaction list and csv file
    :return: list of dictionaries
    """
    if not os.path.exists("statements/"):
        os.makedirs("statements/")
    files = [f for f in os.listdir("statements") if os.path.isfile(os.path.join("statements", f))]
    transaction_list = []
    for file in files:
        print(file)
        file = "statements/" + file
        csv_reader.fix_file(file)
        transaction_list = csv_reader.create_final_transaction_list(file)
        os.remove(file)
    return transaction_list


get_transactions()
