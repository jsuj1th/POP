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
    ('QS', 'QS'), ('ALS', 'ALS'), ('VS', 'VS'), ('MR', 'MR'), ('AO', 'AO'),
    ('CG', 'CG'), ('CC', 'CC'), ('LC', 'LC'), ('IT', 'IT'), ('NA', 'NA'),
]
CURRICULUM_CHOICES = [
    ('read/lit', 'read/lit'), ('math', 'math'), ('spell', 'spell'),
    ('hand', 'hand'), ('science', 'science'), ('soc sci', 'soc sci'),
    ('health', 'health'), ('PE', 'PE'), ('music', 'music'), ('art', 'art'),
    ('lang', 'lang'), ('compos', 'compos'), ('non-ac', 'non-ac'), ('ESL', 'ESL'),
]
PHYSICAL_GROUP_CHOICES = [
    ('TC', 'TC'), ('LG', 'LG'), ('SG', 'SG'), ('Pairs', 'Pairs'), ('Single', 'Single'),
]
ACTIVITY_STRUCTURE_CHOICES = [
    ('lec/lis', 'lec/lis'), ('lec/per', 'lec/per'), ('dir/lis', 'dir/lis'),
    ('dir/per', 'dir/per'), ('dem/lis', 'dem/lis'), ('led/per', 'led/per'),
    ('ask/per', 'ask/per'), ('ask/ans', 'ask/ans'), ('ans/ask', 'ans/ask'),
    ('ev/per', 'ev/per'), ('obs/per', 'obs/per'), ('ev/dis', 'ev/dis'),
    ('ev/cop', 'ev/cop'), ('obs/dis', 'obs/dis'), ('obs/cop', 'obs/cop'),
    ('NA/free', 'NA/free'), ('NA/feed', 'NA/feed'), ('NA/tran', 'NA/tran'),
    ('NA/int', 'NA/int'), ('NA/out', 'NA/out'), ('interac', 'interac'),
]
MODE_CHOICES = [
    ('writing', 'writing'), ('reading', 'reading'), ('aural', 'aural'),
    ('verbal', 'verbal'), ('wr-re', 'wr-re'), ('wr-au', 'wr-au'),
    ('wr-ver', 'wr-ver'), ('re-wr', 're-wr'), ('re-au', 're-au'),
    ('re-ver', 're-ver'), ('au-wr', 'au-wr'), ('au-re', 'au-re'),
    ('ver-wr', 'ver-wr'), ('ver-re', 'ver-re'), ('ver-au', 'ver-au'),
    ('au-re-ver', 'au-re-ver'), ('NA', 'NA'), ('au-ver', 'au-ver'),
]
LANGUAGE_CONTENT_CHOICES = [
    ('social', 'social'), ('academic', 'academic'), ('light cog', 'light cog'),
    ('dns cog', 'dns cog'), ('NA', 'NA'),
]
LANGUAGE_CHOICES = [
    ('L1', 'L1'), ('L2', 'L2'), ('L1-2', 'L1-2'), ('L2-1', 'L2-1'), ('NA', 'NA'),
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
