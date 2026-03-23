from django.contrib import admin
from .models import School, Teacher, Observation


@admin.register(School)
class SchoolAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)


@admin.register(Teacher)
class TeacherAdmin(admin.ModelAdmin):
    list_display = ('name', 'teacher_id', 'school')
    list_filter = ('school',)
    search_fields = ('name', 'teacher_id')


@admin.register(Observation)
class ObservationAdmin(admin.ModelAdmin):
    list_display = (
        'teacher', 'school', 'observation_number', 'observer',
        'esl_strategy', 'curriculum', 'created_at'
    )
    list_filter = ('school', 'esl_strategy', 'curriculum')
    search_fields = ('teacher__name', 'school__name', 'observer__username')
    readonly_fields = ('created_at',)
