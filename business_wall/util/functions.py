
def timedelta_to_hhmm(d):
    return f"{d.seconds//3600:02d}:{(d.seconds//60)%60:02d}"
