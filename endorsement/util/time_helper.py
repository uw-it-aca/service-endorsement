from datetime import datetime
import pytz


class Timer:
    def __init__(self):
        """ Start the timer """
        self.start = self._now()

    def _now(self):
        return datetime.utcnow()

    def get_elapsed(self):
        """ Return the time spent in milliseconds """
        delta = self._now() - self.start
        return delta.microseconds / 1000.0


def get_datetime_now(tz_aware=False):
    """
    @return the local timezone awared datetime object if tz_aware is True,
    otherwise return a datetime object.
    """
    now = datetime.now()
    if tz_aware:
        return local_tz.localize(now.astimezone(pytz.utc))
    return now
