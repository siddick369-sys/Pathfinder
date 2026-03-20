"""
Management command to seed AMN Employee Hub with sample data.
Usage: python manage.py seed_amn
"""
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.utils.text import slugify

User = get_user_model()


class Command(BaseCommand):
    help = 'Seed AMN Employee Hub with sample training modules, courses and lessons'

    def add_arguments(self, parser):
        parser.add_argument(
            '--clear', action='store_true',
            help='Clear existing learning data before seeding'
        )

    def handle(self, *args, **options):
        from learning.models import Department, TrainingModule, Course, Lesson, Quiz, QuizQuestion, QuizChoice

        if options['clear']:
            self.stdout.write('Clearing existing data…')
            QuizChoice.objects.all().delete()
            QuizQuestion.objects.all().delete()
            Quiz.objects.all().delete()
            Lesson.objects.all().delete()
            Course.objects.all().delete()
            TrainingModule.objects.all().delete()
            Department.objects.all().delete()
            self.stdout.write(self.style.WARNING('Cleared.'))

        # ── Departments ────────────────────────────────────────────────────────
        departments_data = [
            {'name': 'Réseau Mobile', 'code': 'RES', 'icon': '📡', 'head_name': 'M. Kamga Paul'},
            {'name': 'Service Client', 'code': 'SVC', 'icon': '🎧', 'head_name': 'Mme Ngono Claire'},
            {'name': 'Finance & Comptabilité', 'code': 'FIN', 'icon': '💰', 'head_name': 'M. Essomba Jean'},
            {'name': 'Ressources Humaines', 'code': 'RH', 'icon': '👥', 'head_name': 'Mme Biya Rose'},
            {'name': 'IT & Systèmes', 'code': 'IT', 'icon': '💻', 'head_name': 'M. Ndi Martin'},
        ]
        departments = {}
        for d in departments_data:
            obj, created = Department.objects.get_or_create(
                code=d['code'],
                defaults=d
            )
            departments[d['code']] = obj
            if created:
                self.stdout.write(f'  Département créé: {obj}')

        # ── Training Modules ───────────────────────────────────────────────────
        modules_data = [
            {
                'number': 1, 'title': 'Accueil & Intégration AMN',
                'slug': 'module-1-accueil-integration-amn',
                'description': 'Découvrez AMN, ses valeurs, sa culture et son organisation. '
                               'Ce module est obligatoire pour tous les nouveaux employés.',
                'department': departments['RH'],
                'level': 'debutant', 'duration_hours': 4, 'is_mandatory': True, 'order': 1,
                'objectives': [
                    'Connaître l\'histoire et les valeurs d\'AMN',
                    'Comprendre l\'organigramme et les départements',
                    'Maîtriser les outils de travail internes',
                    'Respecter la charte éthique et de confidentialité',
                ],
            },
            {
                'number': 2, 'title': 'Réseau Mobile & Technologies',
                'slug': 'module-2-reseau-mobile-technologies',
                'description': 'Comprenez l\'architecture des réseaux mobiles 4G/5G et les '
                               'services proposés par AMN à ses clients.',
                'department': departments['RES'],
                'level': 'intermediaire', 'duration_hours': 8, 'is_mandatory': False, 'order': 2,
                'objectives': [
                    'Comprendre les technologies 4G et 5G',
                    'Identifier les équipements du réseau AMN',
                    'Expliquer les services de données mobiles',
                    'Diagnostiquer les pannes réseau courantes',
                ],
            },
            {
                'number': 3, 'title': 'Excellence du Service Client',
                'slug': 'module-3-excellence-service-client',
                'description': 'Maîtrisez les techniques de communication et de gestion des '
                               'réclamations pour offrir une expérience client exceptionnelle.',
                'department': departments['SVC'],
                'level': 'debutant', 'duration_hours': 6, 'is_mandatory': True, 'order': 3,
                'objectives': [
                    'Appliquer les techniques de communication bienveillante',
                    'Gérer les réclamations et clients difficiles',
                    'Utiliser le CRM AMN efficacement',
                    'Atteindre les KPIs de satisfaction client',
                ],
            },
            {
                'number': 4, 'title': 'Sécurité & Conformité',
                'slug': 'module-4-securite-conformite',
                'description': 'Comprenez les obligations légales, la sécurité des données et '
                               'les procédures de conformité au sein d\'AMN.',
                'department': departments['IT'],
                'level': 'intermediaire', 'duration_hours': 5, 'is_mandatory': True, 'order': 4,
                'objectives': [
                    'Respecter la politique de sécurité informatique',
                    'Protéger les données personnelles (RGPD local)',
                    'Signaler les incidents de sécurité',
                    'Gérer les accès et mots de passe',
                ],
            },
        ]
        modules = {}
        for m in modules_data:
            slug = m['slug']
            obj, created = TrainingModule.objects.get_or_create(
                slug=slug,
                defaults=m
            )
            modules[slug] = obj
            if created:
                self.stdout.write(f'  Module créé: {obj}')

        # ── Courses & Lessons ──────────────────────────────────────────────────
        courses_data = [
            # Module 1
            {
                'module_slug': 'module-1-accueil-integration-amn',
                'title': 'Bienvenue chez AMN',
                'description': 'Histoire, vision et valeurs d\'AMN au Cameroun.',
                'order': 1, 'duration_minutes': 45, 'xp_reward': 100,
                'instructor_name': 'DRH AMN', 'instructor_title': 'Direction des Ressources Humaines',
                'lessons': [
                    {
                        'title': 'L\'histoire d\'AMN', 'lesson_type': 'article', 'order': 1,
                        'duration_minutes': 15, 'xp_reward': 20, 'is_free_preview': True,
                        'content': (
                            '## L\'histoire d\'AMN\n\n'
                            'AMN (African Mobile Network) a été fondé en 2005 à Yaoundé. '
                            'Depuis lors, l\'entreprise s\'est développée pour couvrir l\'ensemble '
                            'du territoire camerounais avec plus de 5 000 employés.\n\n'
                            '### Nos valeurs\n'
                            '- **Innovation** : Nous adoptons les dernières technologies\n'
                            '- **Excellence** : Nous visons la qualité dans tout ce que nous faisons\n'
                            '- **Intégrité** : Nous agissons avec honnêteté et transparence\n'
                            '- **Solidarité** : Nous travaillons ensemble pour atteindre nos objectifs\n\n'
                            '### Notre mission\n'
                            'Connecter chaque Camerounais au réseau numérique mondial.'
                        ),
                    },
                    {
                        'title': 'L\'organigramme AMN', 'lesson_type': 'article', 'order': 2,
                        'duration_minutes': 20, 'xp_reward': 20,
                        'content': (
                            '## Organisation d\'AMN\n\n'
                            'AMN est organisé en cinq grandes directions :\n\n'
                            '1. **Direction Générale** — Stratégie et gouvernance\n'
                            '2. **Direction Technique** — Réseau, IT et infrastructure\n'
                            '3. **Direction Commerciale** — Ventes, marketing, service client\n'
                            '4. **Direction Financière** — Finance, comptabilité, audit\n'
                            '5. **Direction RH** — Recrutement, formation, bien-être\n\n'
                            'Chaque direction est divisée en départements spécialisés.'
                        ),
                    },
                    {
                        'title': 'Quiz : Bienvenue chez AMN', 'lesson_type': 'quiz', 'order': 3,
                        'duration_minutes': 10, 'xp_reward': 50,
                        'content': 'Testez vos connaissances sur l\'histoire et les valeurs d\'AMN.',
                        'quiz': {
                            'passing_score': 70, 'time_limit_minutes': 10, 'max_attempts': 3,
                            'questions': [
                                {
                                    'text': 'En quelle année AMN a-t-il été fondé ?',
                                    'explanation': 'AMN a été fondé en 2005 à Yaoundé.',
                                    'order': 1, 'points': 1,
                                    'choices': [
                                        ('2000', False), ('2005', True), ('2010', False), ('2015', False),
                                    ],
                                },
                                {
                                    'text': 'Quelle est la valeur centrale d\'AMN qui désigne le travail en équipe ?',
                                    'explanation': 'La Solidarité représente notre esprit d\'équipe.',
                                    'order': 2, 'points': 1,
                                    'choices': [
                                        ('Innovation', False), ('Excellence', False),
                                        ('Solidarité', True), ('Compétition', False),
                                    ],
                                },
                                {
                                    'text': 'Combien d\'employés compte AMN aujourd\'hui ?',
                                    'explanation': 'AMN emploie plus de 5 000 personnes à travers le Cameroun.',
                                    'order': 3, 'points': 1,
                                    'choices': [
                                        ('500', False), ('1 000', False), ('5 000', True), ('10 000', False),
                                    ],
                                },
                            ],
                        },
                    },
                ],
            },
            # Module 2
            {
                'module_slug': 'module-2-reseau-mobile-technologies',
                'title': 'Fondamentaux des réseaux mobiles',
                'description': 'Introduction aux technologies 4G et 5G utilisées par AMN.',
                'order': 1, 'duration_minutes': 90, 'xp_reward': 150,
                'instructor_name': 'Ing. Tchamba Serge', 'instructor_title': 'Ingénieur Réseau Senior',
                'lessons': [
                    {
                        'title': 'Introduction à la 4G LTE', 'lesson_type': 'article', 'order': 1,
                        'duration_minutes': 30, 'xp_reward': 25, 'is_free_preview': True,
                        'content': (
                            '## La technologie 4G LTE\n\n'
                            'La 4G (Long Term Evolution) est la 4ème génération de réseaux mobiles. '
                            'Elle offre des débits théoriques allant jusqu\'à 150 Mbps en download.\n\n'
                            '### Architecture 4G\n'
                            '- **eNodeB** : Stations de base radio\n'
                            '- **EPC** : Evolved Packet Core (cœur de réseau)\n'
                            '- **MME** : Mobility Management Entity\n'
                            '- **S-GW / P-GW** : Passerelles de données\n\n'
                            '### Fréquences utilisées par AMN\n'
                            '- **700 MHz** : Couverture rurale étendue\n'
                            '- **1800 MHz** : Capacité urbaine\n'
                            '- **2600 MHz** : Très haut débit dans les grandes villes'
                        ),
                    },
                    {
                        'title': 'La 5G : présent et futur', 'lesson_type': 'article', 'order': 2,
                        'duration_minutes': 25, 'xp_reward': 25,
                        'content': (
                            '## La révolution 5G\n\n'
                            'La 5G représente la 5ème génération, offrant des débits jusqu\'à 10 Gbps '
                            'et une latence inférieure à 1 ms.\n\n'
                            '### Cas d\'usage 5G chez AMN\n'
                            '- IoT industriel (smart factories)\n'
                            '- Véhicules connectés\n'
                            '- Télémedecine\n'
                            '- Streaming 4K/8K\n\n'
                            '### Déploiement AMN\n'
                            'AMN déploie la 5G progressivement dans les grandes villes : '
                            'Douala, Yaoundé, Bafoussam d\'ici 2027.'
                        ),
                    },
                ],
            },
            # Module 3
            {
                'module_slug': 'module-3-excellence-service-client',
                'title': 'Techniques de communication client',
                'description': 'Maîtrisez l\'écoute active et la communication bienveillante.',
                'order': 1, 'duration_minutes': 60, 'xp_reward': 120,
                'instructor_name': 'Mme Ateba Solange', 'instructor_title': 'Responsable Qualité Client',
                'lessons': [
                    {
                        'title': 'L\'écoute active', 'lesson_type': 'article', 'order': 1,
                        'duration_minutes': 20, 'xp_reward': 20, 'is_free_preview': True,
                        'content': (
                            '## L\'écoute active\n\n'
                            'L\'écoute active est une technique de communication qui consiste à '
                            'porter une attention totale à l\'interlocuteur.\n\n'
                            '### Les 4 piliers\n'
                            '1. **Attention** : Regarder, ne pas interrompre\n'
                            '2. **Reformulation** : «Si je comprends bien, vous dites que…»\n'
                            '3. **Empathie** : Se mettre à la place du client\n'
                            '4. **Validation** : Confirmer la compréhension avant de répondre\n\n'
                            '### À éviter\n'
                            '- Interrompre le client\n'
                            '- Formuler sa réponse pendant que le client parle\n'
                            '- Minimiser le problème («C\'est pas grave»)'
                        ),
                    },
                    {
                        'title': 'Gestion des réclamations', 'lesson_type': 'article', 'order': 2,
                        'duration_minutes': 25, 'xp_reward': 20,
                        'content': (
                            '## Gérer les réclamations efficacement\n\n'
                            'Une réclamation bien gérée peut transformer un client insatisfait '
                            'en ambassadeur de la marque.\n\n'
                            '### La méthode ERIC\n'
                            '- **E**couter sans interrompre\n'
                            '- **R**econnaître le problème (s\'excuser si nécessaire)\n'
                            '- **I**nvestiguer les causes\n'
                            '- **C**orriger et proposer une solution\n\n'
                            '### Délais de traitement AMN\n'
                            '| Type | Délai maximum |\n'
                            '|------|---------------|\n'
                            '| Facturation | 24h |\n'
                            '| Réseau | 48h |\n'
                            '| Remboursement | 72h |'
                        ),
                    },
                ],
            },
        ]

        for course_data in courses_data:
            module = modules[course_data['module_slug']]
            lessons_data = course_data.pop('lessons')
            course_data.pop('module_slug')

            course, created = Course.objects.get_or_create(
                module=module, title=course_data['title'],
                defaults={**course_data, 'module': module}
            )
            if created:
                self.stdout.write(f'  Cours créé: {course}')

            for lesson_data in lessons_data:
                quiz_data = lesson_data.pop('quiz', None)
                lesson, l_created = Lesson.objects.get_or_create(
                    course=course, order=lesson_data['order'],
                    defaults={**lesson_data, 'course': course}
                )
                if l_created:
                    self.stdout.write(f'    Leçon créée: {lesson}')

                if quiz_data and l_created:
                    questions_data = quiz_data.pop('questions', [])
                    quiz = Quiz.objects.create(lesson=lesson, **quiz_data)
                    for q_data in questions_data:
                        choices_raw = q_data.pop('choices', [])
                        question = QuizQuestion.objects.create(quiz=quiz, **q_data)
                        for idx, (text, is_correct) in enumerate(choices_raw):
                            QuizChoice.objects.create(
                                question=question, text=text,
                                is_correct=is_correct, order=idx + 1
                            )
                    self.stdout.write(f'      Quiz créé pour: {lesson.title}')

        self.stdout.write(self.style.SUCCESS(
            '\n✅ Seed AMN terminé avec succès !\n'
            f'  {Department.objects.count()} départements\n'
            f'  {TrainingModule.objects.count()} modules\n'
            f'  {Course.objects.count()} cours\n'
            f'  {Lesson.objects.count()} leçons\n'
            f'  {Quiz.objects.count()} quiz\n'
        ))
