from django import template

register = template.Library()


def format_value(val):
    if isinstance(val, int):
        return val
    elif isinstance(val, float):
        return '{0:.2f}'.format(val)
    else:
        return val


def with_subject(key):
    def inner(row, subject):
        return format_value(row[key, subject])

    return inner


def with_empty(key):
    def inner(row):
        return format_value(row[key, ''])

    return inner


first_keys = ['excellent', 'good', 'excellent_and_good', 'pass', 'mean', 'mean_rank', 'mean_diff']
for k in first_keys:
    register.filter(k, with_subject(k))

single_keys = ['school', 'class_idx']
for k in single_keys:
    register.filter(k, with_empty(k))
