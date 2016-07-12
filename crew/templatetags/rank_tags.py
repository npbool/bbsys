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
