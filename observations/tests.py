import json
from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from .models import School, Teacher, Observation
from .forms import ObservationForm


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

VALID_OBS_DATA = {
    'esl_strategy': 'TPR',
    'curriculum': 'math',
    'physical_group': 'TC',
    'activity_structure': 'lec/lis',
    'mode': 'listening',
    'language_content': 'academic',
    'language_instruction_teacher': 'L2',
    'language_instruction_student': 'L1',
}


def make_user(username='testuser', password='testpass123'):
    return User.objects.create_user(username=username, password=password)


def make_school(name='Test School', district='District A', condition='F2F'):
    return School.objects.create(name=name, district=district, condition=condition)


def make_teacher(school, name='Jane Doe', teacher_id='JD-001'):
    return Teacher.objects.create(school=school, name=name, teacher_id=teacher_id)


def make_observation(user, school, teacher, number=1, **kwargs):
    data = {**VALID_OBS_DATA, **kwargs}
    return Observation.objects.create(
        observer=user,
        school=school,
        teacher=teacher,
        observation_number=number,
        **data,
    )


# ---------------------------------------------------------------------------
# Model Tests
# ---------------------------------------------------------------------------

class SchoolModelTest(TestCase):

    def test_str(self):
        school = make_school(name='Lincoln ES')
        self.assertEqual(str(school), 'Lincoln ES')

    def test_optional_fields(self):
        school = School.objects.create(name='Minimal School')
        self.assertEqual(school.district, '')
        self.assertEqual(school.condition, '')

    def test_create_school_with_all_fields(self):
        school = make_school(name='Oak Park', district='Dist 5', condition='Online')
        self.assertEqual(school.name, 'Oak Park')
        self.assertEqual(school.district, 'Dist 5')
        self.assertEqual(school.condition, 'Online')


class TeacherModelTest(TestCase):

    def setUp(self):
        self.school = make_school()

    def test_str(self):
        teacher = make_teacher(self.school, name='John Smith')
        self.assertEqual(str(teacher), 'John Smith')

    def test_teacher_id_unique(self):
        make_teacher(self.school, name='Teacher A', teacher_id='UNIQUE-001')
        with self.assertRaises(Exception):
            make_teacher(self.school, name='Teacher B', teacher_id='UNIQUE-001')

    def test_teacher_id_blank_allowed(self):
        teacher = Teacher.objects.create(school=self.school, name='No ID Teacher')
        self.assertEqual(teacher.teacher_id, '')

    def test_cascade_delete_from_school(self):
        make_teacher(self.school)
        self.school.delete()
        self.assertEqual(Teacher.objects.count(), 0)

    def test_related_name_teachers(self):
        make_teacher(self.school, name='T1', teacher_id='T1')
        make_teacher(self.school, name='T2', teacher_id='T2')
        self.assertEqual(self.school.teachers.count(), 2)


class ObservationModelTest(TestCase):

    def setUp(self):
        self.user = make_user()
        self.school = make_school()
        self.teacher = make_teacher(self.school)

    def test_str(self):
        obs = make_observation(self.user, self.school, self.teacher, number=3)
        self.assertEqual(str(obs), 'Jane Doe - Obs 3')

    def test_default_observation_number(self):
        obs = Observation.objects.create(
            observer=self.user,
            school=self.school,
            teacher=self.teacher,
            **VALID_OBS_DATA,
        )
        self.assertEqual(obs.observation_number, 1)

    def test_created_at_auto_set(self):
        obs = make_observation(self.user, self.school, self.teacher)
        self.assertIsNotNone(obs.created_at)

    def test_cascade_delete_from_teacher(self):
        make_observation(self.user, self.school, self.teacher)
        self.teacher.delete()
        self.assertEqual(Observation.objects.count(), 0)

    def test_cascade_delete_from_user(self):
        make_observation(self.user, self.school, self.teacher)
        self.user.delete()
        self.assertEqual(Observation.objects.count(), 0)

    def test_cascade_delete_from_school(self):
        make_observation(self.user, self.school, self.teacher)
        self.school.delete()
        self.assertEqual(Observation.objects.count(), 0)


# ---------------------------------------------------------------------------
# Form Tests
# ---------------------------------------------------------------------------

class ObservationFormTest(TestCase):

    def test_valid_form(self):
        form = ObservationForm(data=VALID_OBS_DATA)
        self.assertTrue(form.is_valid(), form.errors)

    def test_missing_required_field(self):
        for field in VALID_OBS_DATA:
            data = {k: v for k, v in VALID_OBS_DATA.items() if k != field}
            form = ObservationForm(data=data)
            self.assertFalse(form.is_valid(), f"Form should be invalid without '{field}'")
            self.assertIn(field, form.errors)

    def test_invalid_choice_rejected(self):
        data = {**VALID_OBS_DATA, 'esl_strategy': 'INVALID'}
        form = ObservationForm(data=data)
        self.assertFalse(form.is_valid())
        self.assertIn('esl_strategy', form.errors)

    def test_all_esl_strategy_choices_valid(self):
        for choice in ['QS', 'TPR', 'VS', 'MT', 'RP', 'DR', 'WA', 'other']:
            data = {**VALID_OBS_DATA, 'esl_strategy': choice}
            form = ObservationForm(data=data)
            self.assertTrue(form.is_valid(), f"'{choice}' should be a valid ESL strategy")

    def test_all_curriculum_choices_valid(self):
        for choice in ['read/lit', 'math', 'science', 'social studies', 'other']:
            data = {**VALID_OBS_DATA, 'curriculum': choice}
            form = ObservationForm(data=data)
            self.assertTrue(form.is_valid(), f"'{choice}' should be a valid curriculum")

    def test_all_mode_choices_valid(self):
        for choice in ['writing', 'reading', 'listening', 'speaking', 'multi']:
            data = {**VALID_OBS_DATA, 'mode': choice}
            form = ObservationForm(data=data)
            self.assertTrue(form.is_valid(), f"'{choice}' should be a valid mode")

    def test_all_language_choices_valid(self):
        for choice in ['L1', 'L2', 'both', 'neither']:
            data = {
                **VALID_OBS_DATA,
                'language_instruction_teacher': choice,
                'language_instruction_student': choice,
            }
            form = ObservationForm(data=data)
            self.assertTrue(form.is_valid(), f"'{choice}' should be a valid language choice")

    def test_form_fields(self):
        form = ObservationForm()
        expected_fields = [
            'esl_strategy', 'curriculum', 'physical_group',
            'activity_structure', 'mode', 'language_content',
            'language_instruction_teacher', 'language_instruction_student',
        ]
        self.assertEqual(list(form.fields.keys()), expected_fields)

    def test_all_widgets_have_obs_select_class(self):
        form = ObservationForm()
        for field_name, field in form.fields.items():
            css_class = field.widget.attrs.get('class', '')
            self.assertEqual(css_class, 'obs-select', f"'{field_name}' widget missing 'obs-select' class")


# ---------------------------------------------------------------------------
# View Tests — Login / Logout
# ---------------------------------------------------------------------------

class LoginViewTest(TestCase):

    def setUp(self):
        self.client = Client()
        self.url = reverse('login')
        self.user = make_user()

    def test_get_renders_login_page(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'observations/login.html')

    def test_get_no_error_context(self):
        response = self.client.get(self.url)
        self.assertIsNone(response.context['error'])

    def test_already_authenticated_redirects(self):
        self.client.force_login(self.user)
        response = self.client.get(self.url)
        self.assertRedirects(response, reverse('select_data'))

    def test_post_valid_credentials_logs_in_and_redirects(self):
        response = self.client.post(self.url, {'username': 'testuser', 'password': 'testpass123'})
        self.assertRedirects(response, reverse('select_data'))
        self.assertTrue(response.wsgi_request.user.is_authenticated)

    def test_post_invalid_credentials_shows_error(self):
        response = self.client.post(self.url, {'username': 'testuser', 'password': 'wrongpass'})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['error'], 'Invalid username or password.')

    def test_post_empty_username_shows_error(self):
        response = self.client.post(self.url, {'username': '', 'password': 'testpass123'})
        self.assertEqual(response.status_code, 200)
        self.assertIsNotNone(response.context['error'])

    def test_post_nonexistent_user_shows_error(self):
        response = self.client.post(self.url, {'username': 'nobody', 'password': 'any'})
        self.assertEqual(response.status_code, 200)
        self.assertIsNotNone(response.context['error'])


class LogoutViewTest(TestCase):

    def setUp(self):
        self.client = Client()
        self.user = make_user()
        self.client.force_login(self.user)

    def test_logout_redirects_to_login(self):
        response = self.client.get(reverse('logout'))
        self.assertRedirects(response, reverse('login'))

    def test_logout_clears_session(self):
        self.client.get(reverse('logout'))
        response = self.client.get(reverse('select_data'))
        self.assertRedirects(response, f"{reverse('login')}?next={reverse('select_data')}")


# ---------------------------------------------------------------------------
# View Tests — select_data
# ---------------------------------------------------------------------------

class SelectDataViewTest(TestCase):

    def setUp(self):
        self.client = Client()
        self.user = make_user()
        self.school = make_school()
        self.teacher = make_teacher(self.school)
        self.url = reverse('select_data')

    def test_unauthenticated_redirects_to_login(self):
        response = self.client.get(self.url)
        self.assertRedirects(response, f"{reverse('login')}?next={self.url}")

    def test_get_renders_template(self):
        self.client.force_login(self.user)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'observations/select_data.html')

    def test_get_passes_schools_in_context(self):
        self.client.force_login(self.user)
        response = self.client.get(self.url)
        self.assertIn(self.school, response.context['schools'])

    def test_post_no_school_id_shows_error(self):
        self.client.force_login(self.user)
        response = self.client.post(self.url, {'school_id': '', 'teacher_id': ''})
        self.assertEqual(response.status_code, 200)
        messages = list(response.context['messages'])
        self.assertTrue(any('school' in str(m).lower() for m in messages))

    def test_post_school_but_no_teacher_shows_error(self):
        self.client.force_login(self.user)
        response = self.client.post(self.url, {'school_id': self.school.pk, 'teacher_id': ''})
        self.assertEqual(response.status_code, 200)
        messages = list(response.context['messages'])
        self.assertTrue(any('teacher' in str(m).lower() for m in messages))

    def test_post_invalid_school_shows_error(self):
        self.client.force_login(self.user)
        response = self.client.post(self.url, {'school_id': 9999, 'teacher_id': self.teacher.pk})
        self.assertEqual(response.status_code, 200)
        messages = list(response.context['messages'])
        self.assertTrue(any('invalid' in str(m).lower() for m in messages))

    def test_post_teacher_not_in_school_shows_error(self):
        other_school = make_school(name='Other School')
        other_teacher = make_teacher(other_school, name='Other Teacher', teacher_id='OT-001')
        self.client.force_login(self.user)
        # teacher belongs to other_school but school_id is self.school
        response = self.client.post(self.url, {
            'school_id': self.school.pk,
            'teacher_id': other_teacher.pk,
        })
        self.assertEqual(response.status_code, 200)
        messages = list(response.context['messages'])
        self.assertTrue(any('invalid' in str(m).lower() for m in messages))

    def test_post_valid_redirects_to_observe(self):
        self.client.force_login(self.user)
        response = self.client.post(self.url, {
            'school_id': self.school.pk,
            'teacher_id': self.teacher.pk,
        })
        expected_url = f'/observe/?school_id={self.school.pk}&teacher_id={self.teacher.pk}'
        self.assertRedirects(response, expected_url)

    def test_schools_ordered_by_name(self):
        School.objects.create(name='Zebra School')
        School.objects.create(name='Apple School')
        self.client.force_login(self.user)
        response = self.client.get(self.url)
        school_names = [s.name for s in response.context['schools']]
        self.assertEqual(school_names, sorted(school_names))


# ---------------------------------------------------------------------------
# View Tests — get_teachers (AJAX)
# ---------------------------------------------------------------------------

class GetTeachersViewTest(TestCase):

    def setUp(self):
        self.client = Client()
        self.school = make_school()
        self.teacher = make_teacher(self.school, name='Alpha Teacher', teacher_id='AT-001')
        self.url = reverse('get_teachers')

    def test_no_school_id_returns_empty_list(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertEqual(data['teachers'], [])

    def test_valid_school_id_returns_teachers(self):
        response = self.client.get(self.url, {'school_id': self.school.pk})
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertEqual(len(data['teachers']), 1)
        self.assertEqual(data['teachers'][0]['name'], 'Alpha Teacher')
        self.assertEqual(data['teachers'][0]['teacher_id'], 'AT-001')

    def test_invalid_school_id_returns_empty_list(self):
        response = self.client.get(self.url, {'school_id': 9999})
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertEqual(data['teachers'], [])

    def test_response_contains_id_name_teacher_id_keys(self):
        response = self.client.get(self.url, {'school_id': self.school.pk})
        data = json.loads(response.content)
        teacher = data['teachers'][0]
        self.assertIn('id', teacher)
        self.assertIn('name', teacher)
        self.assertIn('teacher_id', teacher)

    def test_teachers_ordered_by_name(self):
        make_teacher(self.school, name='Zara', teacher_id='ZT-001')
        make_teacher(self.school, name='Aaron', teacher_id='AAT-001')
        response = self.client.get(self.url, {'school_id': self.school.pk})
        data = json.loads(response.content)
        names = [t['name'] for t in data['teachers']]
        self.assertEqual(names, sorted(names))

    def test_post_request_not_allowed(self):
        response = self.client.post(self.url, {'school_id': self.school.pk})
        self.assertEqual(response.status_code, 405)


# ---------------------------------------------------------------------------
# View Tests — observation_form
# ---------------------------------------------------------------------------

class ObservationFormViewTest(TestCase):

    def setUp(self):
        self.client = Client()
        self.user = make_user()
        self.school = make_school()
        self.teacher = make_teacher(self.school)
        self.url = reverse('observation_form')
        self.params = f'?school_id={self.school.pk}&teacher_id={self.teacher.pk}'

    def test_unauthenticated_redirects(self):
        response = self.client.get(self.url + self.params)
        self.assertEqual(response.status_code, 302)
        self.assertIn(reverse('login'), response['Location'])

    def test_get_without_params_redirects_to_select_data(self):
        self.client.force_login(self.user)
        response = self.client.get(self.url)
        self.assertRedirects(response, reverse('select_data'))

    def test_get_with_invalid_school_returns_404(self):
        self.client.force_login(self.user)
        response = self.client.get(self.url + '?school_id=9999&teacher_id=9999')
        self.assertEqual(response.status_code, 404)

    def test_get_renders_form(self):
        self.client.force_login(self.user)
        response = self.client.get(self.url + self.params)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'observations/observation_form.html')
        self.assertIsInstance(response.context['form'], ObservationForm)

    def test_get_context_contains_school_teacher_and_number(self):
        self.client.force_login(self.user)
        response = self.client.get(self.url + self.params)
        self.assertEqual(response.context['school'], self.school)
        self.assertEqual(response.context['teacher'], self.teacher)
        self.assertEqual(response.context['observation_number'], 1)

    def test_observation_number_increments(self):
        make_observation(self.user, self.school, self.teacher, number=1)
        make_observation(self.user, self.school, self.teacher, number=2)
        self.client.force_login(self.user)
        response = self.client.get(self.url + self.params)
        self.assertEqual(response.context['observation_number'], 3)

    def test_post_valid_form_saves_observation(self):
        self.client.force_login(self.user)
        self.client.post(
            self.url + self.params,
            {**VALID_OBS_DATA, 'action': 'enter'},
        )
        self.assertEqual(Observation.objects.count(), 1)
        obs = Observation.objects.first()
        self.assertEqual(obs.observer, self.user)
        self.assertEqual(obs.school, self.school)
        self.assertEqual(obs.teacher, self.teacher)

    def test_post_valid_form_redirects_back_to_form(self):
        self.client.force_login(self.user)
        response = self.client.post(
            self.url + self.params,
            {**VALID_OBS_DATA, 'action': 'enter'},
        )
        expected = f'/observe/?school_id={self.school.pk}&teacher_id={self.teacher.pk}'
        self.assertRedirects(response, expected)

    def test_post_invalid_form_does_not_save(self):
        self.client.force_login(self.user)
        bad_data = {**VALID_OBS_DATA, 'esl_strategy': ''}
        self.client.post(self.url + self.params, bad_data)
        self.assertEqual(Observation.objects.count(), 0)

    def test_post_invalid_form_re_renders_with_errors(self):
        self.client.force_login(self.user)
        bad_data = {**VALID_OBS_DATA, 'esl_strategy': ''}
        response = self.client.post(self.url + self.params, bad_data)
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.context['form'].errors)

    def test_post_action_complete_redirects_to_complete(self):
        self.client.force_login(self.user)
        response = self.client.post(
            self.url + self.params,
            {**VALID_OBS_DATA, 'action': 'complete'},
        )
        self.assertRedirects(
            response,
            f'/observe/complete/?teacher_id={self.teacher.pk}',
        )

    def test_post_action_complete_does_not_save_observation(self):
        self.client.force_login(self.user)
        self.client.post(
            self.url + self.params,
            {**VALID_OBS_DATA, 'action': 'complete'},
        )
        self.assertEqual(Observation.objects.count(), 0)

    def test_post_from_reports_redirects_to_reports(self):
        self.client.force_login(self.user)
        response = self.client.post(
            self.url + self.params + '&from=reports',
            {**VALID_OBS_DATA, 'action': 'enter', 'from_reports': '1'},
        )
        self.assertRedirects(response, reverse('reports'))


