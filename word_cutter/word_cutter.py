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

def format_file(file, header=None):
    if file[-4:] != ".csv":
        file += ".csv"
    final_list = []
    list_of_items = csv.reader(open(file))
    for row in list_of_items:
        if header:
            item = row[header]
        else:
            item = row
        formatted_item = format_string(item)
        final_list = add_to_list(final_list, formatted_item)
    print("Total Payees: " + str(len(final_list)))
    final_list = sorted(final_list)
    for item in final_list:
        print(item)

def format_string(item):
    formatted_item = item[0].lower()
    formatted_item = cut_by_word(formatted_item, "android")
    formatted_item = cut_by_word(formatted_item, "*", "paypal", False)
    formatted_item = cut_by_word(formatted_item, "*", "pp", False, end=3)
    formatted_item = cut_by_word(formatted_item, " contactless")
    formatted_item = cut_by_length(formatted_item.split(), 2)
    formatted_item = cut_by_numbers(formatted_item)
    formatted_item = cut_by_place(formatted_item)
    return formatted_item

format_file("list_of_payees")