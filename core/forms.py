from django import forms
from django.contrib.auth.models import User
from django.forms import inlineformset_factory
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
            # Створюємо профіль для нового користувача
            Profile.objects.get_or_create(user=user)
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
            'section_type': forms.HiddenInput(),
            'content': forms.Textarea(attrs={'rows': 3, 'class': 'form-control'}),
            'order': forms.NumberInput(attrs={'class': 'form-control'}),
        }

    def clean(self):
        cleaned_data = super().clean()
        section_type = cleaned_data.get('section_type') or self.initial.get('section_type')
        content = cleaned_data.get('content')
        order = cleaned_data.get('order')

        if not section_type:
            raise forms.ValidationError("Тип секції має бути вказаний.")
        cleaned_data['section_type'] = section_type
        # Дозволяємо порожній content для нових форм, щоб уникнути помилки
        if not content and self.instance.pk:
            self.add_error('content', "Це поле є обов'язковим для існуючих секцій.")
        if order is None:
            self.add_error('order', "Це поле є обов'язковим.")
        return cleaned_data

# Список фіксованих типів секцій
SECTION_TYPES = ['personal', 'experience', 'education', 'skills', 'other']

SectionFormSet = inlineformset_factory(
    Resume,
    ResumeSection,
    form=ResumeSectionForm,
    fields=['section_type', 'content', 'order'],
    extra=5,  # Не додаємо зайвих форм
    can_delete=False
)
# Налаштування фіксованих типів секцій
def get_section_formset(resume=None):
    if resume:
        # Для редагування: використовуємо існуючі секції
        existing_sections = resume.sections.filter(section_type__in=SECTION_TYPES).order_by('order')
        section_types_map = {section.section_type: section for section in existing_sections}
        # Додаємо відсутні типи секцій
        missing_types = [t for t in SECTION_TYPES if t not in section_types_map]
        for i, section_type in enumerate(missing_types):
            ResumeSection.objects.create(
                resume=resume,
                section_type=section_type,
                content='',
                order=len(existing_sections) + i
            )
        # Оновлюємо formset після додавання секцій
        formset = SectionFormSet(
            instance=resume,
            queryset=resume.sections.filter(section_type__in=SECTION_TYPES).order_by('order')
        )
        # Ініціалізуємо форми (максимум 5)
        for i, form in enumerate(formset.forms[:len(SECTION_TYPES)]):
            if i < len(SECTION_TYPES):
                form.initial['section_type'] = SECTION_TYPES[i]
                form.initial['order'] = i
            form.fields['section_type'].required = False
    else:
        # Для створення: створюємо 5 порожніх форм
        formset = SectionFormSet(instance=Resume())
        # Додаємо форми, якщо їх менше 5
        if len(formset.forms) < len(SECTION_TYPES):
            formset.extra = len(SECTION_TYPES) - len(formset.forms)
            formset.forms.extend([formset.empty_form for _ in range(formset.extra)])
        # Обрізаємо до 5 форм
        formset.forms = formset.forms[:len(SECTION_TYPES)]
        for i, form in enumerate(formset.forms):
            form.initial['section_type'] = SECTION_TYPES[i]
            form.initial['order'] = i
            form.fields['section_type'].required = False
    return formset

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