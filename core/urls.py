from django.urls import path
from .views import (
    HomeView, RegisterView, CustomLoginView, LogoutView,
    ProfileView, ResumeListView, ResumeCreateView, ResumeUpdateView,
    ResumeDeleteView, ResumeCloneView, ResumePreviewView,
    TemplateListView, AnnouncementListView, AnnouncementCreateView,
    AnnouncementUpdateView, AnnouncementDeleteView, export_pdf, export_docx
)

urlpatterns = [
    path('', HomeView.as_view(), name='home'),
    path('register/', RegisterView.as_view(), name='register'),
    path('login/', CustomLoginView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(next_page='home'), name='logout'),
    path('profile/', ProfileView.as_view(), name='profile'),
    path('resumes/', ResumeListView.as_view(), name='resumes'),
    path('resume/create/', ResumeCreateView.as_view(), name='resume_create'),
    path('resume/<int:pk>/edit/', ResumeUpdateView.as_view(), name='resume_edit'),
    path('resume/<int:pk>/delete/', ResumeDeleteView.as_view(), name='resume_delete'),
    path('resume/<int:pk>/clone/', ResumeCloneView.as_view(), name='resume_clone'),
    path('resume/<int:pk>/preview/', ResumePreviewView.as_view(), name='resume_preview'),
    path('resume/<int:pk>/export/pdf/', export_pdf, name='export_pdf'),
    path('resume/<int:pk>/export/docx/', export_docx, name='export_docx'),
    path('templates/', TemplateListView.as_view(), name='templates'),
    path('announcements/', AnnouncementListView.as_view(), name='announcements'),
    path('announcement/create/', AnnouncementCreateView.as_view(), name='announcement_create'),
    path('announcement/<int:pk>/edit/', AnnouncementUpdateView.as_view(), name='announcement_edit'),
    path('announcement/<int:pk>/delete/', AnnouncementDeleteView.as_view(), name='announcement_delete'),
]