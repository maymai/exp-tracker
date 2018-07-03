import csv
import re
import datetime
from word_cutter import word_cutter

def _read_csv(file):
    if file[-4] != ".csv":
        file += ".csv"
    return csv.DictReader(open(file))

def _fix_headers(transaction_list):
    new_transaction_list = []
    for transaction in transaction_list:
        new_transaction = {}
        for item in transaction:
            new_transaction[re.sub("ï»¿", "", item)] = re.sub("Â", "", transaction[item]).lstrip()
        new_transaction_list.append(new_transaction)
    return new_transaction_list

def _get_transactions_list(file):
    transactions = []
    reader = _read_csv(file)
    for row in reader:
        transactions.append(dict(row))
    transactions = _fix_headers(transactions)
    return transactions

def _remove_existing(new_list, payee_header, old_list=None):
    old_new_realtionship = {"Date": "Date", "Name": payee_header, "In": "Paid in", "Out": "Paid out"}
    new_transactions = []
    for transaction in new_list:
        new_transaction = {}
        transaction[payee_header] = word_cutter.format_payee(transaction[payee_header])
        if old_list:
            for old in old_list:
                for h in old_new_realtionship:
                    if old[h] == transaction[old_new_realtionship[h]]:
                        break
                    new_transaction[h] = transaction[old_new_realtionship[h]]
                if old["Name"] == transaction[payee_header]:
                    new_transaction["Category"] = old["Category"]
                else:
                    new_transaction["Category"] = ""
        else:
            for h in old_new_realtionship:
                new_transaction[h] = transaction[old_new_realtionship[h]]
                new_transaction["Category"] = ""
        new_transactions.append(new_transaction)
    return new_transactions

# Make a function to merge transactions into one list
# Update function below to just write it to a file

def write_csv(new_file, payee_header, old_file=None):
    if old_file:
        old_list = _get_transactions_list(old_file)
    else:
        old_list = []
    new_list = _get_transactions_list(new_file)
    new_list = _remove_existing(new_list, payee_header, old_list)
    filename = datetime.datetime.utcnow().strftime("%Y%m%d_%H%M") + ".xls"
    with open(filename, "w", newline='') as file:
        if old_list:
            headers = old_list[0].keys()
        else:
            headers = new_list[0].keys()
        writer = csv.DictWriter(file, fieldnames=headers)
        writer.writeheader()
        for transaction in old_list:
            writer.writerow(transaction)
        for transaction in new_list:
            writer.writerow(transaction)
    return old_list + new_list
