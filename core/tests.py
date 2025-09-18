from django.test import TestCase, Client
from django.contrib.auth.models import User, Group
from django.urls import reverse
from .models import Profile, ResumeTemplate, Resume, ResumeSection, Announcement
from .forms import RegistrationForm, ProfileForm, ResumeForm, ResumeSectionForm, AnnouncementForm
from .serializers import ProfileSerializer, ResumeTemplateSerializer, ResumeSerializer, ResumeSectionSerializer, AnnouncementSerializer

# Тестування моделей
class ModelTests(TestCase):
    def test_profile_str(self):
        """Тест методу __str__ для моделі Profile"""
        user = User.objects.create(username='testuser')
        profile = Profile.objects.create(user=user, bio='Тестовий біо')
        self.assertEqual(str(profile), "Profile of testuser")

    def test_resume_template_str(self):
        """Тест методу __str__ для моделі ResumeTemplate"""
        template = ResumeTemplate.objects.create(name='Тестовий шаблон', description='Опис')
        self.assertEqual(str(template), 'Тестовий шаблон')

    def test_resume_str(self):
        """Тест методу __str__ для моделі Resume"""
        user = User.objects.create(username='testuser')
        resume = Resume.objects.create(user=user, title='Тестове резюме')
        self.assertEqual(str(resume), 'Тестове резюме by testuser')

    def test_resume_section_str(self):
        """Тест методу __str__ для моделі ResumeSection"""
        user = User.objects.create(username='testuser')
        resume = Resume.objects.create(user=user, title='Тестове резюме')
        section = ResumeSection.objects.create(resume=resume, section_type='personal', content='Контент')
        self.assertEqual(str(section), 'personal for Тестове резюме')

    def test_announcement_str(self):
        """Тест методу __str__ для моделі Announcement"""
        user = User.objects.create(username='testuser')
        announcement = Announcement.objects.create(title='Тестове оголошення', content='Контент', created_by=user)
        self.assertEqual(str(announcement), 'Тестове оголошення')


# Тестування форм
class FormTests(TestCase):
    def test_registration_form_valid(self):
        """Тест валідності форми реєстрації з коректними даними"""
        data = {
            'username': 'testuser',
            'email': 'test@example.com',
            'password': 'testpassword123',
            'confirm_password': 'testpassword123',
        }
        form = RegistrationForm(data)
        self.assertTrue(form.is_valid())

    def test_registration_form_invalid_password_mismatch(self):
        """Тест невалідності форми реєстрації при невідповідності паролів"""
        data = {
            'username': 'testuser',
            'email': 'test@example.com',
            'password': 'testpassword123',
            'confirm_password': 'wrongpassword',
        }
        form = RegistrationForm(data)
        self.assertFalse(form.is_valid())
        self.assertIn("Паролі не збігаються.", form.errors['__all__'])

    def test_profile_form_valid(self):
        """Тест валідності форми профілю"""
        data = {'bio': 'Тестовий біо'}
        form = ProfileForm(data)
        self.assertTrue(form.is_valid())

    def test_resume_form_valid(self):
        """Тест валідності форми резюме"""
        data = {'title': 'Тестове резюме'}
        form = ResumeForm(data)
        self.assertTrue(form.is_valid())

    def test_resume_section_form_valid(self):
        """Тест валідності форми секції резюме"""
        data = {
            'section_type': 'personal',
            'content': 'Тестовий контент',
            'order': 0
        }
        form = ResumeSectionForm(data)
        self.assertTrue(form.is_valid())

    def test_announcement_form_valid(self):
        """Тест валідності форми оголошення"""
        data = {
            'title': 'Тестове оголошення',
            'content': 'Тестовий контент',
            'is_active': True
        }
        form = AnnouncementForm(data)
        self.assertTrue(form.is_valid())


