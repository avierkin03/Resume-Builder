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
            'section_type': forms.HiddenInput(),  # Приховуємо поле section_type
            'content': forms.Textarea(attrs={'rows': 3, 'class': 'form-control'}),
            'order': forms.NumberInput(attrs={'class': 'form-control'}),
        }


# Список фіксованих типів секцій
SECTION_TYPES = ['personal', 'experience', 'education', 'skills', 'other']

SectionFormSet = inlineformset_factory(
    Resume,
    ResumeSection,
    form=ResumeSectionForm,
    extra=0,
    # extra=len(SECTION_TYPES),  # 5 форм для 5 типів секцій
    can_delete=False,  # Видалення секцій не дозволяється
)

# Налаштування фіксованих типів секцій
def get_section_formset(resume=None):
    if resume:
        # Видаляємо зайві секції
        resume.sections.exclude(section_type__in=SECTION_TYPES).delete()
        # Отримуємо існуючі секції, сортовані за order
        existing_sections = resume.sections.filter(section_type__in=SECTION_TYPES).order_by('order')
        section_types_map = {section.section_type: section for section in existing_sections}
        # Створюємо відсутні секції
        used_orders = [section.order for section in existing_sections if section.order is not None]
        next_order = max(used_orders + [-1]) + 1 if used_orders else 0
        for section_type in SECTION_TYPES:
            if section_type not in section_types_map:
                order = next_order if next_order < 5 else SECTION_TYPES.index(section_type)
                ResumeSection.objects.create(
                    resume=resume,
                    section_type=section_type,
                    content='',
                    order=order
                )
                next_order += 1
        # Ініціалізуємо formset із п’ятьма формами, відсортованими за order
        formset = SectionFormSet(
            instance=resume,
            queryset=resume.sections.filter(section_type__in=SECTION_TYPES).order_by('order')
        )
        # Переконуємося, що є рівно 5 форм
        if len(formset.forms) < len(SECTION_TYPES):
            extra_forms_needed = len(SECTION_TYPES) - len(formset.forms)
            formset.extra = extra_forms_needed
            formset.forms.extend([formset.empty_form for _ in range(extra_forms_needed)])
        # Ініціалізуємо section_type і order для кожної форми
        for i, form in enumerate(formset.forms[:len(SECTION_TYPES)]):
            if form.instance.pk:
                form.initial['section_type'] = form.instance.section_type
                form.initial['order'] = form.instance.order
            else:
                form.initial['section_type'] = SECTION_TYPES[i]
                form.initial['order'] = i
            form.fields['section_type'].required = True
    else:
        # Для нових резюме створюємо порожній formset із п’ятьма формами
        formset = SectionFormSet(instance=Resume())
        extra_forms_needed = len(SECTION_TYPES) - len(formset.forms)
        if extra_forms_needed > 0:
            formset.extra = extra_forms_needed
            formset.forms.extend([formset.empty_form for _ in range(extra_forms_needed)])
        for i, form in enumerate(formset.forms[:len(SECTION_TYPES)]):
            form.initial['section_type'] = SECTION_TYPES[i]
            form.initial['order'] = i
            form.fields['section_type'].required = True
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