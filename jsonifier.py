class TableJSONifier:
    @classmethod
    def make_field(self, cls, changes):
        return {"title": cls,
                "value": changes,
                "short": True}

    @classmethod
    def make_attachment(self, wkday, fields):
        text = "На сайте появились изменения в расписании на {}!".format(wkday)
        fld_list = [self.make_field(*fld) for fld in fields]

        atch = {"fallback": "На сайте появились изменения в расписании!",
                "color": "#36A64F",
                "text": text,
                "fields": fld_list}

        return [atch]


if __name__ == "__main__":
    tj = TableJSONifier()
    print(tj.make_attachment('понедельник', [('10Е', 'nothing'),
                                             ('11E', 'nothing')]))
