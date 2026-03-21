"""
Tâches Celery pour le module de formation AMN.
Récapitulatif quotidien envoyé par email à chaque employé.
"""
from celery import shared_task
from django.core.mail import send_mail
from django.conf import settings
from django.utils import timezone
from django.template.loader import render_to_string
from datetime import date, timedelta
import logging

logger = logging.getLogger(__name__)


@shared_task(name='learning.send_daily_recap')
def send_daily_learning_recap():
    """
    Envoie un récapitulatif quotidien de formation à chaque employé actif.
    À planifier chaque jour à 18h00 (Africa/Douala).
    """
    from django.contrib.auth import get_user_model
    from learning.models import Enrollment, LessonProgress, Certificate
    from attendance.models import AttendanceRecord

    User = get_user_model()
    today = date.today()
    yesterday = today - timedelta(days=1)

    active_users = User.objects.filter(is_active=True, email__isnull=False).exclude(email='')

    sent_count = 0
    error_count = 0

    for user in active_users:
        try:
            # ── Données formations ──
            enrollments = Enrollment.objects.filter(user=user).select_related('module')
            in_progress = enrollments.filter(status='in_progress')
            completed_today = enrollments.filter(
                status='completed',
                completed_at__date=today
            )

            lessons_today = LessonProgress.objects.filter(
                user=user,
                completed=True,
                completed_at__date=today
            ).select_related('lesson__course__module')

            certs = Certificate.objects.filter(user=user, issued_at__date=today)

            # ── Données présence ──
            attendance_today = AttendanceRecord.objects.filter(user=user, date=today).first()
            attendance_week = AttendanceRecord.objects.filter(
                user=user,
                date__gte=today - timedelta(days=today.weekday()),
                date__lte=today
            )

            # Pas d'activité aujourd'hui → email allégé
            has_activity = lessons_today.exists() or attendance_today or completed_today.exists()

            context = {
                'user': user,
                'today': today,
                'lessons_today': lessons_today,
                'completed_today': completed_today,
                'in_progress': in_progress[:5],
                'certificates_today': certs,
                'attendance_today': attendance_today,
                'week_records': attendance_week,
                'total_enrollments': enrollments.count(),
                'total_completed': enrollments.filter(status='completed').count(),
                'total_certificates': Certificate.objects.filter(user=user).count(),
                'has_activity': has_activity,
            }

            subject = _build_subject(user, today, has_activity, lessons_today.count())
            html_body = render_to_string('learning/emails/daily_recap.html', context)
            text_body = render_to_string('learning/emails/daily_recap.txt', context)

            send_mail(
                subject=subject,
                message=text_body,
                from_email=f'AMN Formation <{settings.DEFAULT_FROM_EMAIL}>',
                recipient_list=[user.email],
                html_message=html_body,
                fail_silently=False,
            )
            sent_count += 1
            logger.info(f'Récap envoyé à {user.email}')

        except Exception as e:
            error_count += 1
            logger.error(f'Erreur récap pour {user}: {e}')

    logger.info(f'Récaps quotidiens : {sent_count} envoyés, {error_count} erreurs.')
    return {'sent': sent_count, 'errors': error_count}


def _build_subject(user, today, has_activity, lessons_count):
    """Construit l'objet de l'email selon l'activité."""
    name = user.first_name or user.username
    day_str = today.strftime('%d/%m/%Y')
    if has_activity and lessons_count > 0:
        return f'🎓 {name} — Récap formation AMN du {day_str} ({lessons_count} leçon{"s" if lessons_count > 1 else ""} complétée{"s" if lessons_count > 1 else ""})'
    elif has_activity:
        return f'📋 {name} — Récap quotidien AMN du {day_str}'
    else:
        return f'💡 {name} — Rappel formation AMN — Continuez votre progression !'


@shared_task(name='learning.send_weekly_report')
def send_weekly_report():
    """
    Rapport hebdomadaire envoyé chaque lundi matin.
    Résumé de la semaine précédente.
    """
    from django.contrib.auth import get_user_model
    from learning.models import Enrollment, LessonProgress
    from attendance.models import AttendanceRecord

    User = get_user_model()
    today = date.today()
    week_start = today - timedelta(days=7)

    active_users = User.objects.filter(is_active=True, email__isnull=False).exclude(email='')
    sent_count = 0

    for user in active_users:
        try:
            lessons_week = LessonProgress.objects.filter(
                user=user,
                completed=True,
                completed_at__date__gte=week_start,
                completed_at__date__lte=today
            ).count()

            attendance_week = AttendanceRecord.objects.filter(
                user=user,
                date__gte=week_start,
                date__lte=today
            )
            present_days = attendance_week.filter(status__in=['present', 'late', 'remote']).count()

            if lessons_week == 0 and present_days == 0:
                continue

            context = {
                'user': user,
                'week_start': week_start,
                'week_end': today,
                'lessons_week': lessons_week,
                'present_days': present_days,
                'attendance_records': attendance_week,
            }

            html_body = render_to_string('learning/emails/weekly_report.html', context)
            text_body = f"""
Bonjour {user.first_name or user.username},

Votre résumé de la semaine AMN ({week_start.strftime('%d/%m')} - {today.strftime('%d/%m/%Y')}):

Formation:
- Leçons complétées : {lessons_week}

Présence:
- Jours présents : {present_days}/5

Continuez votre progression !
L'équipe AMN Formation
            """.strip()

            send_mail(
                subject=f'📊 Rapport hebdomadaire AMN — semaine du {week_start.strftime("%d/%m/%Y")}',
                message=text_body,
                from_email=f'AMN Formation <{settings.DEFAULT_FROM_EMAIL}>',
                recipient_list=[user.email],
                html_message=html_body,
                fail_silently=False,
            )
            sent_count += 1
        except Exception as e:
            logger.error(f'Erreur rapport hebdo pour {user}: {e}')

    return {'sent': sent_count}


@shared_task(name='learning.remind_incomplete_enrollments')
def remind_incomplete_enrollments():
    """
    Rappel pour les employés qui n'ont pas progressé depuis 7 jours.
    """
    from learning.models import Enrollment

    stale_date = timezone.now() - timedelta(days=7)
    stale = Enrollment.objects.filter(
        status='in_progress',
        last_activity__lte=stale_date,
        user__email__isnull=False,
    ).select_related('user', 'module').exclude(user__email='')

    sent_count = 0
    for enrollment in stale:
        try:
            user = enrollment.user
            send_mail(
                subject=f'⏰ {user.first_name or user.username}, continuez votre formation AMN !',
                message=f"""
Bonjour {user.first_name or user.username},

Vous n'avez pas progressé dans la formation "{enrollment.module.title}" depuis plus de 7 jours.

Vous êtes à {enrollment.progress_percent:.0f}% — continuez pour obtenir votre certificat !

Connectez-vous dès maintenant.

L'équipe AMN Formation
                """.strip(),
                from_email=f'AMN Formation <{settings.DEFAULT_FROM_EMAIL}>',
                recipient_list=[user.email],
                fail_silently=False,
            )
            sent_count += 1
        except Exception as e:
            logger.error(f'Erreur rappel pour {enrollment.user}: {e}')

    return {'reminders_sent': sent_count}
