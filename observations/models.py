from django.db import models
from django.contrib.auth.models import User


class School(models.Model):
    name = models.CharField(max_length=200)
    district = models.CharField(max_length=200, blank=True)
    condition = models.CharField(max_length=20, blank=True)  # Online / F2F

    def __str__(self):
        return self.name


class Teacher(models.Model):
    school = models.ForeignKey(School, on_delete=models.CASCADE, related_name='teachers')
    name = models.CharField(max_length=200)
    teacher_id = models.CharField(max_length=50, unique=True, blank=True)

    def __str__(self):
        return self.name


ESL_STRATEGY_CHOICES = [
    ('QS', 'QS'), ('TPR', 'TPR'), ('VS', 'VS'), ('MT', 'MT'), ('RP', 'RP'),
    ('DR', 'DR'), ('WA', 'WA'), ('other', 'other'),
]
CURRICULUM_CHOICES = [
    ('read/lit', 'read/lit'), ('math', 'math'), ('science', 'science'),
    ('social studies', 'social studies'), ('other', 'other'),
]
PHYSICAL_GROUP_CHOICES = [
    ('TC', 'TC'), ('SG', 'SG'), ('I', 'I'), ('P', 'P'),
]
ACTIVITY_STRUCTURE_CHOICES = [
    ('lec/lis', 'lec/lis'), ('disc', 'disc'), ('coop', 'coop'),
    ('ind', 'ind'), ('other', 'other'),
]
MODE_CHOICES = [
    ('writing', 'writing'), ('reading', 'reading'), ('listening', 'listening'),
    ('speaking', 'speaking'), ('multi', 'multi'),
]
LANGUAGE_CONTENT_CHOICES = [
    ('social', 'social'), ('academic', 'academic'), ('both', 'both'),
]
LANGUAGE_CHOICES = [
    ('L1', 'L1'), ('L2', 'L2'), ('both', 'both'), ('neither', 'neither'),
]


class Observation(models.Model):
    observer = models.ForeignKey(User, on_delete=models.CASCADE)
    school = models.ForeignKey(School, on_delete=models.CASCADE)
    teacher = models.ForeignKey(Teacher, on_delete=models.CASCADE)
    observation_number = models.PositiveIntegerField(default=1)
    esl_strategy = models.CharField(max_length=20, choices=ESL_STRATEGY_CHOICES)
    curriculum = models.CharField(max_length=50, choices=CURRICULUM_CHOICES)
    physical_group = models.CharField(max_length=20, choices=PHYSICAL_GROUP_CHOICES)
    activity_structure = models.CharField(max_length=20, choices=ACTIVITY_STRUCTURE_CHOICES)
    mode = models.CharField(max_length=20, choices=MODE_CHOICES)
    language_content = models.CharField(max_length=20, choices=LANGUAGE_CONTENT_CHOICES)
    language_instruction_teacher = models.CharField(max_length=20, choices=LANGUAGE_CHOICES)
    language_instruction_student = models.CharField(max_length=20, choices=LANGUAGE_CHOICES)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.teacher.name} - Obs {self.observation_number}"
