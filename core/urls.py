from django.urls import path
from core import views

urlpatterns = [
    path('', views.HomeView.as_view(), name='home'),
    path('register/', views.RegisterView.as_view(), name='register'),
    path('login/', views.CustomLoginView.as_view(), name='login'),
    path('logout/', views.LogoutView.as_view(next_page='home'), name='logout'),
    path('profile/', views.ProfileView.as_view(), name='profile'),
    path('resumes/', views.ResumeListView.as_view(), name='resumes'),
    path('resume/create/', views.ResumeCreateView.as_view(), name='resume_create'),
    path('resume/<int:pk>/edit/', views.ResumeUpdateView.as_view(), name='resume_edit'),
    path('resume/<int:pk>/delete/', views.ResumeDeleteView.as_view(), name='resume_delete'),
    path('resume/<int:pk>/clone/', views.ResumeCloneView.as_view(), name='resume_clone'),
    path('resume/<int:pk>/preview/', views.ResumePreviewView.as_view(), name='resume_preview'),
    path('resume/<int:pk>/export/pdf/', views.export_pdf, name='export_pdf'),
    path('resume/<int:pk>/export/docx/', views.export_docx, name='export_docx'),
    path('templates/', views.TemplateListView.as_view(), name='templates'),
    path('templates/ajax/', views.template_ajax, name='template_ajax'),
    path('announcements/', views.AnnouncementListView.as_view(), name='announcements'),
    path('announcement/create/', views.AnnouncementCreateView.as_view(), name='announcement_create'),
    path('announcement/<int:pk>/edit/', views.AnnouncementUpdateView.as_view(), name='announcement_edit'),
    path('announcement/<int:pk>/delete/', views.AnnouncementDeleteView.as_view(), name='announcement_delete'),
    # drf
    path('api/profiles/', views.ProfileListAPI.as_view(),name='profiles-list-api'),
    path('api/profile/<int:pk>', views.ProfileDetailAPI.as_view(),name='profile-detail-api'),
    path('api/resume-templates/', views.ResumeTemplateListAPI.as_view(),name='resume-templates-list-api'),
    path('api/resume-template/<int:pk>', views.ResumeTemplateDetailAPI.as_view(),name='resume-template-detail-api'),
    path('api/resumes/', views.ResumeListAPI.as_view(),name='resumes-list-api'),
    path('api/resume/<int:pk>', views.ResumeDetailAPI.as_view(),name='resume-detail-api'),
    path('api/resume-sections/', views.ResumeSectionListAPI.as_view(),name='resume-sections-list-api'),
    path('api/resume-section/<int:pk>', views.ResumeSectionDetailAPI.as_view(),name='resume-section-detail-api'),
    path('api/announcements/', views.AnnouncementListAPI.as_view(),name='announcements-list-api'),
    path('api/announcement/<int:pk>', views.AnnouncementDetailAPI.as_view(),name='announcement-detail-api'),

]