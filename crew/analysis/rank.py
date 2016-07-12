from crew.models import *
import pandas as pd
import numpy as np
from pandas import DataFrame, Series


def rank_series(series):
    return series.rank(method='min', numeric_only=False, na_option='bottom', ascending=False).astype(np.int)


def rank_df(df, subject_columns):
    return pd.DataFrame({
                            ('rank_class', subject): rank_series(df[('score', subject)]) for subject in subject_columns
                            }, dtype=np.int)


class AnalysisError(Exception):
    pass


def load_records(exam, semester, subjects, students):
    subject_df = pd.DataFrame(
        index=[subject.id for subject in subjects],
        data={'subject': [subject.name for subject in subjects]},
    )

    student_df = pd.DataFrame.from_records(
        index=[s.id for s in students],
        data={
            'student_id': [s.student_id for s in students],
            'exam_id': [s.student_id for s in students],
            'name': [s.name for s in students],
            'school': [s.get_school_display() for s in students],
            'grade': [s.get_grade_idx_display() for s in students],
            'class_idx': [s.class_idx for s in students],
            'prop': [s.get_prop_display() for s in students],
        }
    )
    if len(students) == 0:
        raise AnalysisError("没有数据")

    records = Record.objects.filter(exam=exam, semester=semester, subject__in=subjects, student__in=students)
    if len(records) == 0:
        raise AnalysisError("没有数据")
    record_df = pd.DataFrame.from_records(
        records.values('student_id', 'subject_id', 'score'),
    ).merge(subject_df, left_on='subject_id', right_index=True)
    record_df.drop(['subject_id'], axis=1, inplace=True)
    record_df.set_index(['student_id', 'subject'], inplace=True)
    record_df = record_df.unstack(-1)
    record_df['score', '总分'] = record_df.sum(axis=1)

    subject_columns = list(record_df['score'].columns)

    df = pd.merge(student_df, record_df, left_index=True, right_index=True, how='outer')
    return df, subject_columns


def stat_rank(df, subject_columns):
    for subject in subject_columns:
        df['rank_school', subject] = rank_series(df['score', subject])
    rank_class = df.groupby(['class_idx', 'school']).apply(rank_df, subject_columns=subject_columns)
    return pd.merge(df, rank_class, left_index=True, right_index=True)
