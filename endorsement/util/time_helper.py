from datetime import date, datetime, timedelta
import pytz
from django.utils import timezone
from restclients.util.timer import Timer


def get_datetime_now(tz_aware=False):
    """
    @return the local timezone awared datetime object if tz_aware is True,
    otherwise return a datetime object.
    """
    now = datetime.now()
    if tz_aware:
        return local_tz.localize(now.astimezone(pytz.utc))
    return now
