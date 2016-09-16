import json, os, requests

class OneSignal:
    @classmethod
    def send(self, cls, change, wkday):
        self.header = {"Content-Type": "application/json",
                       "Authorization": str(os.environ['ONESIGNAL_AUTHORIZATION'])}

        self.payload = {"app_id": str(os.environ['ONESIGNAL_APP_ID']),
                        "included_segments": [cls],
                        "headings": {"en": "Timetable"},
                        "contents": {"en": "Появились изменения для " + cls +
                                     " на " + wkday + ": " + change}}

        self.req = requests.post("https://onesignal.com/api/v1/notifications",
                   headers = self.header,
                   data = json.dumps(self.payload))
