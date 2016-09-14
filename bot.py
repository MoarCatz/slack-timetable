from urllib.request import urlopen
from datetime import datetime
#from slacker import Slacker
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

    months = {'ЯНВАРЯ':   1,
              'ФЕВРАЛЯ':  2,
              'МАРТА':    3,
              'АПРЕЛЯ':   4,
              'МАЯ':      5,
              'ИЮНЯ':     6,
              'ИЮЛЯ':     7,
              'АВГУСТА':  8,
              'СЕНТЯБРЯ': 9,
              'ОКТЯБРЯ': 10,
              'НОЯБРЯ':  11,
              'ДЕКАБРЯ': 12}

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
    page = urlopen('https://moarcatz.github.io/slack-timetable/').read().decode()
    log.info('fetch successful')
    date_match = re.search('ИЗМЕНЕНИЯ В РАСПИСАНИИ НА ([А-Я]+), ([0-9]+) ([А-Я]+)', page)
    try:
        wkday, day, month = date_match.group(1, 2, 3)
    except AttributeError:
        log.error('table invalid, quitting')
        pass

    change_date = datetime(curr_date.year,
                           months[month],
                           int(day))

    if change_date < curr_date:
        log.info('table outdated, quitting')
        return

    changes10_match = re.search('<h2>10Е</h2>\s+?<p>([^<]+)', page)
    changes11_match = re.search('<h2>11Е</h2>\s+?<p>([^<]+)', page)

    if changes10_match:
        changes10 = changes10_match.group(1).replace('&nbsp;&mdash;', ' -')
        log.info('update for 10 found')
        log.debug('update:\n' + changes10_match.group(1))
    else:
        changes10 = ''
        log.info('no updates for 10')

    if changes11_match:
        changes11 = changes11_match.group(1).replace('&nbsp;&mdash;', ' -')
        changes11 = '*11Е*\n' + changes11
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

main()