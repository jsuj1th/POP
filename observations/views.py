import io
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse, HttpResponse
from django.views.decorators.http import require_GET
import openpyxl
from openpyxl.styles import Font, PatternFill, Alignment

from .models import School, Teacher, Observation
from .forms import ObservationForm


def login_view(request):
    if request.user.is_authenticated:
        return redirect('select_data')

    error = None
    if request.method == 'POST':
        username = request.POST.get('username', '').strip()
        password = request.POST.get('password', '')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('select_data')
        else:
            error = 'Invalid username or password.'

    return render(request, 'observations/login.html', {'error': error})


def logout_view(request):
    logout(request)
    return redirect('login')


@login_required
def select_data(request):
    if request.method == 'POST':
        school_id = request.POST.get('school_id', '').strip()
        teacher_id = request.POST.get('teacher_id', '').strip()

        if not school_id:
            messages.error(request, 'Please select a school.')
        elif not teacher_id:
            messages.error(request, 'Please select a teacher.')
        else:
            # Validate they exist
            try:
                school = School.objects.get(pk=school_id)
                teacher = Teacher.objects.get(pk=teacher_id, school=school)
                return redirect(f'/observe/?school_id={school_id}&teacher_id={teacher_id}')
            except (School.DoesNotExist, Teacher.DoesNotExist):
                messages.error(request, 'Invalid school or teacher selection.')

    schools = School.objects.all().order_by('name')
    return render(request, 'observations/select_data.html', {'schools': schools})


@require_GET
def get_teachers(request):
    school_id = request.GET.get('school_id', '')
    if not school_id:
        return JsonResponse({'teachers': []})
    try:
        school = School.objects.get(pk=school_id)
        teachers = list(
            school.teachers.order_by('name').values('id', 'name', 'teacher_id')
        )
        return JsonResponse({'teachers': teachers})
    except School.DoesNotExist:
        return JsonResponse({'teachers': []})


@login_required
def observation_form(request):
    school_id = request.GET.get('school_id') or request.POST.get('school_id')
    teacher_id = request.GET.get('teacher_id') or request.POST.get('teacher_id')
    from_reports = request.GET.get('from') == 'reports' or request.POST.get('from_reports') == '1'

    if not school_id or not teacher_id:
        messages.error(request, 'Please select a school and teacher first.')
        return redirect('select_data')

    school = get_object_or_404(School, pk=school_id)
    teacher = get_object_or_404(Teacher, pk=teacher_id, school=school)

    observation_number = Observation.objects.filter(teacher=teacher).count() + 1

    if request.method == 'POST':
        action = request.POST.get('action', 'enter')

        # "Complete" ends the session without requiring the current form to be valid.
        # Just redirect to the completion page; whatever was previously saved stands.
        if action == 'complete':
            return redirect(f'/observe/complete/?teacher_id={teacher_id}')

        form = ObservationForm(request.POST)
        if form.is_valid():
            obs = form.save(commit=False)
            obs.observer = request.user
            obs.school = school
            obs.teacher = teacher
            obs.observation_number = observation_number
            obs.save()
            if from_reports:
                messages.success(request, f'Observation #{observation_number} for {teacher.name} added.')
                return redirect('reports')
            return redirect(f'/observe/?school_id={school_id}&teacher_id={teacher_id}')
    else:
        form = ObservationForm()

    context = {
        'form': form,
        'school': school,
        'teacher': teacher,
        'observation_number': observation_number,
        'school_id': school_id,
        'teacher_id': teacher_id,
        'from_reports': from_reports,
    }
    return render(request, 'observations/observation_form.html', context)


@login_required
def observation_complete(request):
    teacher_id = request.GET.get('teacher_id')
    teacher = get_object_or_404(Teacher, pk=teacher_id)
    observations = Observation.objects.filter(
        observer=request.user, teacher=teacher
    ).order_by('observation_number')
    return render(request, 'observations/observation_complete.html', {
        'teacher': teacher,
        'observations': observations,
        'count': observations.count(),
    })


