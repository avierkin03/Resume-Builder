from django import forms
from django.contrib.auth.models import User
from django.forms import modelformset_factory
from .models import Profile, Resume, ResumeSection, Announcement

class RegistrationForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput, label="Пароль")
    confirm_password = forms.CharField(widget=forms.PasswordInput, label="Підтвердження пароля")

    class Meta:
        model = User
        fields = ['username', 'email', 'password']
        labels = {
            'username': 'Ім\'я користувача',
            'email': 'Електронна пошта',
        }

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get("password")
        confirm_password = cleaned_data.get("confirm_password")
        if password and confirm_password and password != confirm_password:
            raise forms.ValidationError("Паролі не збігаються.")
        return cleaned_data

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data['password'])
        if commit:
            user.save()
        return user

class ProfileForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ['bio']
        labels = {
            'bio': 'Про себе',
        }
        widgets = {
            'bio': forms.Textarea(attrs={'rows': 4, 'class': 'form-control'}),
        }

class ResumeForm(forms.ModelForm):
    class Meta:
        model = Resume
        fields = ['title', 'template', 'photo']
        labels = {
            'title': 'Назва резюме',
            'template': 'Шаблон',
            'photo': 'Фотографія',
        }
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'template': forms.Select(attrs={'class': 'form-control'}),
            'photo': forms.FileInput(attrs={'class': 'form-control-file'}),
        }

class ResumeSectionForm(forms.ModelForm):
    class Meta:
        model = ResumeSection
        fields = ['section_type', 'content', 'order']
        labels = {
            'section_type': 'Тип секції',
            'content': 'Вміст',
            'order': 'Порядок',
        }
        widgets = {
            'section_type': forms.Select(attrs={'class': 'form-control'}),
            'content': forms.Textarea(attrs={'rows': 3, 'class': 'form-control'}),
            'order': forms.NumberInput(attrs={'class': 'form-control'}),
        }

SectionFormSet = modelformset_factory(
    ResumeSection,
    form=ResumeSectionForm,
    extra=1,
    can_delete=True,
)

class AnnouncementForm(forms.ModelForm):
    class Meta:
        model = Announcement
        fields = ['title', 'content', 'is_active']
        labels = {
            'title': 'Заголовок',
            'content': 'Вміст',
            'is_active': 'Активне',
        }
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'content': forms.Textarea(attrs={'rows': 5, 'class': 'form-control'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }