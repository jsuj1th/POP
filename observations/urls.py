from django.urls import path
from . import views

urlpatterns = [
    path('', views.select_data, name='select_data'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('observe/', views.observation_form, name='observation_form'),
    path('observe/complete/', views.observation_complete, name='observation_complete'),
    path('observe/download/', views.download_teacher_excel, name='download_teacher_excel'),
    path('observe/download/select/', views.select_session_download, name='select_session_download'),
    path('reports/', views.reports, name='reports'),
    path('reports/edit/<int:obs_id>/', views.edit_observation, name='edit_observation'),
    path('reports/download/', views.download_excel, name='download_excel'),
    path('api/teachers/', views.get_teachers, name='get_teachers'),
]
