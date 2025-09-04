from django.views.generic import TemplateView, FormView, CreateView, UpdateView, DeleteView, ListView, DetailView
from django.contrib.auth.views import LoginView, LogoutView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.models import User, Group
from django.urls import reverse_lazy
from django.shortcuts import get_object_or_404, redirect
from django.http import HttpResponse
from django.contrib import messages
from django.db.models import Q
from .forms import RegistrationForm, ResumeForm, SectionFormSet, get_section_formset
from .models import Resume, ResumeTemplate, ResumeSection, Announcement, Profile
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from docx import Document
import io
from django.contrib.auth import login
from django.template import engines


# В'ю для домашньої сторінки
class HomeView(TemplateView):
    template_name = 'home.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['templates'] = ResumeTemplate.objects.all()[:3]  # Популярні шаблони
        context['announcements'] = Announcement.objects.filter(is_active=True).order_by('-created_at')[:5]
        return context


# В'ю для реєстрації нового користувача
class RegisterView(FormView):
    template_name = 'register.html'
    form_class = RegistrationForm
    success_url = reverse_lazy('home')

    def form_valid(self, form):
        user = form.save()
        group = Group.objects.get_or_create(name='users')[0]
        user.groups.add(group)
        login(self.request, user)
        messages.success(self.request, "Реєстрація успішна!")
        return super().form_valid(form)


# В'ю для логіну користувача
class CustomLoginView(LoginView):
    template_name = 'login.html'
    redirect_authenticated_user = True

    def get_success_url(self):
        messages.success(self.request, "Вхід успішний!")
        return reverse_lazy('home')


# В'ю для оновлення профілю користувача
class ProfileView(LoginRequiredMixin, UpdateView):
    model = Profile
    fields = ['bio']
    template_name = 'profile.html'
    success_url = reverse_lazy('profile')

    def get_object(self):
        profile, created = Profile.objects.get_or_create(user=self.request.user)
        return profile

    def form_valid(self, form):
        messages.success(self.request, "Профіль оновлено!")
        return super().form_valid(form)


# В'ю для списку всіх резюме користувача
class ResumeListView(LoginRequiredMixin, ListView):
    model = Resume
    template_name = 'resume_list.html'
    context_object_name = 'resumes'

    def get_queryset(self):
        return Resume.objects.filter(user=self.request.user).order_by('-updated_at')


# В'ю для створення нового резюме користувача
class ResumeCreateView(LoginRequiredMixin, CreateView):
    model = Resume
    form_class = ResumeForm
    template_name = 'resume_form.html'
    success_url = reverse_lazy('resumes')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.POST:
            context['section_formset'] = SectionFormSet(self.request.POST, self.request.FILES, instance=self.object)
        else:
            context['section_formset'] = get_section_formset()
        return context

    def form_valid(self, form):
        form.instance.user = self.request.user
        self.object = form.save()
        section_formset = SectionFormSet(self.request.POST, self.request.FILES, instance=self.object)
        if section_formset.is_valid():
            section_formset.save()
            messages.success(self.request, "Резюме створено!")
            return super().form_valid(form)
        else:
            messages.error(self.request, "Помилка при збереженні секцій: {}".format(section_formset.errors))
            return self.form_invalid(form)


# В'ю для оновлення існуючого резюме користувача
class ResumeUpdateView(LoginRequiredMixin, UpdateView):
    model = Resume
    form_class = ResumeForm
    template_name = 'resume_form.html'
    success_url = reverse_lazy('resumes')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.POST:
            context['section_formset'] = SectionFormSet(self.request.POST, self.request.FILES, instance=self.object)
        else:
            context['section_formset'] = get_section_formset(resume=self.object)
        return context

    def form_valid(self, form):
        self.object = form.save()
        section_formset = SectionFormSet(self.request.POST, self.request.FILES, instance=self.object)
        if section_formset.is_valid():
            # Перевіряємо унікальність order
            orders = [form.cleaned_data.get('order') for form in section_formset if form.cleaned_data.get('order') is not None]
            if len(orders) != len(set(orders)):
                messages.error(self.request, "Порядок секцій має бути унікальним.")
                return self.form_invalid(form)
            section_formset.save()
            # Дебаг: виводимо order після збереження
            print(f"Saved sections for resume {self.object.id}:")
            for section in self.object.sections.all():
                print(f"Section {section.section_type}: order={section.order}")
            messages.success(self.request, "Резюме оновлено!")
            return super().form_valid(form)
        else:
            messages.error(self.request, "Помилка при збереженні секцій: {}".format(section_formset.errors))
            return self.form_invalid(form)


# В'ю для видалення існуючого резюме користувача
class ResumeDeleteView(LoginRequiredMixin, DeleteView):
    model = Resume
    template_name = 'resume_confirm_delete.html'
    success_url = reverse_lazy('resumes')

    def get_queryset(self):
        return Resume.objects.filter(user=self.request.user)

    def form_valid(self, form):
        messages.success(self.request, "Резюме видалено!")
        return super().form_valid(form)