@login_required
def download_teacher_excel(request):
    teacher_id = request.GET.get('teacher_id')
    teacher = get_object_or_404(Teacher, pk=teacher_id)
    observations = Observation.objects.filter(
        observer=request.user, teacher=teacher
    ).select_related('school', 'teacher').order_by('observation_number')

    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = 'Observations'

    headers = [
        'School', 'Teacher', 'Teacher ID', 'Obs #',
        'ESL Strategy', 'Curriculum', 'Physical Group',
        'Activity Structure', 'Mode', 'Language Content',
        'Lang Instr (T)', 'Lang Instr (S)', 'Date'
    ]

    header_fill = PatternFill(start_color='7090B0', end_color='7090B0', fill_type='solid')
    header_font = Font(color='FFFFFF', bold=True)

    for col_num, header in enumerate(headers, 1):
        cell = ws.cell(row=1, column=col_num, value=header)
        cell.fill = header_fill
        cell.font = header_font
        cell.alignment = Alignment(horizontal='center')

    for row_num, obs in enumerate(observations, 2):
        ws.cell(row=row_num, column=1, value=obs.school.name)
        ws.cell(row=row_num, column=2, value=obs.teacher.name)
        ws.cell(row=row_num, column=3, value=obs.teacher.teacher_id)
        ws.cell(row=row_num, column=4, value=obs.observation_number)
        ws.cell(row=row_num, column=5, value=obs.esl_strategy)
        ws.cell(row=row_num, column=6, value=obs.curriculum)
        ws.cell(row=row_num, column=7, value=obs.physical_group)
        ws.cell(row=row_num, column=8, value=obs.activity_structure)
        ws.cell(row=row_num, column=9, value=obs.mode)
        ws.cell(row=row_num, column=10, value=obs.language_content)
        ws.cell(row=row_num, column=11, value=obs.language_instruction_teacher)
        ws.cell(row=row_num, column=12, value=obs.language_instruction_student)
        ws.cell(row=row_num, column=13, value=obs.created_at.strftime('%Y-%m-%d %H:%M'))

        if row_num % 2 == 0:
            even_fill = PatternFill(start_color='F5F5F5', end_color='F5F5F5', fill_type='solid')
            for col in range(1, 14):
                ws.cell(row=row_num, column=col).fill = even_fill

    col_widths = [30, 25, 15, 8, 15, 18, 16, 20, 12, 18, 15, 15, 18]
    for i, width in enumerate(col_widths, 1):
        ws.column_dimensions[openpyxl.utils.get_column_letter(i)].width = width

    buffer = io.BytesIO()
    wb.save(buffer)
    buffer.seek(0)

    safe_name = teacher.name.replace(' ', '_')
    response = HttpResponse(
        buffer.getvalue(),
        content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )
    response['Content-Disposition'] = f'attachment; filename="observations_{safe_name}.xlsx"'
    return response


@login_required
def edit_observation(request, obs_id):
    obs = get_object_or_404(Observation, pk=obs_id, observer=request.user)
    if request.method == 'POST':
        form = ObservationForm(request.POST, instance=obs)
        if form.is_valid():
            form.save()
            messages.success(request, f'Observation #{obs.observation_number} for {obs.teacher.name} updated.')
            return redirect('reports')
    else:
        form = ObservationForm(instance=obs)
    return render(request, 'observations/edit_observation.html', {'form': form, 'obs': obs})


@login_required
def reports(request):
    observations = Observation.objects.filter(observer=request.user).select_related(
        'school', 'teacher'
    ).order_by('teacher__name', 'observation_number')

    # Group by teacher
    groups = {}
    for obs in observations:
        tid = obs.teacher.id
        if tid not in groups:
            groups[tid] = {
                'teacher': obs.teacher,
                'school': obs.school,
                'observations': [],
            }
        groups[tid]['observations'].append(obs)

    return render(request, 'observations/reports.html', {'groups': groups.values()})


@login_required
def download_excel(request):
    observations = Observation.objects.filter(observer=request.user).select_related(
        'school', 'teacher'
    ).order_by('-created_at')

    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = 'Observations'

    headers = [
        'School', 'Teacher', 'Teacher ID', 'Obs #',
        'ESL Strategy', 'Curriculum', 'Physical Group',
        'Activity Structure', 'Mode', 'Language Content',
        'Lang Instr (T)', 'Lang Instr (S)', 'Date'
    ]

    header_fill = PatternFill(start_color='7090B0', end_color='7090B0', fill_type='solid')
    header_font = Font(color='FFFFFF', bold=True)

    for col_num, header in enumerate(headers, 1):
        cell = ws.cell(row=1, column=col_num, value=header)
        cell.fill = header_fill
        cell.font = header_font
        cell.alignment = Alignment(horizontal='center')

    for row_num, obs in enumerate(observations, 2):
        ws.cell(row=row_num, column=1, value=obs.school.name)
        ws.cell(row=row_num, column=2, value=obs.teacher.name)
        ws.cell(row=row_num, column=3, value=obs.teacher.teacher_id)
        ws.cell(row=row_num, column=4, value=obs.observation_number)
        ws.cell(row=row_num, column=5, value=obs.esl_strategy)
        ws.cell(row=row_num, column=6, value=obs.curriculum)
        ws.cell(row=row_num, column=7, value=obs.physical_group)
        ws.cell(row=row_num, column=8, value=obs.activity_structure)
        ws.cell(row=row_num, column=9, value=obs.mode)
        ws.cell(row=row_num, column=10, value=obs.language_content)
        ws.cell(row=row_num, column=11, value=obs.language_instruction_teacher)
        ws.cell(row=row_num, column=12, value=obs.language_instruction_student)
        ws.cell(row=row_num, column=13, value=obs.created_at.strftime('%Y-%m-%d %H:%M'))

        if row_num % 2 == 0:
            even_fill = PatternFill(start_color='F5F5F5', end_color='F5F5F5', fill_type='solid')
            for col in range(1, 14):
                ws.cell(row=row_num, column=col).fill = even_fill

    # Auto-adjust column widths
    col_widths = [30, 25, 15, 8, 15, 18, 16, 20, 12, 18, 15, 15, 18]
    for i, width in enumerate(col_widths, 1):
        ws.column_dimensions[openpyxl.utils.get_column_letter(i)].width = width

    buffer = io.BytesIO()
    wb.save(buffer)
    buffer.seek(0)

    response = HttpResponse(
        buffer.getvalue(),
        content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )
    response['Content-Disposition'] = 'attachment; filename="observations.xlsx"'
    return response
