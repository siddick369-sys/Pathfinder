from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from django.db.models import Count, Avg

from .models import (
    TrainingModule, Course, Lesson, Enrollment, LessonProgress,
    Quiz, QuizAttempt, QuizQuestion, QuizChoice, Certificate, Department
)


@login_required
def module_list(request):
    """Liste de tous les modules de formation AMN."""
    modules = TrainingModule.objects.filter(status='published').select_related('department')
    departments = Department.objects.all()

    dept_filter = request.GET.get('dept')
    level_filter = request.GET.get('level')
    if dept_filter:
        modules = modules.filter(department__code=dept_filter)
    if level_filter:
        modules = modules.filter(level=level_filter)

    # Enrichir avec la progression de l'utilisateur
    user_enrollments = {
        e.module_id: e for e in Enrollment.objects.filter(user=request.user)
    }
    for mod in modules:
        mod.user_enrollment = user_enrollments.get(mod.id)

    stats = {
        'total_modules': modules.count(),
        'enrolled': Enrollment.objects.filter(user=request.user).count(),
        'completed': Enrollment.objects.filter(user=request.user, status='completed').count(),
        'certificates': Certificate.objects.filter(user=request.user).count(),
    }

    context = {
        'modules': modules,
        'departments': departments,
        'stats': stats,
        'dept_filter': dept_filter,
        'level_filter': level_filter,
    }
    return render(request, 'learning/module_list.html', context)


@login_required
def module_detail(request, slug):
    """Détail d'un module de formation."""
    module = get_object_or_404(TrainingModule, slug=slug, status='published')
    courses = module.courses.filter(is_published=True).prefetch_related('lessons')

    enrollment = Enrollment.objects.filter(user=request.user, module=module).first()

    # Progression par leçon
    lesson_ids = Lesson.objects.filter(course__module=module).values_list('id', flat=True)
    completed_lessons = set(
        LessonProgress.objects.filter(
            user=request.user, lesson_id__in=lesson_ids, completed=True
        ).values_list('lesson_id', flat=True)
    )

    for course in courses:
        for lesson in course.lessons.all():
            lesson.is_completed = lesson.id in completed_lessons

    context = {
        'module': module,
        'courses': courses,
        'enrollment': enrollment,
        'completed_lessons': completed_lessons,
        'total_lessons': len(lesson_ids),
        'completed_count': len(completed_lessons),
    }
    return render(request, 'learning/module_detail.html', context)


@login_required
def lesson_view(request, module_slug, lesson_id):
    """Vue d'une leçon."""
    lesson = get_object_or_404(Lesson, id=lesson_id, course__module__slug=module_slug)
    module = lesson.course.module

    # S'assurer que l'utilisateur est inscrit
    enrollment, _ = Enrollment.objects.get_or_create(
        user=request.user, module=module,
        defaults={'status': 'in_progress', 'last_activity': timezone.now()}
    )

    progress, _ = LessonProgress.objects.get_or_create(user=request.user, lesson=lesson)

    if request.method == 'POST':
        action = request.POST.get('action')
        if action == 'complete':
            if not progress.completed:
                progress.mark_complete()
                messages.success(request, f'✅ Leçon "{lesson.title}" marquée comme terminée !')
            return redirect('learning:lesson', module_slug=module_slug, lesson_id=lesson_id)

    # Leçons adjacentes
    all_lessons = list(Lesson.objects.filter(course__module=module).order_by('course__order', 'order'))
    current_idx = next((i for i, l in enumerate(all_lessons) if l.id == lesson.id), 0)
    prev_lesson = all_lessons[current_idx - 1] if current_idx > 0 else None
    next_lesson = all_lessons[current_idx + 1] if current_idx < len(all_lessons) - 1 else None

    context = {
        'lesson': lesson,
        'module': module,
        'progress': progress,
        'enrollment': enrollment,
        'prev_lesson': prev_lesson,
        'next_lesson': next_lesson,
        'has_quiz': hasattr(lesson, 'quiz'),
    }
    return render(request, 'learning/lesson_view.html', context)


@login_required
def enroll_module(request, slug):
    """S'inscrire à un module."""
    module = get_object_or_404(TrainingModule, slug=slug)
    enrollment, created = Enrollment.objects.get_or_create(
        user=request.user, module=module,
        defaults={'status': 'enrolled'}
    )
    if created:
        messages.success(request, f'🎓 Inscription au module "{module.title}" confirmée !')
    else:
        messages.info(request, 'Vous êtes déjà inscrit à ce module.')
    return redirect('learning:module_detail', slug=slug)


@login_required
def my_learning(request):
    """Tableau de bord personnel de formation."""
    enrollments = Enrollment.objects.filter(
        user=request.user
    ).select_related('module', 'module__department').order_by('-last_activity')

    certificates = Certificate.objects.filter(user=request.user).select_related('module')

    in_progress = enrollments.filter(status='in_progress')
    completed = enrollments.filter(status='completed')
    enrolled = enrollments.filter(status='enrolled')

    context = {
        'enrollments': enrollments,
        'in_progress': in_progress,
        'completed': completed,
        'enrolled': enrolled,
        'certificates': certificates,
        'total_xp': sum(
            e.module.courses.aggregate(total=Count('lessons'))['total'] or 0
            for e in completed
        ),
    }
    return render(request, 'learning/my_learning.html', context)


@login_required
def certificate_view(request, cert_number):
    """Affichage d'un certificat."""
    certificate = get_object_or_404(Certificate, certificate_number=cert_number, user=request.user)
    return render(request, 'learning/certificate.html', {'certificate': certificate})
