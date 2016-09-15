from urllib.request import urlopen
from urllib.error import URLError
from datetime import datetime
from slacker import Slacker
from jsonifier import TableJSONifier
import logging, os, re

class TimeTableBot:
    months = {'ЯНВАРЯ':    1,
              'ФЕВРАЛЯ':   2,
              'МАРТА':     3,
              'АПРЕЛЯ':    4,
              'МАЯ':       5,
              'ИЮНЯ':      6,
              'ИЮЛЯ':      7,
              'АВГУСТА':   8,
              'СЕНТЯБРЯ':  9,
              'ОКТЯБРЯ':  10,
              'НОЯБРЯ':   11,
              'ДЕКАБРЯ':  12}

    curr_date = datetime.now()

    # Set up logging
    log_level = logging.DEBUG

    log = logging.Logger('bot')
    log.setLevel(log_level)

    log_handler = logging.StreamHandler()
    log_handler.setLevel(log_level)

    log_fmt = logging.Formatter('[{asctime}] [{levelname}]\n{message}\n',
                                datefmt = '%d-%m %H:%M:%S', style = '{')
    log_handler.setFormatter(log_fmt)

    log.addHandler(log_handler)


    def already_sent(self):
        """Checks if the changes were sent already"""
        tm = int(os.environ['CHANGES_TM'])
        self.changes_sent = datetime.fromtimestamp(tm)
        if self.changes_sent > self.curr_date:
            return True
        return False

    def get_table_page(self, addr, enc):
        """Gets the changes page's content"""
        self.log.info('fetching table page')
        page = urlopen(addr).read().decode(enc)
        self.log.info('fetch successful')
        return page

    def parse_header(self, page):
        """Dissects the heading in the changes page"""
        header = re.search('ИЗМЕНЕНИЯ В РАСПИСАНИИ НА ([А-Я]+), ([0-9]+) ([А-Я]+)', page)
        try:
            self.wkday, self.day, self.month = header.group(1, 2, 3)
            return True
        except AttributeError:
            return False

    def parse_changes(self, page):
        """Returns a list of changes for both classes
        (if they're present)"""
        changes_list = []
        changes = re.findall(r'<h2>(1[10]Е)<\/h2>\n<p>((\n|.)+?)(?=(<\/body>|<h2>))', page)
        for i in changes:
            cls, chg = i[:2]
            chg = chg.replace('<p>', '')
            chg = chg.replace('</p>', '')
            chg = chg.replace('&nbsp;&mdash;', ' –')
            changes_list.append((cls, chg))
            self.log.info('found updates for ' + i[0])

        return changes_list

    def set_timestamp(self, change_date):
        """Sets the new timestamp"""
        tm = str(int(change_date.timestamp()))
        self.log.info('setting a new timestamp in CHANGES_TM')
        os.environ['CHANGES_TM'] = tm

    def send(self, attachments):
        """Sends a message to Slack"""
        # Create a Slack bot instance
        slack = Slacker(str(os.environ['SLACK_API_TOKEN']))

        # Send a message to #general channel
        self.log.info('sending a message to Slack')
        slack.chat.post_message('#general',
                                text = ' ',
                                username = 'timetable',
                                icon_emoji = ':spiral_calendar_pad:',
                                attachments = attachments)

    def run(self):
        self.log.info('starting up')

        if self.already_sent():
            self.log.info('already up-to-date, quitting')
            self.log.debug('latest update sent for ' +
                           self.changes_sent.strftime('%d-%m-%Y'))

        try:
            self.page = self.get_table_page(os.environ['TIMETABLE_URL'],
                                            os.environ['TIMETABLE_ENC'])
        except URLError:
            self.log.error('failed to fetch page, quitting')
            return -1

        if not self.parse_header(self.page):
            self.log.error('table invalid, quitting')
            return -1

        self.change_date = datetime(self.curr_date.year,
                                    self.months[self.month],
                                    int(self.day))

        if self.change_date < self.curr_date:
            self.log.info('table outdated, quitting')
            return

        self.changes = self.parse_changes(self.page)

        self.log.info('generating JSON message')
        atch = TableJSONifier.make_attachment(self.wkday,
                                              self.changes)

        self.send(atch)
        self.set_timestamp(self.change_date)
        self.log.info('success, quitting')

TimeTableBot().run()
