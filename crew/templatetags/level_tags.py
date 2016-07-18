from .average_tags import *


@register.filter(name='value')
def get_value(row, key):
    return row[key]


for k in ['max_score', 'valid_count', 'total_count', 'level_a_count', 'level_a_ratio', 'level_a_rank', 'level_b_count',
          'level_b_ratio', 'level_b_rank']:
    register.filter(k, with_subject(k))
