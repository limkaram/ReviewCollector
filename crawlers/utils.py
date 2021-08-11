import re


def check_contain_datefmt_text(text):
    checker = re.search(r'([0-9]{4}[.][0-9]{2}[.][0-9]{2})', text)
    if checker is None:
        return False
    return True


def get_datefmt_text(text):
    checker = re.search(r'([0-9]{4}[.][0-9]{2}[.][0-9]{2})', text)
    if checker is not None:
        return checker.group(1)