from django.db import models
from django.contrib.auth.models import User

# Модель "Профіль" 
class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    bio = models.TextField(blank=True, null=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Profile of {self.user.username}"

    class Meta:
        verbose_name = 'Profile'
        verbose_name_plural = 'Profiles'


# Модель "Шаблон для резюме" 
class ResumeTemplate(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)
    html_template = models.TextField()  # Зберігає HTML-шаблон для рендерингу
    created_at = models.DateTimeField(auto_now_add=True)
    image = models.ImageField(upload_to='templates/', null=True, blank=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Resume Template'
        verbose_name_plural = 'Resume Templates'


# Модель "Резюме" 
class Resume(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='resumes')
    title = models.CharField(max_length=100)
    template = models.ForeignKey(ResumeTemplate, on_delete=models.SET_NULL, null=True, blank=True)
    photo = models.ImageField(upload_to='photos/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.title} by {self.user.username}"

    class Meta:
        verbose_name = 'Resume'
        verbose_name_plural = 'Resumes'


# Модель "Секція резюме" 
class ResumeSection(models.Model):
    SECTION_TYPES = (
        ('personal', 'Personal Information'),
        ('experience', 'Work Experience'),
        ('education', 'Education'),
        ('skills', 'Skills'),
        ('other', 'Other'),
    )
    resume = models.ForeignKey(Resume, on_delete=models.CASCADE, related_name='sections')
    section_type = models.CharField(max_length=50, choices=SECTION_TYPES)
    content = models.TextField()
    order = models.IntegerField(default=0)

    def __str__(self):
        return f"{self.section_type} for {self.resume.title}"

    class Meta:
        verbose_name = 'Resume Section'
        verbose_name_plural = 'Resume Sections'
        ordering = ['order']


# Модель "Оголошення" 
class Announcement(models.Model):
    title = models.CharField(max_length=200)
    content = models.TextField()
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='announcements')
    created_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = 'Announcement'
        verbose_name_plural = 'Announcements'
        ordering = ['-created_at']