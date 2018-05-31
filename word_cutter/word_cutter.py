import csv
from difflib import SequenceMatcher as sm

def get_similarity(a, b):
    return sm(None, a, b).ratio()

def cut_by_word(word, cut, check=None, prefix=True, start=0, end=0):
    if not check: check = cut
    if not end: end = len(word)
    if prefix:
        if check in word[start:end]:
            return word[:word.index(cut)]
    else:
        if check in word[start:end]:
            return word[word.index(cut) + 1:]
    return word

def cut_by_length(words, length):
    new_words = []
    for word in words:
        if len(word) > length:
            new_words.append(word)
    return " ".join(new_words)

def cut_by_numbers(word):
    number = ""
    for char in word:
        try:
            integer = int(char)
        except ValueError:
            continue
        else:
            number = char
            break
    if number:
        if word.index(number) > 0:
            if word[word.index(number) - 1] == " ":
                return word[:word.index(number)]
    return word

def cut_by_place(word):
    words = word.split()
    last_word = words[-1]
    places = ["cardiff", "porth", "caerphilly", "ponty", "pontypridd",
              "swansea", "hove", "brighton", "wales", "caernarfon", "uk"]
    for place in places:
        while get_similarity(last_word, place) > 0.67 and len(words) > 1:
            words.remove(last_word)
            last_word = words[-1]
    return " ".join(words)

def add_to_list(list, item, similarity=0.75):
    if not list:
        list.append(item)
    elif item not in list:
        exists = False
        for i in list:
            if get_similarity(item, i) > similarity:
                exists = True
                break
        if not exists:
            list.append(item)
    return list

def format_strings(file, header=None):
    if file[-4:] != ".csv":
        file += ".csv"
    list_of_items = csv.reader(open(file))
    final_list = []
    for row in list_of_items:
        if header:
            item = row[header]
        else:
            item = row
        formated_item = item[0].lower()
        formated_item = cut_by_word(formated_item, "android")
        formated_item = cut_by_word(formated_item, "*", "paypal", False)
        formated_item = cut_by_word(formated_item, "*", "pp", False, end=3)
        formated_item = cut_by_word(formated_item, " contactless")
        formated_item = cut_by_length(formated_item.split(), 2)
        formated_item = cut_by_numbers(formated_item)
        formated_item = cut_by_place(formated_item)
        final_list = add_to_list(final_list, formated_item)
    print("Total Payees: " + str(len(final_list)))
    final_list = sorted(final_list)
    for item in final_list:
        print(item)

format_strings("list_of_payees")