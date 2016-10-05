import json, os, requests

class SendingFailure(Exception):
    def __init__(self, cls):
        self.cls = cls


class OneSignal:
    @classmethod
    def send(self, cls, change, wkday):
        self.header = {"Content-Type": "application/json",
                       "Authorization": str(os.environ['ONESIGNAL_AUTHORIZATION'])}

        self.payload = {"app_id": str(os.environ['ONESIGNAL_APP_ID']),
                        "included_segments": [cls],
                        "headings": {"en": "Timetable"},
                        "contents": {"en": "Появились изменения для " + cls +
                                     " на " + wkday + ": " + change},
                        "url": "http://lyceum.urfu.ru/study/izmenHtml.php"
                        }

        self.req = requests.post("https://onesignal.com/api/v1/notifications",
                   headers = self.header,
                   data = json.dumps(self.payload))

        if self.req.status_code != requests.codes.ok:
            raise SendingFailure(cls)
