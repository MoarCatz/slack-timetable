from urllib.request import urlopen
from datetime import datetime
from slacker import Slacker
import os, re

def main():
    months = {'ЯНВАРЯ':   0,
              'ФЕВРАЛЯ':  1,
              'МАРТА':    2,
              'АПРЕЛЯ':   3,
              'МАЯ':      4,
              'ИЮНЯ':     5,
              'ИЮЛЯ':     6,
              'АВГУСТА':  7,
              'СЕНТЯБРЯ': 8,
              'ОКТЯБРЯ':  9,
              'НОЯБРЯ':  10,
              'ДЕКАБРЯ': 11}

    curr_date = datetime.now()

    with open('changes.txt') as f:
        tm = int(f.read())
        changes_sent = datetime.fromtimestamp(tm)
        if changes_sent > curr_date:
            return

    page = urlopen('http://lyceum.urfu.ru/study/izmenHtml.php').read().decode('cp1251')
    date_match = re.search('ИЗМЕНЕНИЯ В РАСПИСАНИИ НА [А-Я]+, ([0-9]+) ([А-Я]+)', page)
    try:
        day, month = date_match.group(1, 2)
    except IndexError:
        return

    change_date = datetime(curr_date.year,
                           months[month],
                           day)

    if change_date < curr_date:
        return

    changes10_match = re.search('<h1>10Е</h1>\n([^<]+)', page)
    changes11_match = re.search('<h1>11Е</h1>\n([^<]+)', page)

    changes10 = ('*10Е*\n' + changes10_match.group(1)) if changes10_match else ''
    changes11 = ('*11Е*\n' + changes11_match.group(1)) if changes11_match else ''

    message = (changes10 + '\n' + changes11 + '\n').strip()

    with open('changes.txt', 'w') as f:
        f.write(str(int(change_date.timestamp())))

    # Create a Slack bot instance
    slack = Slacker(str(os.environ['SLACK_API_TOKEN']))

    # Send a message to #general channel
    slack.chat.post_message('#general',
                            'Привет! На сайте появились изменения в расписании:\n' + message,
                            username = 'timetable',
                            icon_emoji = ':spiral_calendar_pad:')
