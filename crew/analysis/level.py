import functools
import itertools
import pandas as pd
import numpy as np
from django.db.models import Q
from .util import load_records, load_teachers, ClassBasedAnalysis, AnalysisError, GROUP_KEYS
from .rank import rank_series
from crew.models import Student
import operator


class LevelAnalysis(ClassBasedAnalysis):
    def __init__(self, form, rank_form, score_formset):
        super().__init__(form)
        self.show_subjects = [s for s in form.cleaned_data['show_subjects'] if s in self.subjects]
        self.settings = {
            'level_a_rank': rank_form.cleaned_data['level_a_rank'],
            'level_b_rank': rank_form.cleaned_data['level_b_rank'],
        }
        self.settings['level_a_score'] = {
            score_form.cleaned_data['subject_name']: score_form.cleaned_data['level_a_score'] for score_form in
            score_formset
            }
        self.settings['level_b_score'] = {
            score_form.cleaned_data['subject_name']: score_form.cleaned_data['level_b_score'] for score_form in
            score_formset
            }

        self.settings['use_rank'] = rank_form.cleaned_data['use_rank']

    @staticmethod
    def group_stat(df, subject, mean):
        score_series = df['score', subject]
        group_mean = score_series.mean()
        level_a_count = df['is_level_a', subject].sum()
        level_b_count = df['is_level_b', subject].sum()
        valid_count = score_series.count()
        return pd.Series({
            ('valid_count', subject): valid_count,
            ('total_count', subject): len(df),
            ('mean', subject): group_mean,
            ('mean_diff', subject): group_mean - mean,
            ('max_score', subject): score_series.max(),
            ('level_a_count', subject): level_a_count,
            ('level_a_ratio', subject): level_a_count / valid_count,
            ('level_b_count', subject): level_b_count,
            ('level_b_ratio', subject): level_b_count / valid_count,
        })

    def get_df_list(self):
        subject_df_list = []
        df = self.record_df
        teacher_df = load_teachers(self.grade)
        for subject in ['总分'] + [s.name for s in self.show_subjects]:
            df['rank', subject] = rank_series(df['score', subject])
            df['is_level_a', subject] = df['rank', subject] <= self.settings['level_a_rank'] if self.settings[
                'use_rank'] else df['score', subject] >= self.settings['level_a_score'][subject]
            df['is_level_b', subject] = df['rank', subject] <= self.settings['level_b_rank'] if self.settings[
                'use_rank'] else df['score', subject] >= self.settings['level_b_score'][subject]
            mean = df['score', subject].mean()
            subject_df = df.groupby(GROUP_KEYS).apply(LevelAnalysis.group_stat, subject=subject, mean=mean)
            subject_df['level_a_rank', subject] = rank_series(subject_df['level_a_ratio', subject])
            subject_df['level_b_rank', subject] = rank_series(subject_df['level_b_ratio', subject])
            subject_df.columns = list(
                zip(subject_df.columns.get_level_values(0), subject_df.columns.get_level_values(1)))

            if subject == "总分":
                subject = "班主任"
            if subject in teacher_df.columns:
                subject_df = subject_df.join(teacher_df[subject])
            else:
                subject_df[subject] = np.nan
            subject_df.reset_index(inplace=True)
            subject_df_list.append(subject_df)

        return subject_df_list

    def get_agg_list(self):
        agg_list = []
        for subject in ['总分'] + [s.name for s in self.show_subjects]:
            agg_list.append(LevelAnalysis.group_stat(self.record_df, subject, 0))
        return agg_list


class LevelDistAnalysis(LevelAnalysis):
    def __init__(self, form, rank_form, score_formset):
        self.class_idx = form.cleaned_data['class_idx']
        super().__init__(form, rank_form, score_formset)


    def get_student_query_set(self):
        conds = functools.reduce(operator.or_, (Q(school=sp[0], prop=sp[1]) for sp in self.school_props))
        return Student.objects.filter(conds).filter(grade_idx=self.grade, class_idx=self.class_idx, category=self.category)

    def get_df(self):
        df = self.record_df
        for subject in ['总分'] + [s.name for s in self.show_subjects]:
            df['rank', subject] = rank_series(df['score', subject])
            df['is_level_a', subject] = df['rank', subject] <= self.settings['level_a_rank'] if self.settings[
                'use_rank'] else df['score', subject] >= self.settings['level_a_score'][subject]
            df['is_level_b', subject] = df['rank', subject] <= self.settings['level_b_rank'] if self.settings[
                'use_rank'] else df['score', subject] >= self.settings['level_b_score'][subject]
        return df
