import re
import datetime


def check_contain_datefmt_text(text: str):
    checker = re.search(r'([0-9]{4}[.][0-9]{2}[.][0-9]{2})', text)
    if checker is None:
        return False
    return True


def get_datefmt_text(text: str):
    checker = re.search(r'([0-9]{4}[.][0-9]{2}[.][0-9]{2})', text)
    if checker is not None:
        return checker.group(1)


def change_steam_date_format(text: str):
    month_str2int = {'January': 1,
                     'February': 2,
                     'March': 3,
                     'April': 4,
                     'May': 5,
                     'June': 6,
                     'July': 7,
                     'August': 8,
                     'September': 9,
                     'October': 10,
                     'November': 11,
                     'December': 12}

    case1 = re.match(r'Posted: (?P<day>[0-9]{1,2}) (?P<month>[A-Za-z]+), (?P<year>[0-9]{4})', text)
    case2 = re.match(r'Posted: (?P<month>[A-Za-z]+) (?P<day>[0-9]{1,2}), (?P<year>[0-9]{4})', text)

    if (case1 is not None) and (case2 is None):
        time_info = case1.groupdict()
    elif (case2 is not None) and (case1 is None):
        time_info = case2.groupdict()
    else:
        raise Exception(f'Text [{text}] is not complete date format string')

    year, month, day = int(time_info['year']), month_str2int[time_info['month']], int(time_info['day'])

    return datetime.datetime(year=year, month=month, day=day).strftime('%Y-%m-%d')
