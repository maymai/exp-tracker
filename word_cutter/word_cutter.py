import csv
import re
from difflib import SequenceMatcher as sm

def _get_similarity(a, b):
    return sm(None, a, b).ratio()

def _cut_by_word(word, cut, check=None, prefix=True, start=0, end=0):
    if not check: check = cut
    if not end: end = len(word)
    if prefix:
        if check in word[start:end]:
            return word[:word.index(cut)]
    else:
        if check in word[start:end]:
            return word[word.index(cut) + 1:]
    return word

def _cut_by_length(words, length):
    new_words = []
    for word in words:
        if len(word) > length:
            new_words.append(word)
    return " ".join(new_words)

def _cut_by_numbers(word):
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

def _cut_by_place(word):
    words = word.split()
    last_word = words[-1]
    places = ["cardiff", "porth", "caerphilly", "ponty", "pontypridd",
              "swansea", "hove", "brighton", "wales", "caernarfon", "uk", "bangor"]
    for place in places:
        while _get_similarity(last_word, place) > 0.67 and len(words) > 1:
            words.remove(last_word)
            last_word = words[-1]
    return " ".join(words)

def _add_individual_items_to_list(list, item, similarity=0.75):
    if not list:
        list.append(item)
    elif item not in list:
        exists = False
        for i in list:
            if _get_similarity(item, i) > similarity:
                exists = True
                break
        if not exists:
            list.append(item)
    return list

def format_payees_in_file(file, header=None):
    if file[-4:] != ".csv":
        file += ".csv"
    final_list = []
    if header:
        list_of_items = csv.DictReader(open(file))
    else:
        list_of_items = csv.reader(open(file))
    for row in list_of_items:
        if header:
            item = row[header]
        else:
            item = row[0]
        formatted_item = format_payee(item)
        final_list = _add_individual_items_to_list(final_list, formatted_item)
    final_list = sorted(final_list)
    return final_list

def _cut_bad_characters(word):
    return re.sub(r"[\W]", "", word)

def format_payee(payee):
    formatted_item = payee.lower()
    formatted_item = _cut_by_word(formatted_item, "android")
    formatted_item = _cut_by_word(formatted_item, "*", "paypal", False)
    formatted_item = _cut_by_word(formatted_item, "*", "pp", False, end=3)
    formatted_item = _cut_by_word(formatted_item, " contactless")
    formatted_item = _cut_by_length(formatted_item.split(), 2)
    formatted_item = _cut_by_numbers(formatted_item)
    formatted_item = _cut_by_place(formatted_item)
    formatted_item = _cut_bad_characters(formatted_item)
    return formatted_item.capitalize()
