class InvalidMonth(Exception):
    def __str__(self):
        return u'Number of month not within valid range!'

def get_season_name_by_month(mon):
    if mon in (12,1,2):
        seas = 'DJF'
    elif mon in (3,4,5):
        seas = 'MAM'
    elif mon in (6,7,8):
        seas = 'JJA'
    elif mon in (9,10,11):
        seas = 'SON'
    else:
        raise InvalidMonth

    return seas