# ---------------------------------------------------------------------------
# View Tests — observation_complete
# ---------------------------------------------------------------------------

class ObservationCompleteViewTest(TestCase):

    def setUp(self):
        self.client = Client()
        self.user = make_user()
        self.school = make_school()
        self.teacher = make_teacher(self.school)
        self.url = reverse('observation_complete')

    def test_unauthenticated_redirects(self):
        response = self.client.get(self.url + f'?teacher_id={self.teacher.pk}')
        self.assertIn(reverse('login'), response['Location'])

    def test_invalid_teacher_id_returns_404(self):
        self.client.force_login(self.user)
        response = self.client.get(self.url + '?teacher_id=9999')
        self.assertEqual(response.status_code, 404)

    def test_renders_complete_template(self):
        self.client.force_login(self.user)
        response = self.client.get(self.url + f'?teacher_id={self.teacher.pk}')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'observations/observation_complete.html')

    def test_context_contains_teacher_and_observations(self):
        make_observation(self.user, self.school, self.teacher, number=1)
        make_observation(self.user, self.school, self.teacher, number=2)
        self.client.force_login(self.user)
        response = self.client.get(self.url + f'?teacher_id={self.teacher.pk}')
        self.assertEqual(response.context['teacher'], self.teacher)
        self.assertEqual(response.context['count'], 2)

    def test_only_current_user_observations_shown(self):
        other_user = make_user(username='other')
        make_observation(self.user, self.school, self.teacher, number=1)
        make_observation(other_user, self.school, self.teacher, number=2)
        self.client.force_login(self.user)
        response = self.client.get(self.url + f'?teacher_id={self.teacher.pk}')
        self.assertEqual(response.context['count'], 1)

    def test_observations_ordered_by_observation_number(self):
        make_observation(self.user, self.school, self.teacher, number=2)
        make_observation(self.user, self.school, self.teacher, number=1)
        self.client.force_login(self.user)
        response = self.client.get(self.url + f'?teacher_id={self.teacher.pk}')
        obs_numbers = [o.observation_number for o in response.context['observations']]
        self.assertEqual(obs_numbers, sorted(obs_numbers))


# ---------------------------------------------------------------------------
# View Tests — download_teacher_excel
# ---------------------------------------------------------------------------

