
from datetime import datetime, timedelta


def divide_timedeltas(td1,td2):
    return td1.total_seconds()/td2.total_seconds()


def floor_granule_datetime(t, granulation, offset=timedelta(minutes=0)):
    t0 = datetime(year=t.year,month=t.month,day=t.day)
    t1 = t0 + offset
    d = t - t1
    
    floored = t1 + int( divide_timedeltas(d, granulation) )*granulation

    return floored
