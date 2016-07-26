from crew.models import *
from django.db.models import Q
import functools
import operator
import pandas as pd
import numpy as np

GROUP_KEYS = ['school', 'grade', 'class_idx']


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


def load_teachers(grade_idx):
    managers = ClassTeacher.objects.filter(grade_idx=grade_idx, ).select_related('teacher', 'subject')
    df = pd.DataFrame.from_dict([
                                    {'school': t.get_school_display(),
                                     'grade': t.get_grade_idx_display(),
                                     'class_idx': t.class_idx,
                                     'subject': "班主任" if t.subject is None else t.subject.name,
                                     'name': t.teacher.name} for t in managers
                                    ])
    df.set_index(['school', 'grade', 'class_idx', 'subject'], inplace=True)
    return df['name'].unstack(-1)


class AnalysisError(Exception):
    pass


class ClassBasedAnalysis:
    def __init__(self, form):
        self.semester = form.cleaned_data['semester']
        self.exam = form.cleaned_data['exam']
        self.category = form.cleaned_data['category']
        self.grade = form.cleaned_data['grade']
        self.school_props = form.cleaned_data['school_props']
        self.subjects = list(Subject.category_subjects(self.category))

        self.students = self.get_student_query_set()
        self.record_df, self.subject_list = load_records(self.exam, self.semester, self.subjects, self.students)

    def get_student_query_set(self):
        conds = functools.reduce(operator.or_, (Q(school=sp[0], prop=sp[1]) for sp in self.school_props))
        return Student.objects.filter(conds).filter(grade_idx=self.grade, category=self.category)