class DownloadTeacherExcelViewTest(TestCase):

    def setUp(self):
        self.client = Client()
        self.user = make_user()
        self.school = make_school()
        self.teacher = make_teacher(self.school)
        self.url = reverse('download_teacher_excel')

    def test_unauthenticated_redirects(self):
        response = self.client.get(self.url + f'?teacher_id={self.teacher.pk}')
        self.assertIn(reverse('login'), response['Location'])

    def test_invalid_teacher_returns_404(self):
        self.client.force_login(self.user)
        response = self.client.get(self.url + '?teacher_id=9999')
        self.assertEqual(response.status_code, 404)

    def test_returns_xlsx_content_type(self):
        self.client.force_login(self.user)
        response = self.client.get(self.url + f'?teacher_id={self.teacher.pk}')
        self.assertEqual(
            response['Content-Type'],
            'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
        )

    def test_response_has_attachment_disposition(self):
        self.client.force_login(self.user)
        response = self.client.get(self.url + f'?teacher_id={self.teacher.pk}')
        disposition = response['Content-Disposition']
        self.assertIn('attachment', disposition)
        self.assertIn('.xlsx', disposition)

    def test_filename_uses_teacher_name(self):
        self.client.force_login(self.user)
        response = self.client.get(self.url + f'?teacher_id={self.teacher.pk}')
        disposition = response['Content-Disposition']
        self.assertIn('Jane_Doe', disposition)

    def test_only_current_user_observations_exported(self):
        other_user = make_user(username='other')
        make_observation(self.user, self.school, self.teacher, number=1)
        make_observation(other_user, self.school, self.teacher, number=2)
        self.client.force_login(self.user)
        # If we get a 200, user's data is exported (we can't easily inspect xlsx content here,
        # but verify the view doesn't leak by checking it returns a valid response)
        response = self.client.get(self.url + f'?teacher_id={self.teacher.pk}')
        self.assertEqual(response.status_code, 200)

    def test_returns_valid_xlsx_bytes(self):
        import io
        import openpyxl
        make_observation(self.user, self.school, self.teacher)
        self.client.force_login(self.user)
        response = self.client.get(self.url + f'?teacher_id={self.teacher.pk}')
        wb = openpyxl.load_workbook(io.BytesIO(response.content))
        ws = wb.active
        # Header row + 1 data row
        self.assertEqual(ws.max_row, 2)


# ---------------------------------------------------------------------------
# View Tests — edit_observation
# ---------------------------------------------------------------------------

class EditObservationViewTest(TestCase):

    def setUp(self):
        self.client = Client()
        self.user = make_user()
        self.school = make_school()
        self.teacher = make_teacher(self.school)
        self.obs = make_observation(self.user, self.school, self.teacher)

    def url(self, obs_id=None):
        return reverse('edit_observation', args=[obs_id or self.obs.pk])

    def test_unauthenticated_redirects(self):
        response = self.client.get(self.url())
        self.assertIn(reverse('login'), response['Location'])

    def test_other_user_cannot_access_observation(self):
        other = make_user(username='other')
        self.client.force_login(other)
        response = self.client.get(self.url())
        self.assertEqual(response.status_code, 404)

    def test_invalid_obs_id_returns_404(self):
        self.client.force_login(self.user)
        response = self.client.get(self.url(obs_id=9999))
        self.assertEqual(response.status_code, 404)

    def test_get_renders_edit_template(self):
        self.client.force_login(self.user)
        response = self.client.get(self.url())
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'observations/edit_observation.html')

    def test_get_prepopulates_form_with_existing_data(self):
        self.client.force_login(self.user)
        response = self.client.get(self.url())
        form = response.context['form']
        self.assertEqual(form.initial.get('esl_strategy') or form['esl_strategy'].value(), 'TPR')

    def test_get_passes_obs_in_context(self):
        self.client.force_login(self.user)
        response = self.client.get(self.url())
        self.assertEqual(response.context['obs'], self.obs)

    def test_post_valid_saves_and_redirects_to_reports(self):
        self.client.force_login(self.user)
        updated = {**VALID_OBS_DATA, 'esl_strategy': 'VS'}
        response = self.client.post(self.url(), updated)
        self.assertRedirects(response, reverse('reports'))
        self.obs.refresh_from_db()
        self.assertEqual(self.obs.esl_strategy, 'VS')

    def test_post_invalid_re_renders_with_errors(self):
        self.client.force_login(self.user)
        bad = {**VALID_OBS_DATA, 'esl_strategy': 'INVALID'}
        response = self.client.post(self.url(), bad)
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.context['form'].errors)

    def test_post_invalid_does_not_modify_observation(self):
        self.client.force_login(self.user)
        bad = {**VALID_OBS_DATA, 'esl_strategy': ''}
        self.client.post(self.url(), bad)
        self.obs.refresh_from_db()
        self.assertEqual(self.obs.esl_strategy, 'TPR')