# В'ю для клонування існуючого резюме користувача
class ResumeCloneView(LoginRequiredMixin, DetailView):
    model = Resume
    template_name = 'resume_list.html'  # Не потрібна окрема сторінка

    def get(self, request, *args, **kwargs):
        resume = self.get_object()
        if resume.user != self.request.user:
            messages.error(self.request, "Доступ заборонено!")
            return redirect('resumes')
        new_resume = Resume.objects.create(
            user=resume.user,
            title=f"Copy of {resume.title}",
            template=resume.template,
            photo=resume.photo
        )
        for section in resume.sections.all():
            ResumeSection.objects.create(
                resume=new_resume,
                section_type=section.section_type,
                content=section.content,
                order=section.order
            )
        messages.success(self.request, "Резюме склоновано!")
        return redirect('resumes')


# В'ю для прев'ю конкретного резюме
class ResumePreviewView(LoginRequiredMixin, DetailView):
    model = Resume
    template_name = 'resume_preview.html'
    context_object_name = 'resume'

    def get_queryset(self):
        return Resume.objects.filter(user=self.request.user)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.object.template:
            template_engine = engines['django']
            template = template_engine.from_string(self.object.template.html_template)
            context['rendered_template'] = template.render({
                'resume': self.object,
                'sections': self.object.sections.all(),
            })
        return context


# В'ю для списку шаблонів резюме
class TemplateListView(ListView):
    model = ResumeTemplate
    template_name = 'template_list.html'
    context_object_name = 'templates'


# В'ю для списку оголошень
class AnnouncementListView(ListView):
    model = Announcement
    template_name = 'announcement_list.html'
    context_object_name = 'announcements'

    def get_queryset(self):
        return Announcement.objects.filter(is_active=True).order_by('-created_at')


# В'ю для створення нового оголошення
class AnnouncementCreateView(LoginRequiredMixin, CreateView):
    model = Announcement
    fields = ['title', 'content', 'is_active']
    template_name = 'announcement_form.html'
    success_url = reverse_lazy('announcements')

    def get_queryset(self):
        return Announcement.objects.filter(created_by=self.request.user)

    def form_valid(self, form):
        if not self.request.user.groups.filter(name='admins').exists():
            messages.error(self.request, "Тільки адміністратори можуть створювати оголошення!")
            return redirect('announcements')
        form.instance.created_by = self.request.user
        messages.success(self.request, "Оголошення створено!")
        return super().form_valid(form)


# В'ю для редагування існуючого оголошення
class AnnouncementUpdateView(LoginRequiredMixin, UpdateView):
    model = Announcement
    fields = ['title', 'content', 'is_active']
    template_name = 'announcement_form.html'
    success_url = reverse_lazy('announcements')

    def get_queryset(self):
        return Announcement.objects.filter(created_by=self.request.user)

    def form_valid(self, form):
        if not self.request.user.groups.filter(name='admins').exists():
            messages.error(self.request, "Тільки адміністратори можуть редагувати оголошення!")
            return redirect('announcements')
        messages.success(self.request, "Оголошення оновлено!")
        return super().form_valid(form)


# В'ю для видалення існуючого оголошення
class AnnouncementDeleteView(LoginRequiredMixin, DeleteView):
    model = Announcement
    template_name = 'announcement_confirm_delete.html'
    success_url = reverse_lazy('announcements')

    def get_queryset(self):
        return Announcement.objects.filter(created_by=self.request.user)

    def form_valid(self, form):
        if not self.request.user.groups.filter(name='admins').exists():
            messages.error(self.request, "Тільки адміністратори можуть видаляти оголошення!")
            return redirect('announcements')
        messages.success(self.request, "Оголошення видалено!")
        return super().form_valid(form)


# В'ю для експорту конкретного резюме в pdf-форматі
def export_pdf(request, pk):
    resume = get_object_or_404(Resume, pk=pk, user=request.user)
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="{resume.title}.pdf"'
    p = canvas.Canvas(response, pagesize=A4)
    y = 800
    p.drawString(100, y, resume.title)
    y -= 30
    for section in resume.sections.all():
        p.drawString(100, y, f"{section.get_section_type_display()}:")
        y -= 20
        p.drawString(120, y, section.content[:100])  # Обмеження для прикладу
        y -= 30
    if resume.photo:
        p.drawImage(resume.photo.path, 100, y - 100, width=100, height=100)
    p.showPage()
    p.save()
    return response


# В'ю для експорту конкретного резюме в docx-форматі
def export_docx(request, pk):
    resume = get_object_or_404(Resume, pk=pk, user=request.user)
    doc = Document()
    doc.add_heading(resume.title, 0)
    for section in resume.sections.all():
        doc.add_heading(section.get_section_type_display(), level=1)
        doc.add_paragraph(section.content)
    response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.wordprocessingml.document')
    response['Content-Disposition'] = f'attachment; filename="{resume.title}.docx"'
    doc_buffer = io.BytesIO()
    doc.save(doc_buffer)
    response.write(doc_buffer.getvalue())
    return response