from django import forms
from .models import Observation


class ObservationForm(forms.ModelForm):
    class Meta:
        model = Observation
        fields = [
            'esl_strategy', 'curriculum', 'physical_group',
            'activity_structure', 'mode', 'language_content',
            'language_instruction_teacher', 'language_instruction_student',
        ]
        widgets = {
            'esl_strategy': forms.Select(attrs={
                'class': 'form-select tamu-select',
                'aria-required': 'true',
            }),
            'curriculum': forms.Select(attrs={
                'class': 'form-select tamu-select',
                'aria-required': 'true',
            }),
            'physical_group': forms.Select(attrs={
                'class': 'form-select tamu-select',
                'aria-required': 'true',
            }),
            'activity_structure': forms.Select(attrs={
                'class': 'form-select tamu-select',
                'aria-required': 'true',
            }),
            'mode': forms.Select(attrs={
                'class': 'form-select tamu-select',
                'aria-required': 'true',
            }),
            'language_content': forms.Select(attrs={
                'class': 'form-select tamu-select',
                'aria-required': 'true',
            }),
            'language_instruction_teacher': forms.Select(attrs={
                'class': 'form-select tamu-select',
                'aria-required': 'true',
            }),
            'language_instruction_student': forms.Select(attrs={
                'class': 'form-select tamu-select',
                'aria-required': 'true',
            }),
        }
        labels = {
            'esl_strategy': 'ESL Strategy',
            'curriculum': 'Curriculum',
            'physical_group': 'Physical Group',
            'activity_structure': 'Activity Structure',
            'mode': 'Mode',
            'language_content': 'Language Content',
            'language_instruction_teacher': 'Language of Instruction (Teacher)',
            'language_instruction_student': 'Language of Instruction (Student)',
        }