# Тестування в'юшок
class ViewTests(TestCase):
    def setUp(self):
        """Налаштування для тестів в'юшок"""
        self.client = Client()
        self.user = User.objects.create_user(username='testuser', password='testpassword')
        self.client.login(username='testuser', password='testpassword')
        self.template = ResumeTemplate.objects.create(name='Тестовий шаблон')
        self.resume = Resume.objects.create(user=self.user, title='Тестове резюме', template=self.template)
        self.announcement = Announcement.objects.create(title='Тестове оголошення', content='Контент', created_by=self.user)

    def test_home_view(self):
        """Тест домашньої сторінки"""
        response = self.client.get(reverse('home'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'home.html')

    def test_register_view_get(self):
        """Тест сторінки реєстрації (GET)"""
        response = self.client.get(reverse('register'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'register.html')

    def test_register_view_post(self):
        """Тест реєстрації (POST)"""
        data = {
            'username': 'newuser',
            'email': 'new@example.com',
            'password': 'newpassword123',
            'confirm_password': 'newpassword123',
        }
        response = self.client.post(reverse('register'), data)
        self.assertEqual(response.status_code, 302)  # Перенаправлення на home
        self.assertTrue(User.objects.filter(username='newuser').exists())

    def test_login_view_get(self):
        """Тест сторінки логіну (GET)"""
        response = self.client.get(reverse('login'))
        self.assertEqual(response.status_code, 302) # Перенаправлення на home

    def test_profile_view(self):
        """Тест сторінки профілю"""
        response = self.client.get(reverse('profile'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'profile.html')

    def test_resume_list_view(self):
        """Тест списку резюме"""
        response = self.client.get(reverse('resumes'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'resume_list.html')
        self.assertContains(response, self.resume.title)

    def test_resume_create_view_get(self):
        """Тест сторінки створення резюме (GET)"""
        response = self.client.get(reverse('resume_create'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'resume_form.html')

    def test_resume_create_view_post(self):
        """Тест створення резюме (POST)"""
        data = {
            'title': 'Нове резюме',
            'template': self.template.id,
            'form-TOTAL_FORMS': 5,
            'form-INITIAL_FORMS': 0,
            'form-MIN_NUM_FORMS': 0,
            'form-MAX_NUM_FORMS': 1000,
            'form-0-section_type': 'personal',
            'form-0-content': 'Тестовий контент',
            'form-0-order': 0,
            'form-1-section_type': 'personal',
            'form-1-content': 'Тестовий контент',
            'form-1-order': 1,
            'form-2-section_type': 'experience',
            'form-2-content': 'Тестовий контент',
            'form-2-order': 2,
            'form-3-section_type': 'education',
            'form-3-content': 'Тестовий контент',
            'form-3-order': 3,
            'form-4-section_type': 'skills',
            'form-4-content': 'Тестовий контент',
            'form-4-order': 4,
            'form-5-section_type': 'other',
            'form-5-content': 'Тестовий контент',
            'form-5-order': 5,
        }
        response = self.client.post(reverse('resume_create'), data)
        self.assertEqual(response.status_code, 200) 
        self.assertTrue(Resume.objects.filter(title='Нове резюме').exists())

    def test_resume_update_view(self):
        """Тест редагування резюме"""
        response = self.client.get(reverse('resume_edit', kwargs={'pk': self.resume.pk}))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'resume_form.html')

    def test_resume_delete_view(self):
        """Тест видалення резюме"""
        response = self.client.post(reverse('resume_delete', kwargs={'pk': self.resume.pk}))
        self.assertEqual(response.status_code, 302)  # Перенаправлення на resumes
        self.assertFalse(Resume.objects.filter(pk=self.resume.pk).exists())

    def test_resume_preview_view(self):
        """Тест попереднього перегляду резюме"""
        response = self.client.get(reverse('resume_preview', kwargs={'pk': self.resume.pk}))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'resume_preview.html')

    def test_announcement_create_view(self):
        """Тест створення оголошення"""
        group = Group.objects.create(name='admins')
        self.user.groups.add(group)
        data = {
            'title': 'Нове оголошення',
            'content': 'Тестовий контент',
            'is_active': True
        }
        response = self.client.post(reverse('announcement_create'), data)
        self.assertEqual(response.status_code, 302)  # Перенаправлення на announcements
        self.assertTrue(Announcement.objects.filter(title='Нове оголошення').exists())

    def test_template_ajax(self):
        """Тест AJAX-в'ю для шаблонів"""
        response = self.client.get(reverse('template_ajax') + '?page=1')
        self.assertEqual(response.status_code, 200)
        self.assertTrue('templates' in response.json())

    def test_export_pdf(self):
        """Тест експорту PDF"""
        response = self.client.get(reverse('export_pdf', kwargs={'pk': self.resume.pk}))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'application/pdf')

    def test_export_docx(self):
        """Тест експорту DOCX"""
        response = self.client.get(reverse('export_docx', kwargs={'pk': self.resume.pk}))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'application/vnd.openxmlformats-officedocument.wordprocessingml.document')


# Тестування серіалізаторів
class SerializerTests(TestCase):
    def test_profile_serializer(self):
        """Тест серіалізатора Profile"""
        user = User.objects.create(username='testuser')
        profile = Profile.objects.create(user=user, bio='Тестовий біо')
        serializer = ProfileSerializer(profile)
        self.assertEqual(serializer.data['user'], user.pk)
        self.assertEqual(serializer.data['bio'], 'Тестовий біо')

    def test_resume_template_serializer(self):
        """Тест серіалізатора ResumeTemplate""" 
        template = ResumeTemplate.objects.create(name='Тестовий шаблон')
        serializer = ResumeTemplateSerializer(template)
        self.assertEqual(serializer.data['name'], 'Тестовий шаблон')

    def test_resume_serializer(self):
        """Тест серіалізатора ResumeSerializer""" 
        user = User.objects.create(username='testuser')
        resume = Resume.objects.create(user=user, title='Тестове резюме')
        serializer = ResumeSerializer(resume)
        self.assertEqual(serializer.data['user'], user.pk)
        self.assertEqual(serializer.data['title'], 'Тестове резюме')

    def test_resume_section_serializer(self):
        """Тест серіалізатора ResumeSectionSerializer""" 
        user = User.objects.create(username='testuser')
        resume = Resume.objects.create(user=user, title='Тестове резюме')
        section = ResumeSection.objects.create(resume=resume, section_type='personal', content='Контент')
        serializer = ResumeSectionSerializer(section)
        self.assertEqual(serializer.data['resume'], resume.pk)
        self.assertEqual(serializer.data['section_type'], 'personal')
        self.assertEqual(serializer.data['content'], 'Контент')

    def test_announcement_serializer(self):
        """Тест серіалізатора AnnouncementSerializer"""
        user = User.objects.create(username='testuser')
        announcement = Announcement.objects.create(title='Тестове оголошення', content='Контент', created_by=user) 
        serializer = AnnouncementSerializer(announcement)
        self.assertEqual(serializer.data['title'], 'Тестове оголошення')
        self.assertEqual(serializer.data['content'], 'Контент')
        self.assertEqual(serializer.data['created_by'], user.pk)

# python manage.py test