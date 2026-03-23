from django import forms
from .models import Observation, ESL_STRATEGY_CHOICES, CURRICULUM_CHOICES, PHYSICAL_GROUP_CHOICES, ACTIVITY_STRUCTURE_CHOICES, MODE_CHOICES, LANGUAGE_CONTENT_CHOICES, LANGUAGE_CHOICES


class ObservationForm(forms.ModelForm):
    class Meta:
        model = Observation
        fields = [
            'esl_strategy', 'curriculum', 'physical_group',
            'activity_structure', 'mode', 'language_content',
            'language_instruction_teacher', 'language_instruction_student',
        ]
        widgets = {
            'esl_strategy': forms.Select(attrs={'class': 'obs-select'}),
            'curriculum': forms.Select(attrs={'class': 'obs-select'}),
            'physical_group': forms.Select(attrs={'class': 'obs-select'}),
            'activity_structure': forms.Select(attrs={'class': 'obs-select'}),
            'mode': forms.Select(attrs={'class': 'obs-select'}),
            'language_content': forms.Select(attrs={'class': 'obs-select'}),
            'language_instruction_teacher': forms.Select(attrs={'class': 'obs-select'}),
            'language_instruction_student': forms.Select(attrs={'class': 'obs-select'}),
        }
        labels = {
            'esl_strategy': 'ESL Strategy:',
            'curriculum': 'Curriculum:',
            'physical_group': 'Physical Group:',
            'activity_structure': 'Activity Structure:',
            'mode': 'Mode:',
            'language_content': 'Language Content:',
            'language_instruction_teacher': 'Language of Instruction (Teacher):',
            'language_instruction_student': 'Language of Instruction (Student):',
        }
