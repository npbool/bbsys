from django import template

register = template.Library()


def with_subject(key):
    def inner(row, subject):
        return '{0:.2f}'.format(row[key, subject])

    return inner


def with_empty(key):
    def inner(row):
        return row[key, '']

    return inner


first_keys = ['excellent', 'good', 'excellent_and_good', 'pass', 'mean', 'rank_mean', 'mean_diff']
for k in first_keys:
    register.filter(k, with_subject(k))

single_keys = ['school', 'class_idx']
for k in single_keys:
    register.filter(k, with_empty(k))
