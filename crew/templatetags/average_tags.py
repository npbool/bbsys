from django import template
import pandas as pd
register = template.Library()


def format_value(val):
    if isinstance(val, int):
        return val
    elif isinstance(val, float):
        if pd.isnull(val):
            return ''
        return '{0:.2f}'.format(val)
    else:
        return str(val)


def with_subject(key):
    def inner(row, subject):
        return format_value(row[key, subject])

    return inner


def with_empty(key):
    def inner(row):
        if (key,'') in row:
            value = row[key, '']
        else:
            value = row[key]
        return format_value(value)

    return inner


first_keys = ['excellent', 'good', 'excellent_and_good', 'pass', 'mean', 'mean_rank', 'mean_diff', 'rank_rise']
for k in first_keys:
    register.filter(k, with_subject(k))

single_keys = ['school', 'class_idx', 'grade']
for k in single_keys:
    register.filter(k, with_empty(k))

register.filter("manager", with_empty("班主任"))
