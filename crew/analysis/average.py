import functools
import itertools
import pandas as pd
import numpy as np
from .util import load_records, ClassBasedAnalysis, AnalysisError
from .rank import rank_series


class AverageAnalysis(ClassBasedAnalysis):
    def __init__(self, form):
        super().__init__(form)
        self.show_subjects = [s for s in form.cleaned_data['show_subjects'] if s in self.subjects]

    @staticmethod
    def group_subject_stat(df, subject, mean, total):
        excellent_score = subject.total_score * subject.excellent_ratio
        good_score = subject.total_score * subject.good_ratio
        pass_score = subject.total_score * subject.pass_ratio
        score = df['score', subject.name]

        excellent_cnt = (score >= excellent_score).sum()
        good_cnt = (score >= good_score).sum()
        pass_cnt = (score >= pass_score).sum()
        sn = subject.name
        return pd.Series({
            ('excellent', sn): excellent_cnt / total,
            ('good', sn): (good_cnt - excellent_cnt) / total,
            ('excellent_and_good', sn): good_cnt / total,
            ('pass', sn): (pass_cnt - good_cnt) / total,
            ('mean', sn): score.mean(),
            ('mean_diff', sn): score.mean() - mean
        })

    @staticmethod
    def group_total_stat(df, mean):
        score = df['score', '总分']
        return pd.Series({
            ('mean', '总分'): score.mean(),
            ('mean_diff', '总分'): score.mean() - mean
        })

    def get_df(self):
        df = self.record_df
        # 总分
        s = df['score', '总分']
        mean = s.mean()
        res_df = df.groupby(['school', 'class_idx']).apply(AverageAnalysis.group_total_stat, mean=mean)
        res_df['mean_rank', '总分'] = rank_series(res_df['mean', '总分'])
        # 单科
        for subject in self.show_subjects:
            s = df['score', subject.name]
            df['rank', subject.name] = rank_series(s)
            mean = s.mean()
            total = len(s) - pd.isnull(s).sum()
            ratio_df = df.groupby(['school', 'class_idx']).apply(AverageAnalysis.group_subject_stat, subject=subject,
                                                                 mean=mean,
                                                                 total=total)
            ratio_df['mean_rank', subject.name] = rank_series(ratio_df['mean', subject.name])
            if res_df is None:
                res_df = ratio_df
            else:
                res_df = pd.merge(res_df, ratio_df, left_index=True, right_index=True)
        res_df['school'] = res_df.index.get_level_values(0)
        res_df['class_idx'] = res_df.index.get_level_values(1)

        return res_df


class AverageCmpAnalysis(ClassBasedAnalysis):
    def __init__(self, form):
        super().__init__(form)
        self.semester_cmp = form.cleaned_data['semester_cmp']
        self.exam_cmp = form.cleaned_data['exam_cmp']
        self.record_df_cmp, self.subject_list_cmp = load_records(self.exam_cmp, self.semester_cmp, self.subjects,
                                                                 self.students)

        self.show_subjects = [s for s in form.cleaned_data['show_subjects'] if
                              s in self.subjects and s in self.subject_list_cmp]

    def get_df(self):
        df = self.record_df
        df_cmp = self.record_df_cmp

        for subject in self.show_subjects:
            pass
