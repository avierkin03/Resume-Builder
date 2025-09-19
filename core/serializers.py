from rest_framework import serializers
from .models import Profile, ResumeTemplate, Resume, ResumeSection, Announcement

# Серіалізатор для моделі "Profile"
class ProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = Profile
        fields = "__all__"


# Серіалізатор для моделі "ResumeTemplate"
class ResumeTemplateSerializer(serializers.ModelSerializer):
    class Meta:
        model = ResumeTemplate
        fields = "__all__"


# Серіалізатор для моделі "Resume"
class ResumeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Resume
        fields = "__all__"


# Серіалізатор для моделі "ResumeSection"
class ResumeSectionSerializer(serializers.ModelSerializer):
    class Meta:
        model = ResumeSection
        fields = "__all__"


# Серіалізатор для моделі "Announcement"
class AnnouncementSerializer(serializers.ModelSerializer):
    class Meta:
        model = Announcement
        fields = "__all__"