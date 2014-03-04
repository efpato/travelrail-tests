# -*- coding: utf-8 -*-

from datetime import timedelta


def next_weekday(date_from, weekday, offset=0):
    date_from = date_from + timedelta(offset)
    days_ahead = weekday - date_from.weekday()
    if days_ahead <= 0:
        days_ahead += 7
    return date_from + timedelta(days_ahead)
