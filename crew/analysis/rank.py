from crew.models import *
import pandas as pd
import numpy as np
from pandas import DataFrame, Series
from crew.models import *
import functools
import operator
from django.db.models import Q
from crew.util import debug_print


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


def stat_rank_cmp(df, sc, df_cmp, sc_cmp):
    sc_common = [s for s in sc if s in sc_cmp]

    for subject in sc_common:
        df['rank_school', subject] = rank_series(df['score', subject])
        df_cmp['rank_school_cmp', subject] = rank_series(df_cmp['score', subject])
    df_cmp.rename(columns={('score', subject): ('score_cmp', subject) for subject in sc_common}, inplace=True)
    df_cmp = df_cmp[
        [('score_cmp', subject) for subject in sc_common] + [('rank_school_cmp', subject) for subject in sc_common]]
    df = pd.merge(df, df_cmp, left_index=True, right_index=True)
    for subject in sc_common:
        df['diff', subject] = df['rank_school_cmp', subject] - df['rank_school', subject]
    return df


class Analysis:
    def __init__(self, form, sort_by, ascending):
        self.semester, self.exam = form.cleaned_data['semester'], form.cleaned_data['exam']
        self.subjects = form.cleaned_data['subjects']
        self.school_props = form.cleaned_data['school_props']
        self.grade = form.cleaned_data['grade']
        self.classes = form.cleaned_data['classes']
        self.analysis_type = form.cleaned_data['analysis_type']
        self.sort_by = sort_by
        self.ascending = ascending

        conds = functools.reduce(operator.or_, (Q(school=sp[0], prop=sp[1]) for sp in self.school_props))
        self.rank_students = Student.objects.filter(conds)
        if len(self.rank_students) == 0:
            raise ImportError("没有数据")

        self.display_students = Student.objects.filter(conds).filter(class_idx__in=self.classes, grade_idx=self.grade)
        self.record_df, self.subject_list = load_records(self.exam, self.semester, self.subjects, self.rank_students)

    def get_df_subjects(self):
        pass

    def get_context(self):
        pass


class RankAnalysis(Analysis):
    template_name = "record/components/rank_list.html"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def get_df(self):
        df = self.record_df
        for subject in self.subject_list:
            df['rank_school', subject] = rank_series(df['score', subject])
        rank_class = df.groupby(['class_idx', 'school']).apply(rank_df, subject_columns=self.subject_list)
        df = pd.merge(df, rank_class, left_index=True, right_index=True)

        df = df.ix[[s.id for s in self.display_students]]
        if self.sort_by == 'student_id':
            df['student_id_numeric'] = df['student_id'].map(lambda x: int(x[1:]))
            df.sort_values('student_id_numeric', ascending=self.ascending, inplace=True)
        else:
            df.sort_values(('score', self.sort_by), ascending=self.ascending, inplace=True)
        return df

    def get_context(self):
        df = self.get_df()
        return {
            'data': df.to_dict('records'),
            'subjects': self.subject_list
        }


class RankCmpAnalysis(Analysis):
    template_name = "record/components/rank_diff_list.html"

    def __init__(self, form, *args, **kwargs):
        super().__init__(form, *args, **kwargs)
        self.semester_cmp, self.exam_cmp = form.cleaned_data['semester_cmp'], form.cleaned_data['exam_cmp']
        self.subject_common = None

    def get_df(self):
        df, subject_list = self.record_df, self.subject_list
        df_cmp, subject_list_cmp = load_records(self.exam_cmp, self.semester_cmp, self.subjects, self.rank_students)
        sc_common = [s for s in subject_list if s in subject_list_cmp]
        self.subject_common = sc_common

        for subject in sc_common:
            df['rank_school', subject] = rank_series(df['score', subject])
            df_cmp['rank_school_cmp', subject] = rank_series(df_cmp['score', subject])
        df_cmp.rename(columns={('score', subject): ('score_cmp', subject) for subject in sc_common}, inplace=True)
        df_cmp = df_cmp[
            [('score_cmp', subject) for subject in sc_common] + [('rank_school_cmp', subject) for subject in sc_common]]
        df = pd.merge(df, df_cmp, left_index=True, right_index=True)
        for subject in sc_common:
            df['rank_diff', subject] = df['rank_school_cmp', subject] - df['rank_school', subject]
        df = df.ix[[s.id for s in self.display_students]]
        if self.sort_by == 'student_id':
            df['student_id_numeric'] = df['student_id'].map(lambda x: int(x[1:]))
            df.sort_values('student_id_numeric', ascending=self.ascending, inplace=True)
        else:
            df.sort_values(('score', self.sort_by), ascending=self.ascending, inplace=True)

        return df

    def get_context(self):
        df = self.get_df()
        return {
            'data': df.to_dict('records'),
            'subjects': self.subject_common,
            'exam': self.exam,
            'exam_cmp': self.exam_cmp,
        }
