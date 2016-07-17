from crew.models import *
import pandas as pd
import numpy as np
from pandas import DataFrame, Series
from crew.models import *
import functools
import operator
from django.db.models import Q
from crew.util import debug_print
from .util import load_records, ClassBasedAnalysis


def rank_series(series):
    return series.rank(method='min', numeric_only=False, na_option='bottom', ascending=False).astype(np.int)


def rank_df(df, subject_columns):
    return pd.DataFrame({
                            ('rank_class', subject): rank_series(df[('score', subject)]) for subject in subject_columns
                            }, dtype=np.int)


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
        self.rank_students = Student.objects.filter(conds).filter(grade_idx=self.grade)
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


def num_ge(df, segments):
    res = {
        seg: (df > seg).sum() for seg in segments
        }
    res['total'] = len(df) - pd.isnull(df).sum()
    return res


class SegmentAnalysis(ClassBasedAnalysis):
    def __init__(self, form):
        super(SegmentAnalysis, self).__init__(form)
        self.show_total = form.cleaned_data['show_total']
        self.show_subjects = [s for s in form.cleaned_data['show_subjects'] if s in self.subjects]

        sys_setting = SystemSettings.get_instance()
        if self.category == 'L':
            self.segments = sys_setting.science_segments
        elif self.category == 'W':
            self.segments = sys_setting.art_segments
        else:
            self.segments = sys_setting.universal_segments

    def get_df_list(self):
        df = self.record_df
        df_list = []
        if self.show_total:
            s = df['score', '总分']
            cnt_df = s.groupby(df['class_idx']).apply(num_ge,
                                                      segments=[int(x) for x in self.segments.split(',')]).unstack(-1)
            cnt_df['class_idx'] = cnt_df.index
            agg = cnt_df.sum(axis=0)
            df_list.append(('总分', cnt_df, agg, self.segments))
        for subject in self.show_subjects:
            s = df['score', subject.name]
            cnt_df = s.groupby(df['class_idx']).apply(num_ge,
                                                      segments=[int(x) for x in subject.segments.split(',')]).unstack(
                -1)
            cnt_df['class_idx'] = cnt_df.index
            agg = cnt_df.sum(axis=0)
            df_list.append((subject.name, cnt_df, agg, subject.segments))

        return df_list
