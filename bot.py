from urllib.request import urlopen
from datetime import datetime
from slacker import Slacker
import logging, os, re

def main():
    log_level = logging.DEBUG

    log = logging.Logger('bot')
    log.setLevel(log_level)

    log_handler = logging.StreamHandler()
    log_handler.setLevel(log_level)

    log_fmt = logging.Formatter('[{asctime}] [{levelname}]\n{message}\n',
                                datefmt = '%d-%m %H:%M:%S', style = '{')
    log_handler.setFormatter(log_fmt)

    log.addHandler(log_handler)

    log.info('starting up')

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
            log.info('already up-to-date, quitting')
            log.debug('latest update sent for ' +
                      changes_sent.strftime('%d-%m-%Y'))
            return

    log.info('fetching table page')
    page = urlopen('http://lyceum.urfu.ru/study/izmenHtml.php').read().decode('cp1251')
    log.info('fetch successful')
    date_match = re.search('ИЗМЕНЕНИЯ В РАСПИСАНИИ НА [А-Я]+, ([0-9]+) ([А-Я]+)', page)
    try:
        day, month = date_match.group(1, 2)
    except IndexError:
        log.error('table invalid, quitting')
        return

    change_date = datetime(curr_date.year,
                           months[month],
                           day)

    if change_date < curr_date:
        log.info('table outdated, quitting')
        return

    changes10_match = re.search('<h1>10Е</h1>\n([^<]+)', page)
    changes11_match = re.search('<h1>11Е</h1>\n([^<]+)', page)

    if changes10_match:
        changes10 = ('*10Е*\n' + changes10_match.group(1))
        log.info('update for 10 found')
        log.debug('update:\n' + changes10_match.group(1))
    else:
        changes10 = ''
        log.info('no updates for 10')

    if changes11_match:
        changes11 = ('*11Е*\n' + changes11_match.group(1))
        log.info('update for 11 found')
        log.debug('update:\n' + changes11_match.group(1))
    else:
        changes11 = ''
        log.info('no updates for 11')

    log.info('generating a message to Slack')
    message = (changes10 + '\n' + changes11 + '\n').strip()
    log.debug('message:\n' + message)

    with open('changes.txt', 'w') as f:
        log.info('setting a new timestamp in changes.txt')
        f.write(str(int(change_date.timestamp())))


    # Create a Slack bot instance
    slack = Slacker(str(os.environ['SLACK_API_TOKEN']))

    # Send a message to #general channel
    log.info('sending a message to Slack')
    slack.chat.post_message('#general',
                            'Привет! На сайте появились изменения в расписании:\n' + message,
                            username = 'timetable',
                            icon_emoji = ':spiral_calendar_pad:')

    log.info('success, quitting')