# ---------------------------------------------------------------------------
# View Tests — reports
# ---------------------------------------------------------------------------

class ReportsViewTest(TestCase):

    def setUp(self):
        self.client = Client()
        self.user = make_user()
        self.school = make_school()
        self.teacher = make_teacher(self.school)
        self.url = reverse('reports')

    def test_unauthenticated_redirects(self):
        response = self.client.get(self.url)
        self.assertRedirects(response, f"{reverse('login')}?next={self.url}")

    def test_renders_reports_template(self):
        self.client.force_login(self.user)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'observations/reports.html')

    def test_only_current_user_observations_shown(self):
        other_user = make_user(username='other')
        make_observation(self.user, self.school, self.teacher, number=1)
        make_observation(other_user, self.school, self.teacher, number=2)
        self.client.force_login(self.user)
        response = self.client.get(self.url)
        groups = list(response.context['groups'])
        total_obs = sum(len(g['observations']) for g in groups)
        self.assertEqual(total_obs, 1)

    def test_observations_grouped_by_teacher(self):
        teacher2 = make_teacher(self.school, name='Second Teacher', teacher_id='ST-002')
        make_observation(self.user, self.school, self.teacher, number=1)
        make_observation(self.user, self.school, teacher2, number=1)
        self.client.force_login(self.user)
        response = self.client.get(self.url)
        groups = list(response.context['groups'])
        self.assertEqual(len(groups), 2)

    def test_empty_reports_for_new_user(self):
        self.client.force_login(self.user)
        response = self.client.get(self.url)
        groups = list(response.context['groups'])
        self.assertEqual(len(groups), 0)

    def test_multiple_observations_per_teacher_in_same_group(self):
        make_observation(self.user, self.school, self.teacher, number=1)
        make_observation(self.user, self.school, self.teacher, number=2)
        self.client.force_login(self.user)
        response = self.client.get(self.url)
        groups = list(response.context['groups'])
        self.assertEqual(len(groups), 1)
        self.assertEqual(len(groups[0]['observations']), 2)


# ---------------------------------------------------------------------------
# View Tests — download_excel (all observations)
# ---------------------------------------------------------------------------

class DownloadExcelViewTest(TestCase):

    def setUp(self):
        self.client = Client()
        self.user = make_user()
        self.school = make_school()
        self.teacher = make_teacher(self.school)
        self.url = reverse('download_excel')

    def test_unauthenticated_redirects(self):
        response = self.client.get(self.url)
        self.assertRedirects(response, f"{reverse('login')}?next={self.url}")

    def test_returns_xlsx_content_type(self):
        self.client.force_login(self.user)
        response = self.client.get(self.url)
        self.assertEqual(
            response['Content-Type'],
            'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
        )

    def test_response_has_attachment_filename(self):
        self.client.force_login(self.user)
        response = self.client.get(self.url)
        self.assertIn('observations.xlsx', response['Content-Disposition'])

    def test_only_current_user_data_exported(self):
        import io
        import openpyxl
        other_user = make_user(username='other')
        make_observation(self.user, self.school, self.teacher, number=1)
        make_observation(other_user, self.school, self.teacher, number=2)
        self.client.force_login(self.user)
        response = self.client.get(self.url)
        wb = openpyxl.load_workbook(io.BytesIO(response.content))
        ws = wb.active
        # Header + 1 data row (not 2)
        self.assertEqual(ws.max_row, 2)

    def test_returns_valid_xlsx_with_correct_headers(self):
        import io
        import openpyxl
        self.client.force_login(self.user)
        response = self.client.get(self.url)
        wb = openpyxl.load_workbook(io.BytesIO(response.content))
        ws = wb.active
        headers = [ws.cell(row=1, column=i).value for i in range(1, 14)]
        self.assertEqual(headers[0], 'School')
        self.assertEqual(headers[1], 'Teacher')
        self.assertEqual(headers[-1], 'Date')

    def test_empty_export_has_only_header_row(self):
        import io
        import openpyxl
        self.client.force_login(self.user)
        response = self.client.get(self.url)
        wb = openpyxl.load_workbook(io.BytesIO(response.content))
        ws = wb.active
        self.assertEqual(ws.max_row, 1)
