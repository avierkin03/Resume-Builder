from django.contrib import admin
from .models import Profile, ResumeTemplate, Resume, ResumeSection, Announcement

admin.site.register(Profile)
admin.site.register(ResumeTemplate)
admin.site.register(Resume)
admin.site.register(ResumeSection)
admin.site.register(Announcement)
