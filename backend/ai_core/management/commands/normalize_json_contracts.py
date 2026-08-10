"""Normalize persisted structured JSON data to the canonical English contract."""

from django.core.management.base import BaseCommand

from ai_core.json_contracts import canonicalize_json
from assessments.models import Assessment, AssessmentResult
from jobs.models import JobPostingNormalization
from matching.models import MatchResult
from passports.models import StudyTrack, TalentPassport
from resumes.models import ResumeNormalization


class Command(BaseCommand):
    """Rewrite existing JSON fields using canonical English keys and enum values."""

    help = "Normalize persisted JSON contracts to canonical English keys and values."

    MODEL_FIELDS = (
        (ResumeNormalization, ("structured_data",)),
        (JobPostingNormalization, ("structured_data",)),
        (MatchResult, ("structured_data",)),
        (Assessment, ("structured_data",)),
        (AssessmentResult, ("answers", "study_track", "structured_data")),
        (
            TalentPassport,
            ("professional_profile", "career_recommendations", "dashboard_summary"),
        ),
        (StudyTrack, ("items",)),
    )

    def handle(self, *args, **options):
        updated_rows = 0
        for model, fields in self.MODEL_FIELDS:
            for instance in model.objects.all().iterator():
                changed_fields = []
                for field in fields:
                    current = getattr(instance, field)
                    if current is None:
                        continue
                    normalized = canonicalize_json(current)
                    if normalized != current:
                        setattr(instance, field, normalized)
                        changed_fields.append(field)
                if changed_fields:
                    instance.save(update_fields=changed_fields)
                    updated_rows += 1

        self.stdout.write(self.style.SUCCESS(f"Normalized {updated_rows} database rows."))
