from django.db import models
from django.contrib.auth.models import User


class School(models.Model):
    name = models.CharField(max_length=200)
    district = models.CharField(max_length=200, blank=True)
    condition = models.CharField(max_length=20, blank=True)

    def __str__(self):
        return self.name


class Teacher(models.Model):
    school = models.ForeignKey(School, on_delete=models.CASCADE, related_name='teachers')
    name = models.CharField(max_length=200)
    teacher_id = models.CharField(max_length=50, unique=True, blank=True)

    def __str__(self):
        return self.name


class ObservationSession(models.Model):
    observer = models.ForeignKey(User, on_delete=models.CASCADE)
    school = models.ForeignKey(School, on_delete=models.CASCADE)
    teacher = models.ForeignKey(Teacher, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.teacher.name} - Session {self.id}"


ESL_STRATEGY_CHOICES = [
    (1, 'QS'), (2, 'ALS'), (3, 'VS'), (4, 'MR'), (5, 'AO'),
    (6, 'CG'), (7, 'CC'), (8, 'LC'), (9, 'IT'), (10, 'NA'),
]

CURRICULUM_CHOICES = [
    (1, 'read/lit'), (2, 'math'), (3, 'spell'), (4, 'hand'),
    (5, 'science'), (6, 'soc sci'), (7, 'health'), (8, 'PE'),
    (9, 'music'), (10, 'art'), (11, 'lang'), (12, 'compos'),
    (13, 'non-ac'), (14, 'ESL'),
]

PHYSICAL_GROUP_CHOICES = [
    (1, 'TC'), (2, 'LG'), (3, 'SG'), (4, 'Pairs'), (5, 'Single'),
]

ACTIVITY_STRUCTURE_CHOICES = [
    (1, 'lec/lis'), (2, 'lec/per'), (3, 'dir/lis'), (4, 'dir/per'),
    (5, 'dem/lis'), (6, 'led/per'), (7, 'ask/per'), (8, 'ask/ans'),
    (9, 'ans/ask'), (10, 'ev/per'), (11, 'obs/per'), (12, 'ev/dis'),
    (13, 'ev/cop'), (14, 'obs/dis'), (15, 'obs/cop'), (16, 'NA/free'),
    (17, 'NA/feed'), (18, 'NA/tran'), (19, 'NA/int'), (20, 'NA/out'),
    (21, 'interact'),
]

MODE_CHOICES = [
    (1, 'writing'), (2, 'reading'), (3, 'aural'), (4, 'verbal'),
    (5, 'wr-re'), (6, 'wr-au'), (7, 'wr-ver'), (8, 're-wr'),
    (9, 're-au'), (10, 're-ver'), (11, 'au-wr'), (12, 'au-re'),
    (13, 'ver-wr'), (14, 'ver-re'), (15, 'ver-au'),
    (16, 'au-re-ver'), (17, 'NA'), (18, 'au-ver'),
]

LANGUAGE_CONTENT_CHOICES = [
    (1, 'social'), (2, 'academic'), (3, 'light cog'),
    (4, 'dns cog'), (5, 'NA'),
]

LANGUAGE_CHOICES = [
    (1, 'L1'), (2, 'L2'), (3, 'L1-2'), (4, 'L2-1'), (5, 'NA'),
]


class Observation(models.Model):
    
    session = models.ForeignKey(ObservationSession, on_delete=models.CASCADE)

    observer = models.ForeignKey(User, on_delete=models.CASCADE)
    school = models.ForeignKey(School, on_delete=models.CASCADE)
    teacher = models.ForeignKey(Teacher, on_delete=models.CASCADE)
    observation_number = models.PositiveIntegerField(default=1)

    esl_strategy = models.IntegerField(choices=ESL_STRATEGY_CHOICES)
    curriculum = models.IntegerField(choices=CURRICULUM_CHOICES)
    physical_group = models.IntegerField(choices=PHYSICAL_GROUP_CHOICES)
    activity_structure = models.IntegerField(choices=ACTIVITY_STRUCTURE_CHOICES)
    mode = models.IntegerField(choices=MODE_CHOICES)
    language_content = models.IntegerField(choices=LANGUAGE_CONTENT_CHOICES)
    language_instruction_teacher = models.IntegerField(choices=LANGUAGE_CHOICES)
    language_instruction_student = models.IntegerField(choices=LANGUAGE_CHOICES)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.teacher.name} - Obs {self.observation_number}"
