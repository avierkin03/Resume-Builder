from django.core.management.base import BaseCommand
from core.models import Resume, ResumeSection

class Command(BaseCommand):
    help = 'Migrate existing resumes to have exactly five fixed sections'

    def handle(self, *args, **kwargs):
        SECTION_TYPES = ['personal', 'experience', 'education', 'skills', 'other']
        for resume in Resume.objects.all():
            # Видаляємо зайві секції
            resume.sections.exclude(section_type__in=SECTION_TYPES).delete()
            # Отримуємо існуючі секції
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
            # Видаляємо зайві секції, якщо їх більше 5
            if resume.sections.count() > len(SECTION_TYPES):
                resume.sections.filter(section_type__in=SECTION_TYPES).order_by('id')[len(SECTION_TYPES):].delete()
            self.stdout.write(self.style.SUCCESS(f'Migrated resume {resume.id}: {resume.title}'))