from urllib.request import urlopen
from urllib.error import URLError
from urllib.parse import urlparse
from datetime import datetime
from slacker import Slacker
from jsonifier import TableJSONifier
from onesignal import OneSignal, SendingFailure
import logging, psycopg2, os, re

class TimetableBot:
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

    def connect(self):
        """Connects to the database"""
        self.url = urlparse(os.environ["DATABASE_URL"])
        self.log.info('connecting to the database')
        self.db = psycopg2.connect(database=self.url.path[1:],
                                   user=self.url.username,
                                   password=self.url.password,
                                   host=self.url.hostname,
                                   port=self.url.port)

        self.log.info('connection established')

    def get_table_page(self, addr, enc):
        """Gets the changes page's content"""
        self.log.info('fetching table page')
        page = urlopen(addr).read().decode(enc)
        self.log.info('fetch successful')
        return page

    def parse_header(self, page):
        """Checks the header in the changes page
        and retrieves the date"""
        header = re.search('ИЗМЕНЕНИЯ В РАСПИСАНИИ НА ([А-Я]+), ([0-9]+) ([А-Я]+)', page)
        if not header:
            return False
        self.wkday, self.day, self.month = header.group(1, 2, 3)
        self.wkday = self.wkday.lower()
        return True

    def parse_changes(self, page):
        """Returns a list of changes for both E classes
        (if they're present)"""
        c = self.db.cursor()
        c.execute('''SELECT classes FROM changes''')
        done = set(c.fetchone())

        changes_e = []
        changes = re.findall(r'<h2>([0-9]{1,2}[А-Са-с])<\/h2>\s*<p>((\n|.)+?)(?=(<\/body>|<h2>|<h1>))', page)
        for i in changes:
            cls, chg = i[:2]
            cls = cls.upper()
            if cls in done:
                continue
            chg = chg.strip().replace('<p>', '')
            chg = chg.replace('</p>', '')
            chg = chg.replace('&nbsp;&mdash;', ' –')
            if cls in ('10Е', '11Е'):
                changes_e.append((cls, chg))
            self.log.info('found updates for ' + cls)
            self.log.info('sending push for ' + cls)
            try:
                OneSignal.send(cls, chg.replace('\r\n', ', '), self.wkday)
                done.add(cls)
            except SendingFailure as e:
                self.log.error('failed to send updates for', e.cls)

        c.execute('''UPDATE changes SET classes = %s''', (list(done),))
        c.close()
        self.db.commit()

        return changes_e

    def send_slack(self, attachments):
        """Sends a message to Slack"""
        # Create a Slack bot instance
        slack = Slacker(os.environ['SLACK_API_TOKEN'])

        # Send a message to #general channel
        self.log.info('sending a message to Slack')
        slack.chat.post_message('#general',
                                text = ' ',
                                username = 'timetable',
                                icon_emoji = ':spiral_calendar_pad:',
                                attachments = attachments)

    def reset_sent_classes(self):
        c = self.db.cursor()
        self.log.info('resetting the classes that have received notifications')
        c.execute('''UPDATE changes SET classes = ARRAY[]::text[]''')
        c.close()

        self.db.commit()

    def run(self):
        self.log.info('starting up')

        self.connect()

        try:
            self.page = self.get_table_page(os.environ['TIMETABLE_URL'],
                                            os.environ['TIMETABLE_ENC'])
        except URLError:
            self.log.error('failed to fetch page, quitting')
            return
        except UnicodeDecodeError:
            self.log.error('failed to decode page content, quitting')
            return

        if not self.parse_header(self.page):
            self.log.error('table invalid, quitting')
            return

        self.change_date = datetime(self.curr_date.year,
                                    self.months[self.month],
                                    int(self.day))

        if self.change_date < self.curr_date:
            self.reset_sent_classes()
            self.log.info('table outdated, quitting')
            return

        self.changes_e = self.parse_changes(self.page)

        if self.changes_e:
            self.log.info('generating JSON message')
            atch = TableJSONifier.make_attachment(self.wkday,
                                                  self.changes_e)
            self.send_slack(atch)

        self.db.close()
        self.log.info('success, quitting')

TimetableBot().run()
