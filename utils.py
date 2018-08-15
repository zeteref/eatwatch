from datetime import datetime

def today_at(hour):
    now = datetime.now()
    hour, minute = [int(x) for x in  hour.split(':')]

    ret = datetime(now.year, now.month, now.day, hour, minute)
    return ret

class extracted(tuple):

    def first(self):
        if len(self) < 1:
            return None

        return self[0]


    def refine(self, func):
        return extracted(func(x) for x in self)


def extract(iterable, func=lambda x: True if x is not None else False):
    return extracted(x for x in iter(iterable) if func(x))


def first(iterable, func=lambda x: True if x is not None else False):
    return extract(iterable, func).first()
