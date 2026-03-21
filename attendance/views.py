from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from django.db.models import Count, Sum, Avg
from datetime import date, timedelta
import calendar

from .models import AttendanceRecord, LeaveRequest, WorkSchedule, AttendanceSummary


@login_required
def attendance_dashboard(request):
    """Tableau de bord présence de l'employé."""
    today = date.today()
    current_month = today.month
    current_year = today.year

    # Présences du mois en cours
    records = AttendanceRecord.objects.filter(
        user=request.user,
        date__year=current_year,
        date__month=current_month,
    ).order_by('-date')

    # Stats du mois
    present_count = records.filter(status='present').count()
    late_count = records.filter(status='late').count()
    absent_count = records.filter(status='absent').count()
    leave_count = records.filter(status__in=['on_leave', 'sick']).count()
    total_hours = records.aggregate(h=Sum('working_hours'))['h'] or 0.0
    overtime = records.aggregate(o=Sum('overtime_hours'))['o'] or 0.0

    working_days = _count_working_days(current_year, current_month)
    attendance_rate = round((present_count + late_count) / max(working_days, 1) * 100, 1)

    # Record du jour
    today_record = AttendanceRecord.objects.filter(user=request.user, date=today).first()

    # Congés en attente
    pending_leaves = LeaveRequest.objects.filter(user=request.user, status='pending').count()

    # 5 derniers jours
    recent_records = records[:10]

    context = {
        'today': today,
        'today_record': today_record,
        'records': recent_records,
        'present_count': present_count,
        'late_count': late_count,
        'absent_count': absent_count,
        'leave_count': leave_count,
        'total_hours': round(total_hours, 1),
        'overtime': round(overtime, 1),
        'attendance_rate': attendance_rate,
        'working_days': working_days,
        'pending_leaves': pending_leaves,
        'current_month_name': calendar.month_name[current_month],
        'current_year': current_year,
    }
    return render(request, 'attendance/dashboard.html', context)


@login_required
def checkin(request):
    """Pointage d'arrivée."""
    today = date.today()
    record, created = AttendanceRecord.objects.get_or_create(
        user=request.user, date=today,
        defaults={'status': 'present'}
    )
    now = timezone.localtime().time()
    if not record.check_in:
        record.check_in = now
        # Déterminer si en retard (après 8h30)
        from datetime import time
        if now > time(8, 30):
            record.status = 'late'
            messages.warning(request, f'⚠️ Pointage enregistré à {now.strftime("%H:%M")} — En retard.')
        else:
            record.status = 'present'
            messages.success(request, f'✅ Bonjour ! Pointage d\'arrivée à {now.strftime("%H:%M")}.')
        record.save()
    else:
        messages.info(request, 'Vous avez déjà pointé votre arrivée aujourd\'hui.')
    return redirect('attendance:dashboard')


@login_required
def checkout(request):
    """Pointage de départ."""
    today = date.today()
    record = AttendanceRecord.objects.filter(user=request.user, date=today).first()
    if record and record.check_in and not record.check_out:
        now = timezone.localtime().time()
        record.check_out = now
        record.save()
        messages.success(request, f'👋 Bonne soirée ! Départ enregistré à {now.strftime("%H:%M")} — {record.duration_display} travaillées.')
    elif not record or not record.check_in:
        messages.error(request, "Vous n'avez pas encore pointé votre arrivée.")
    else:
        messages.info(request, 'Départ déjà enregistré.')
    return redirect('attendance:dashboard')


@login_required
def leave_request_create(request):
    """Créer une demande de congé."""
    if request.method == 'POST':
        leave_type = request.POST.get('leave_type')
        start_date = request.POST.get('start_date')
        end_date = request.POST.get('end_date')
        reason = request.POST.get('reason', '').strip()

        if not all([leave_type, start_date, end_date, reason]):
            messages.error(request, 'Tous les champs sont obligatoires.')
        else:
            from datetime import datetime
            start = datetime.strptime(start_date, '%Y-%m-%d').date()
            end = datetime.strptime(end_date, '%Y-%m-%d').date()
            if end < start:
                messages.error(request, 'La date de fin doit être après la date de début.')
            else:
                LeaveRequest.objects.create(
                    user=request.user,
                    leave_type=leave_type,
                    start_date=start,
                    end_date=end,
                    reason=reason,
                )
                messages.success(request, '📋 Demande de congé soumise avec succès. En attente de validation RH.')
                return redirect('attendance:my_leaves')

    context = {'leave_types': LeaveRequest.TYPE_CHOICES}
    return render(request, 'attendance/leave_request.html', context)


@login_required
def my_leaves(request):
    """Historique des demandes de congé."""
    leaves = LeaveRequest.objects.filter(user=request.user).order_by('-created_at')
    context = {'leaves': leaves}
    return render(request, 'attendance/my_leaves.html', context)


@login_required
def attendance_history(request):
    """Historique complet des présences avec filtres."""
    month = int(request.GET.get('month', date.today().month))
    year = int(request.GET.get('year', date.today().year))

    records = AttendanceRecord.objects.filter(
        user=request.user,
        date__year=year,
        date__month=month,
    ).order_by('date')

    # Résumé du mois
    summary = {
        'present': records.filter(status='present').count(),
        'late': records.filter(status='late').count(),
        'absent': records.filter(status='absent').count(),
        'leave': records.filter(status__in=['on_leave', 'sick', 'holiday']).count(),
        'remote': records.filter(status='remote').count(),
        'total_hours': round(records.aggregate(h=Sum('working_hours'))['h'] or 0, 1),
        'overtime': round(records.aggregate(o=Sum('overtime_hours'))['o'] or 0, 1),
    }

    months = [(i, calendar.month_name[i]) for i in range(1, 13)]
    years = list(range(date.today().year - 2, date.today().year + 1))

    context = {
        'records': records,
        'summary': summary,
        'selected_month': month,
        'selected_year': year,
        'months': months,
        'years': years,
        'month_name': calendar.month_name[month],
    }
    return render(request, 'attendance/history.html', context)


def _count_working_days(year, month):
    """Compte les jours ouvrables d'un mois."""
    _, num_days = calendar.monthrange(year, month)
    count = 0
    for day in range(1, num_days + 1):
        d = date(year, month, day)
        if d.weekday() < 5:  # Lundi-Vendredi
            count += 1
    return count
