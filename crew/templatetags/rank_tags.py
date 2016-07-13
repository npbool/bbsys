from django import template

import numpy as np

register = template.Library()


@register.filter(name="rank_school")
def get_rank_school(student, subject):
    return student[('rank_school', subject)]


@register.filter(name="rank_class")
def get_rank_class(student, subject):
    return student[('rank_class', subject)]


@register.filter(name="score")
def get_score(student, subject):
    score = student[('score', subject)]
    if np.isnan(score):
        return "缺考"
    return score


@register.filter(name="score_cmp")
def get_score_cmp(student, subject):
    score = student[('score_cmp', subject)]
    if np.isnan(score):
        return "缺考"
    return score


@register.filter(name="rank_school_cmp")
def get_rank_school_cmp(student, subject):
    rank = student[('rank_school_cmp', subject)]
    return rank


@register.filter(name="rank_diff")
def get_rank_diff(student, subject):
    rank = student[('rank_diff', subject)]
    return rank


@register.filter(name='value')
def get_value(row, key):
    return row[key]
