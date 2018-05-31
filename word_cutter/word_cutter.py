import csv
from difflib import SequenceMatcher as sm

def get_similar(a, b):
    return sm(None, a, b).ratio()

list_of_payees = csv.reader(open('list_of_payees.csv'))
final_payees = []
places = ["cardiff", "porth", "caerphilly", "ponty", "pontypridd",
          "swansea", "hove", "brighton", "wales", "caernarfon", "uk"]
for payee in list_of_payees:
    paypal = False
    formated_payee = payee[0].lower()
    if "android" in formated_payee:
        formated_payee = formated_payee[:formated_payee.index("android")]
    if "paypal" in formated_payee:
        paypal = True
        formated_payee = formated_payee[formated_payee.index("*") + 1:]
    if "pp" in formated_payee[:3]:
        formated_payee = formated_payee[formated_payee.index("*") + 1:]
    if "contactless" in formated_payee:
        formated_payee = formated_payee[:formated_payee.index(" contactless")]
    good_list = []
    for word in  formated_payee.split():
        if len(word) > 2:
            good_list.append(word)
    formated_payee = " ".join(good_list)
    bad_number = ""
    for char in formated_payee:
        try:
            integer = int(char)
        except ValueError:
            continue
        else:
            bad_number = char
            break
    if bad_number:
        if formated_payee.index(bad_number) > 0:
            if formated_payee[formated_payee.index(bad_number) - 1] == " ":
                formated_payee = formated_payee[:formated_payee.index(bad_number)]
    for place in places:
        last_word = formated_payee.rsplit(None, 1)
        while get_similar(last_word[-1], place) > 0.67 and len(last_word) > 1:
            formated_payee = formated_payee[:(len(last_word[-1]) + 1)*(-1)]
            last_word = formated_payee.rsplit(None, 1)
    if formated_payee:
        if not final_payees:
            final_payees.append(formated_payee)
        elif formated_payee not in final_payees:
            exists = False
            for pay in final_payees:
                sim = get_similar(formated_payee, pay)
                if sim > 0.75:
                    # print(formated_payee + " is " + str(sim) + " similar to " + pay)
                    exists = True
                    break
            # for word in formated_payee.split():
            #     if word != "the" and word != "of" and word != "plc":
            #         for payee in final_payees:
            #             for p in payee.split():
            #                 sim = similar(word, p)
            #                 if sim > 0.89:
            #                     print(word + " is " + str(sim) + " similar to " + p)
            #                     exists = True
            #                     break
            if not exists:
                final_payees.append(formated_payee)
print("Total Payees: " + str(len(final_payees)))
final_payees = sorted(final_payees)
for payee in final_payees:
    print(payee)
