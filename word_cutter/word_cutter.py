"""
This script was created to format payee names on a bank statement to make them
easier to be stored in a database. It removes part of the string that may alter the
name of the payee reducing the chance of duplicates.

This script contains 2 main functions:
format_payees_in_file
format_payee

Functions starting with "_" are support functions to be used by format_payee
"""
import csv
import re
from difflib import SequenceMatcher as sm


def _get_similarity(a, b):
    """
    :param a: string
    :param b: string
    :return: percentage similarity rate between a and b
    """
    return sm(None, a, b).ratio()


def _cut_by_word(word, cut, check=None, prefix=True, start=0, end=0):
    """
    removes part of a sentence or word
    :param word: string
    :param cut: string - part of the string to be removed
    :param check: string - part of the string that must exist in order to remove cut
    :param prefix: boolean -  true = cut is at the start of word, false = cut is at the end of word
    :param start: integer - index of starting point of word
    :param end: integer - index of ending point of word
    :return: string - word - cut if check = true
    """
    if not check:
        check = cut
    if not end:
        end = len(word)
    if prefix:
        if check in word[start:end]:
            return word[:word.index(cut)]
    else:
        if check in word[start:end]:
            return word[word.index(cut) + 1:]
    return word


def _cut_by_length(words, length):
    """
    removes small words from sentences
    :param words: string - sentence to have words removes from
    :param length: integer - max number of letters in words to be removed
    :return: string - words - word where len(word) <= length
    """
    new_words = []
    for word in words:
        if len(word) > length:
            new_words.append(word)
    return " ".join(new_words)


def _cut_by_numbers(word):
    """
    removes integers from string
    :param word: string
    :return: string - word - numbers
    """
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
    """
    removes words fromstring that matches words on list
    :param word: string
    :return: string - word - places
    """
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
    """
    identifies if item is already on list and appends it if not
    :param list: list - original list of items
    :param item: string (hashable element) - item to be added to list
    :param similarity: float - number between 0 and 1, 1 being identical
    :return: list - with new item appended or not
    """
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
    """
    creates a list of strings from a column on a csv file
    :param file: string - csv filepath
    :param header: optional string - the header of the csv file that contains the words to be stripped and listed
    :return: list of strings
    """
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


def _cut_bad_characters(words):
    """
    removes expressions from string
    :param word: string
    :return: string - unformatted
    """
    word_list = words.split()
    final_word_list = []
    for word in word_list:
        final_word = re.sub(r"[\W]", "", word)
        final_word_list.append(final_word)
    return " ".join(final_word_list)


def format_payee(payee):
    """
    used to strip payee names from characters and arrive to a common payee name
    :param payee: string
    :return: string formatted
    """
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
