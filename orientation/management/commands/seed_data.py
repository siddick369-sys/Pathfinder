"""
PathFinder — Commande de peuplement de la base de données.

Crée les données initiales nécessaires au fonctionnement de la plateforme :
- Compétences (Skills)
- Parcours de carrière (CareerPath) avec étapes
- 10 Questions d'orientation avec choix pondérés
- Mini-quiz hebdomadaires
- Badges de gamification
- Boosters boutique
- Catégories blog & marketplace
"""
from django.core.management.base import BaseCommand
from orientation.models import OrientationQuestion, OrientationChoice, MiniQuiz, MiniQuizChoice
from parcours.models import CareerPath, CareerStep
from competences.models import Skill, SkillResource
from gamification.models import Badge, Booster, Challenge
from blog.models import Category as BlogCategory
from marketplace.models import ServiceCategory
from django.utils import timezone
from datetime import timedelta


class Command(BaseCommand):
    help = 'Peuple la base de données avec les données initiales de PathFinder'

    def handle(self, *args, **options):
        self.stdout.write('=== Peuplement de la base PathFinder ===\n')
        self.create_skills()
        self.create_career_paths()
        self.create_orientation_questions()
        self.create_mini_quizzes()
        self.create_badges()
        self.create_boosters()
        self.create_blog_categories()
        self.create_service_categories()
        self.create_challenges()
        self.stdout.write(self.style.SUCCESS('\n✅ Base de données peuplée avec succès !'))

    def create_skills(self):
        self.stdout.write('  → Création des compétences...')
        skills_data = [
            {'slug': 'python', 'name': 'Python', 'icon': '🐍', 'description': 'Langage de programmation polyvalent pour le web, la data et l\'IA.'},
            {'slug': 'javascript', 'name': 'JavaScript', 'icon': '⚡', 'description': 'Langage incontournable pour le développement web frontend et backend.'},
            {'slug': 'html-css', 'name': 'HTML/CSS', 'icon': '🎨', 'description': 'Fondamentaux du développement web : structure et mise en page.'},
            {'slug': 'react', 'name': 'React', 'icon': '⚛️', 'description': 'Bibliothèque JavaScript pour construire des interfaces utilisateur modernes.'},
            {'slug': 'django', 'name': 'Django', 'icon': '🟢', 'description': 'Framework Python puissant pour le développement web rapide et sécurisé.'},
            {'slug': 'sql', 'name': 'SQL & Bases de données', 'icon': '🗄️', 'description': 'Gestion et interrogation des bases de données relationnelles.'},
            {'slug': 'data-analysis', 'name': 'Analyse de données', 'icon': '📊', 'description': 'Collecte, nettoyage et analyse de données pour la prise de décision.'},
            {'slug': 'machine-learning', 'name': 'Machine Learning', 'icon': '🤖', 'description': 'Algorithmes d\'apprentissage automatique et intelligence artificielle.'},
            {'slug': 'gestion-projet', 'name': 'Gestion de projet', 'icon': '📋', 'description': 'Planification, organisation et suivi de projets numériques.'},
            {'slug': 'marketing-digital', 'name': 'Marketing digital', 'icon': '📱', 'description': 'Stratégies de marketing en ligne : SEO, réseaux sociaux, publicité.'},
            {'slug': 'ui-ux', 'name': 'Design UI/UX', 'icon': '🖌️', 'description': 'Conception d\'interfaces utilisateur intuitives et expérience utilisateur.'},
            {'slug': 'cybersecurite', 'name': 'Cybersécurité', 'icon': '🔒', 'description': 'Protection des systèmes informatiques et des données.'},
            {'slug': 'cloud-devops', 'name': 'Cloud & DevOps', 'icon': '☁️', 'description': 'Infrastructure cloud, conteneurisation et déploiement continu.'},
            {'slug': 'mobile-dev', 'name': 'Développement mobile', 'icon': '📲', 'description': 'Création d\'applications mobiles Android et iOS.'},
            {'slug': 'communication', 'name': 'Communication', 'icon': '🗣️', 'description': 'Techniques de communication professionnelle et prise de parole.'},
            {'slug': 'comptabilite', 'name': 'Comptabilité & Finance', 'icon': '💰', 'description': 'Gestion comptable, analyse financière et budgétisation.'},
            {'slug': 'entrepreneuriat', 'name': 'Entrepreneuriat', 'icon': '🚀', 'description': 'Création d\'entreprise, business plan et levée de fonds.'},
            {'slug': 'anglais-pro', 'name': 'Anglais professionnel', 'icon': '🇬🇧', 'description': 'Maîtrise de l\'anglais dans un contexte professionnel et technique.'},
        ]
        for data in skills_data:
            Skill.objects.get_or_create(slug=data['slug'], defaults=data)
        self.stdout.write(f'    {len(skills_data)} compétences créées.')

        # Ajouter quelques ressources pour les compétences principales
        resources_data = [
            {'skill_slug': 'python', 'title': 'Introduction à Python', 'resource_type': 'video', 'level': 'debutant', 'duration_minutes': 45, 'xp_reward': 25, 'is_free_preview': True,
             'description': 'Découvrez les bases de Python : variables, types, boucles et fonctions.'},
            {'skill_slug': 'python', 'title': 'Python : Les structures de données', 'resource_type': 'tutoriel', 'level': 'debutant', 'duration_minutes': 60, 'xp_reward': 30,
             'description': 'Listes, dictionnaires, tuples et ensembles en Python.'},
            {'skill_slug': 'python', 'title': 'Exercices Python débutant', 'resource_type': 'exercice', 'level': 'debutant', 'duration_minutes': 90, 'xp_reward': 40,
             'description': '20 exercices pratiques pour consolider vos bases Python.'},
            {'skill_slug': 'javascript', 'title': 'JavaScript pour débutants', 'resource_type': 'video', 'level': 'debutant', 'duration_minutes': 50, 'xp_reward': 25, 'is_free_preview': True,
             'description': 'Les fondamentaux de JavaScript : syntaxe, DOM et événements.'},
            {'skill_slug': 'javascript', 'title': 'ES6+ : Les nouveautés modernes', 'resource_type': 'tutoriel', 'level': 'intermediaire', 'duration_minutes': 40, 'xp_reward': 35,
             'description': 'Arrow functions, destructuring, async/await et modules ES6.'},
            {'skill_slug': 'html-css', 'title': 'Créer sa première page web', 'resource_type': 'video', 'level': 'debutant', 'duration_minutes': 30, 'xp_reward': 20, 'is_free_preview': True,
             'description': 'Apprenez à structurer une page HTML et la styliser avec CSS.'},
            {'skill_slug': 'html-css', 'title': 'CSS Flexbox & Grid', 'resource_type': 'tutoriel', 'level': 'intermediaire', 'duration_minutes': 45, 'xp_reward': 30,
             'description': 'Maîtrisez les layouts modernes avec Flexbox et CSS Grid.'},
            {'skill_slug': 'django', 'title': 'Démarrer avec Django', 'resource_type': 'mini_formation', 'level': 'debutant', 'duration_minutes': 120, 'xp_reward': 50, 'is_free_preview': True,
             'description': 'Créez votre première application web avec Django de A à Z.'},
            {'skill_slug': 'data-analysis', 'title': 'Pandas & NumPy : les bases', 'resource_type': 'video', 'level': 'debutant', 'duration_minutes': 60, 'xp_reward': 30,
             'description': 'Manipulation de données avec les bibliothèques Python essentielles.'},
            {'skill_slug': 'gestion-projet', 'title': 'Méthodologie Agile/Scrum', 'resource_type': 'pdf', 'level': 'debutant', 'duration_minutes': 30, 'xp_reward': 20, 'is_free_preview': True,
             'description': 'Comprendre la gestion de projet Agile et le framework Scrum.'},
            {'skill_slug': 'marketing-digital', 'title': 'SEO : Référencement naturel', 'resource_type': 'tutoriel', 'level': 'debutant', 'duration_minutes': 45, 'xp_reward': 25,
             'description': 'Optimiser la visibilité de votre site sur Google.'},
            {'skill_slug': 'ui-ux', 'title': 'Principes de Design UX', 'resource_type': 'video', 'level': 'debutant', 'duration_minutes': 40, 'xp_reward': 25, 'is_free_preview': True,
             'description': 'Les principes fondamentaux pour concevoir des interfaces centrées utilisateur.'},
        ]
        for i, data in enumerate(resources_data):
            skill_slug = data.pop('skill_slug')
            try:
                skill = Skill.objects.get(slug=skill_slug)
                data['skill'] = skill
                data['order'] = i
                data.setdefault('is_free_preview', False)
                SkillResource.objects.get_or_create(title=data['title'], defaults=data)
            except Skill.DoesNotExist:
                pass
        self.stdout.write(f'    {len(resources_data)} ressources créées.')

    def create_career_paths(self):
        self.stdout.write('  → Création des parcours de carrière...')
        careers = [
            {
                'slug': 'fullstack',
                'title': 'Développeur Full-Stack',
                'description': 'Maîtrisez le développement web de A à Z : frontend, backend, bases de données et déploiement. Le développeur full-stack est l\'un des profils les plus recherchés au Cameroun.',
                'tags': ['Informatique', 'Web', 'Programmation'],
                'icon': '💻',
                'skills': ['python', 'javascript', 'html-css', 'react', 'django', 'sql', 'cloud-devops'],
                'steps': [
                    {'order': 1, 'title': 'Fondamentaux du Web', 'description': 'HTML, CSS et JavaScript de base', 'is_free': True, 'price_fcfa': 0, 'duration_hours': 40, 'icon': '🌐', 'features': ['Cours vidéo 12h', '8 projets pratiques', 'Quiz interactifs']},
                    {'order': 2, 'title': 'JavaScript Avancé & React', 'description': 'Maîtrisez JS moderne et React pour le frontend', 'is_free': False, 'price_fcfa': 15000, 'duration_hours': 60, 'icon': '⚛️', 'features': ['Cours vidéo 20h', '5 projets React', 'Mentorat hebdomadaire']},
                    {'order': 3, 'title': 'Backend avec Python/Django', 'description': 'API REST, authentification, bases de données', 'is_free': False, 'price_fcfa': 20000, 'duration_hours': 80, 'icon': '🐍', 'features': ['Cours vidéo 25h', '6 projets backend', 'Code review par mentor']},
                    {'order': 4, 'title': 'Projet Final Full-Stack', 'description': 'Construisez une application complète déployée en production', 'is_free': False, 'price_fcfa': 10000, 'is_premium': True, 'duration_hours': 40, 'icon': '🚀', 'features': ['Projet guidé', 'Déploiement cloud', 'Certificat professionnel']},
                ],
            },
            {
                'slug': 'data_analyst',
                'title': 'Data Analyst',
                'description': 'Apprenez à collecter, analyser et visualiser les données pour aider les entreprises camerounaises à prendre de meilleures décisions.',
                'tags': ['Data', 'Statistiques', 'Business Intelligence'],
                'icon': '📊',
                'skills': ['python', 'sql', 'data-analysis', 'machine-learning', 'anglais-pro'],
                'steps': [
                    {'order': 1, 'title': 'Bases de données & SQL', 'description': 'Maîtrisez les requêtes SQL et la modélisation de données', 'is_free': True, 'price_fcfa': 0, 'duration_hours': 30, 'icon': '🗄️', 'features': ['Cours vidéo 10h', '50 exercices SQL', 'Projet base de données']},
                    {'order': 2, 'title': 'Python pour la Data', 'description': 'Pandas, NumPy, Matplotlib pour l\'analyse exploratoire', 'is_free': False, 'price_fcfa': 15000, 'duration_hours': 50, 'icon': '🐍', 'features': ['Cours vidéo 15h', 'Datasets camerounais', '4 projets data']},
                    {'order': 3, 'title': 'Visualisation & Reporting', 'description': 'Créez des dashboards et rapports interactifs', 'is_free': False, 'price_fcfa': 15000, 'duration_hours': 40, 'icon': '📈', 'features': ['Power BI / Tableau', 'Storytelling data', 'Projet dashboard']},
                    {'order': 4, 'title': 'Machine Learning Introduction', 'description': 'Modèles prédictifs et classification de données', 'is_free': False, 'price_fcfa': 25000, 'is_premium': True, 'duration_hours': 60, 'icon': '🤖', 'features': ['Scikit-learn', '5 projets ML', 'Certificat Data Analyst']},
                ],
            },
            {
                'slug': 'chef_projet',
                'title': 'Chef de Projet Digital',
                'description': 'Pilotez des projets numériques de bout en bout : planification, coordination d\'équipes, livraison. Un rôle stratégique pour les entreprises en transformation digitale.',
                'tags': ['Management', 'Organisation', 'Digital'],
                'icon': '📋',
                'skills': ['gestion-projet', 'communication', 'marketing-digital', 'entrepreneuriat', 'anglais-pro'],
                'steps': [
                    {'order': 1, 'title': 'Fondamentaux de la Gestion de Projet', 'description': 'Méthodologies Agile, Scrum, outils de planification', 'is_free': True, 'price_fcfa': 0, 'duration_hours': 25, 'icon': '📋', 'features': ['Cours vidéo 8h', 'Templates Notion/Trello', 'Études de cas']},
                    {'order': 2, 'title': 'Leadership & Communication', 'description': 'Gérez des équipes et communiquez efficacement', 'is_free': False, 'price_fcfa': 12000, 'duration_hours': 30, 'icon': '🗣️', 'features': ['Cours vidéo 10h', 'Simulations de réunion', 'Feedback personnalisé']},
                    {'order': 3, 'title': 'Outils & Workflow Digital', 'description': 'Maîtrisez les outils de gestion et d\'automatisation', 'is_free': False, 'price_fcfa': 15000, 'duration_hours': 35, 'icon': '⚙️', 'features': ['Jira, Slack, Notion', 'Automatisations', 'Projet réel']},
                    {'order': 4, 'title': 'Projet Capstone : Pilotage Complet', 'description': 'Gérez un projet digital de A à Z avec une vraie équipe', 'is_free': False, 'price_fcfa': 10000, 'is_premium': True, 'duration_hours': 40, 'icon': '🏆', 'features': ['Projet en équipe', 'Mentorat senior', 'Certificat Chef de Projet']},
                ],
            },
            {
                'slug': 'marketing_digital',
                'title': 'Spécialiste Marketing Digital',
                'description': 'Devenez expert en stratégies marketing en ligne : SEO, réseaux sociaux, publicité payante, email marketing. Très demandé par les PME camerounaises.',
                'tags': ['Marketing', 'Communication', 'Réseaux sociaux'],
                'icon': '📱',
                'skills': ['marketing-digital', 'communication', 'ui-ux', 'entrepreneuriat', 'anglais-pro'],
                'steps': [
                    {'order': 1, 'title': 'Fondamentaux du Marketing Digital', 'description': 'SEO, SEA, réseaux sociaux et stratégie de contenu', 'is_free': True, 'price_fcfa': 0, 'duration_hours': 20, 'icon': '📱', 'features': ['Cours vidéo 8h', 'Templates de stratégie', 'Exercices pratiques']},
                    {'order': 2, 'title': 'Community Management', 'description': 'Gérez les réseaux sociaux et créez du contenu engageant', 'is_free': False, 'price_fcfa': 10000, 'duration_hours': 30, 'icon': '💬', 'features': ['Stratégie réseaux sociaux', 'Création de contenu', 'Outils de planification']},
                    {'order': 3, 'title': 'Publicité en ligne & Analytics', 'description': 'Google Ads, Facebook Ads et analyse de performance', 'is_free': False, 'price_fcfa': 18000, 'duration_hours': 40, 'icon': '📈', 'features': ['Campagnes publicitaires', 'Google Analytics', 'Optimisation ROI']},
                    {'order': 4, 'title': 'Projet : Stratégie Marketing Complète', 'description': 'Élaborez et exécutez une stratégie marketing pour un client réel', 'is_free': False, 'price_fcfa': 12000, 'is_premium': True, 'duration_hours': 35, 'icon': '🎯', 'features': ['Client réel', 'Rapport de performance', 'Certificat Marketing']},
                ],
            },
            {
                'slug': 'mobile_dev',
                'title': 'Développeur Mobile',
                'description': 'Créez des applications mobiles pour Android et iOS. Le mobile est le premier canal d\'accès à Internet en Afrique.',
                'tags': ['Mobile', 'Android', 'iOS', 'Programmation'],
                'icon': '📲',
                'skills': ['javascript', 'react', 'mobile-dev', 'ui-ux', 'sql'],
                'steps': [
                    {'order': 1, 'title': 'Fondamentaux Mobile', 'description': 'UX mobile, JavaScript et introduction à React Native', 'is_free': True, 'price_fcfa': 0, 'duration_hours': 30, 'icon': '📲', 'features': ['Cours vidéo 10h', 'Principes UX mobile', 'Première app']},
                    {'order': 2, 'title': 'React Native Avancé', 'description': 'Navigation, state management et API natives', 'is_free': False, 'price_fcfa': 18000, 'duration_hours': 50, 'icon': '⚛️', 'features': ['Cours vidéo 18h', '6 mini-projets', 'Accès API caméra, GPS']},
                    {'order': 3, 'title': 'Backend Mobile & Firebase', 'description': 'Authentification, base de données temps réel, notifications push', 'is_free': False, 'price_fcfa': 15000, 'duration_hours': 40, 'icon': '🔥', 'features': ['Firebase complet', 'Notifications push', 'Stockage cloud']},
                    {'order': 4, 'title': 'Publication sur les Stores', 'description': 'Déployez votre app sur Google Play et App Store', 'is_free': False, 'price_fcfa': 10000, 'is_premium': True, 'duration_hours': 20, 'icon': '🏪', 'features': ['Publication Google Play', 'App Store Connect', 'Certificat Dev Mobile']},
                ],
            },
            {
                'slug': 'cybersecurite',
                'title': 'Analyste Cybersécurité',
                'description': 'Protégez les systèmes informatiques contre les menaces. La cybersécurité est un secteur en pleine croissance au Cameroun et en Afrique.',
                'tags': ['Sécurité', 'Réseaux', 'Informatique'],
                'icon': '🔒',
                'skills': ['cybersecurite', 'python', 'sql', 'cloud-devops', 'anglais-pro'],
                'steps': [
                    {'order': 1, 'title': 'Fondamentaux Sécurité', 'description': 'Réseaux, protocoles et principes de sécurité informatique', 'is_free': True, 'price_fcfa': 0, 'duration_hours': 35, 'icon': '🔒', 'features': ['Cours vidéo 12h', 'Labs pratiques', 'Quiz sécurité']},
                    {'order': 2, 'title': 'Tests d\'intrusion', 'description': 'Méthodologie de pentest et outils de sécurité offensive', 'is_free': False, 'price_fcfa': 20000, 'duration_hours': 50, 'icon': '🕵️', 'features': ['Kali Linux', 'OWASP Top 10', 'Environnements de lab']},
                    {'order': 3, 'title': 'Sécurité Cloud & Défensive', 'description': 'Surveillance, détection d\'incidents et sécurité cloud', 'is_free': False, 'price_fcfa': 22000, 'duration_hours': 45, 'icon': '🛡️', 'features': ['SIEM & monitoring', 'AWS Security', 'Incident response']},
                    {'order': 4, 'title': 'Projet : Audit de Sécurité', 'description': 'Réalisez un audit de sécurité complet pour une organisation', 'is_free': False, 'price_fcfa': 15000, 'is_premium': True, 'duration_hours': 30, 'icon': '📝', 'features': ['Audit complet', 'Rapport professionnel', 'Certificat Cybersécurité']},
                ],
            },
        ]

        for career_data in careers:
            skills_slugs = career_data.pop('skills')
            steps_data = career_data.pop('steps')
            career, created = CareerPath.objects.get_or_create(
                slug=career_data['slug'],
                defaults=career_data
            )
            if created:
                # Associer les compétences
                for slug in skills_slugs:
                    try:
                        skill = Skill.objects.get(slug=slug)
                        career.skills.add(skill)
                    except Skill.DoesNotExist:
                        pass
                # Créer les étapes
                for step_data in steps_data:
                    step_data.setdefault('is_premium', False)
                    CareerStep.objects.get_or_create(
                        career=career, order=step_data['order'],
                        defaults=step_data
                    )
        self.stdout.write(f'    {len(careers)} parcours de carrière créés avec étapes.')

    def create_orientation_questions(self):
        self.stdout.write('  → Création des 10 questions d\'orientation...')

        # Slugs des carrières utilisés dans les poids
        # fullstack, data_analyst, chef_projet, marketing_digital, mobile_dev, cybersecurite

        questions = [
            # Q1 - Centre d'intérêt
            {
                'text': 'Quel type d\'activité vous passionne le plus ?',
                'order': 1,
                'category': 'interest',
                'icon': '💡',
                'choices': [
                    {'text': 'Créer des sites web et des applications', 'icon': '💻',
                     'weights': {'fullstack': 5, 'data_analyst': 1, 'chef_projet': 2, 'marketing_digital': 2, 'mobile_dev': 4, 'cybersecurite': 2}},
                    {'text': 'Analyser des chiffres et trouver des tendances', 'icon': '📊',
                     'weights': {'fullstack': 1, 'data_analyst': 5, 'chef_projet': 3, 'marketing_digital': 3, 'mobile_dev': 1, 'cybersecurite': 2}},
                    {'text': 'Organiser et coordonner des équipes', 'icon': '👥',
                     'weights': {'fullstack': 1, 'data_analyst': 1, 'chef_projet': 5, 'marketing_digital': 3, 'mobile_dev': 1, 'cybersecurite': 1}},
                    {'text': 'Protéger les systèmes contre les hackers', 'icon': '🔒',
                     'weights': {'fullstack': 2, 'data_analyst': 2, 'chef_projet': 1, 'marketing_digital': 0, 'mobile_dev': 1, 'cybersecurite': 5}},
                ],
            },
            # Q2 - Centre d'intérêt
            {
                'text': 'Quel contenu consommez-vous le plus sur Internet ?',
                'order': 2,
                'category': 'interest',
                'icon': '🌐',
                'choices': [
                    {'text': 'Des tutoriels de programmation et de code', 'icon': '🖥️',
                     'weights': {'fullstack': 5, 'data_analyst': 3, 'chef_projet': 1, 'marketing_digital': 0, 'mobile_dev': 5, 'cybersecurite': 3}},
                    {'text': 'Des articles sur le business et le management', 'icon': '📰',
                     'weights': {'fullstack': 0, 'data_analyst': 2, 'chef_projet': 5, 'marketing_digital': 4, 'mobile_dev': 0, 'cybersecurite': 1}},
                    {'text': 'Des vidéos sur le marketing et les réseaux sociaux', 'icon': '📹',
                     'weights': {'fullstack': 0, 'data_analyst': 1, 'chef_projet': 2, 'marketing_digital': 5, 'mobile_dev': 1, 'cybersecurite': 0}},
                    {'text': 'Des actualités sur la cybersécurité et les nouvelles technologies', 'icon': '🛡️',
                     'weights': {'fullstack': 3, 'data_analyst': 2, 'chef_projet': 1, 'marketing_digital': 1, 'mobile_dev': 2, 'cybersecurite': 5}},
                ],
            },
            # Q3 - Style de travail
            {
                'text': 'Comment préférez-vous travailler ?',
                'order': 3,
                'category': 'workstyle',
                'icon': '🏢',
                'choices': [
                    {'text': 'Seul(e), concentré(e) devant mon écran à coder', 'icon': '🧑‍💻',
                     'weights': {'fullstack': 5, 'data_analyst': 4, 'chef_projet': 1, 'marketing_digital': 1, 'mobile_dev': 5, 'cybersecurite': 4}},
                    {'text': 'En équipe, en échangeant des idées constamment', 'icon': '🤝',
                     'weights': {'fullstack': 2, 'data_analyst': 2, 'chef_projet': 5, 'marketing_digital': 4, 'mobile_dev': 2, 'cybersecurite': 2}},
                    {'text': 'Un mix : travail solo et réunions stratégiques', 'icon': '⚖️',
                     'weights': {'fullstack': 3, 'data_analyst': 3, 'chef_projet': 4, 'marketing_digital': 3, 'mobile_dev': 3, 'cybersecurite': 3}},
                    {'text': 'En investigation, à chercher des failles et résoudre des problèmes', 'icon': '🔍',
                     'weights': {'fullstack': 3, 'data_analyst': 4, 'chef_projet': 1, 'marketing_digital': 1, 'mobile_dev': 2, 'cybersecurite': 5}},
                ],
            },
            # Q4 - Objectif
            {
                'text': 'Quel est votre objectif professionnel principal ?',
                'order': 4,
                'category': 'goal',
                'icon': '🎯',
                'choices': [
                    {'text': 'Travailler en freelance et être indépendant(e)', 'icon': '🏠',
                     'weights': {'fullstack': 5, 'data_analyst': 3, 'chef_projet': 2, 'marketing_digital': 4, 'mobile_dev': 5, 'cybersecurite': 3}},
                    {'text': 'Intégrer une grande entreprise ou une multinationale', 'icon': '🏢',
                     'weights': {'fullstack': 3, 'data_analyst': 4, 'chef_projet': 5, 'marketing_digital': 3, 'mobile_dev': 3, 'cybersecurite': 5}},
                    {'text': 'Créer ma propre entreprise tech au Cameroun', 'icon': '🚀',
                     'weights': {'fullstack': 4, 'data_analyst': 2, 'chef_projet': 4, 'marketing_digital': 5, 'mobile_dev': 4, 'cybersecurite': 2}},
                    {'text': 'Travailler à distance pour des clients internationaux', 'icon': '🌍',
                     'weights': {'fullstack': 5, 'data_analyst': 4, 'chef_projet': 3, 'marketing_digital': 3, 'mobile_dev': 4, 'cybersecurite': 4}},
                ],
            },
            # Q5 - Compétence
            {
                'text': 'Quelle compétence vous attire le plus ?',
                'order': 5,
                'category': 'skill',
                'icon': '⚡',
                'choices': [
                    {'text': 'La programmation et la logique algorithmique', 'icon': '🧮',
                     'weights': {'fullstack': 5, 'data_analyst': 4, 'chef_projet': 1, 'marketing_digital': 0, 'mobile_dev': 5, 'cybersecurite': 4}},
                    {'text': 'La communication et la persuasion', 'icon': '🎤',
                     'weights': {'fullstack': 0, 'data_analyst': 1, 'chef_projet': 4, 'marketing_digital': 5, 'mobile_dev': 0, 'cybersecurite': 1}},
                    {'text': 'L\'analyse de données et les statistiques', 'icon': '📉',
                     'weights': {'fullstack': 1, 'data_analyst': 5, 'chef_projet': 2, 'marketing_digital': 3, 'mobile_dev': 1, 'cybersecurite': 3}},
                    {'text': 'Le design et la créativité visuelle', 'icon': '🎨',
                     'weights': {'fullstack': 3, 'data_analyst': 1, 'chef_projet': 2, 'marketing_digital': 4, 'mobile_dev': 4, 'cybersecurite': 0}},
                ],
            },
            # Q6 - Style de travail
            {
                'text': 'Face à un problème complexe, quelle est votre première réaction ?',
                'order': 6,
                'category': 'workstyle',
                'icon': '🧩',
                'choices': [
                    {'text': 'Je décompose le problème en petites parties et je code une solution', 'icon': '🔧',
                     'weights': {'fullstack': 5, 'data_analyst': 3, 'chef_projet': 2, 'marketing_digital': 1, 'mobile_dev': 5, 'cybersecurite': 4}},
                    {'text': 'Je collecte des données pour comprendre la situation', 'icon': '📊',
                     'weights': {'fullstack': 2, 'data_analyst': 5, 'chef_projet': 3, 'marketing_digital': 3, 'mobile_dev': 1, 'cybersecurite': 3}},
                    {'text': 'Je réunis l\'équipe pour brainstormer ensemble', 'icon': '💬',
                     'weights': {'fullstack': 1, 'data_analyst': 1, 'chef_projet': 5, 'marketing_digital': 4, 'mobile_dev': 1, 'cybersecurite': 1}},
                    {'text': 'Je cherche les vulnérabilités et les failles dans le système', 'icon': '🕵️',
                     'weights': {'fullstack': 2, 'data_analyst': 2, 'chef_projet': 1, 'marketing_digital': 0, 'mobile_dev': 1, 'cybersecurite': 5}},
                ],
            },
            # Q7 - Centre d'intérêt
            {
                'text': 'Quel projet vous motiverait le plus ?',
                'order': 7,
                'category': 'interest',
                'icon': '🔥',
                'choices': [
                    {'text': 'Développer une application mobile utilisée par des milliers de Camerounais', 'icon': '📲',
                     'weights': {'fullstack': 4, 'data_analyst': 1, 'chef_projet': 3, 'marketing_digital': 2, 'mobile_dev': 5, 'cybersecurite': 1}},
                    {'text': 'Analyser les données de vente d\'une entreprise pour augmenter ses revenus', 'icon': '💹',
                     'weights': {'fullstack': 1, 'data_analyst': 5, 'chef_projet': 3, 'marketing_digital': 4, 'mobile_dev': 0, 'cybersecurite': 1}},
                    {'text': 'Piloter la transformation digitale d\'une entreprise locale', 'icon': '🏗️',
                     'weights': {'fullstack': 2, 'data_analyst': 2, 'chef_projet': 5, 'marketing_digital': 3, 'mobile_dev': 1, 'cybersecurite': 2}},
                    {'text': 'Sécuriser les systèmes informatiques d\'une banque camerounaise', 'icon': '🏦',
                     'weights': {'fullstack': 2, 'data_analyst': 2, 'chef_projet': 1, 'marketing_digital': 0, 'mobile_dev': 1, 'cybersecurite': 5}},
                ],
            },
            # Q8 - Objectif
            {
                'text': 'Quel salaire mensuel visez-vous dans 3 ans ?',
                'order': 8,
                'category': 'goal',
                'icon': '💰',
                'choices': [
                    {'text': '200 000 - 400 000 FCFA (emploi stable)', 'icon': '💵',
                     'weights': {'fullstack': 2, 'data_analyst': 3, 'chef_projet': 3, 'marketing_digital': 4, 'mobile_dev': 2, 'cybersecurite': 3}},
                    {'text': '400 000 - 800 000 FCFA (profil qualifié)', 'icon': '💶',
                     'weights': {'fullstack': 4, 'data_analyst': 4, 'chef_projet': 4, 'marketing_digital': 3, 'mobile_dev': 4, 'cybersecurite': 4}},
                    {'text': '800 000+ FCFA (expert ou freelance international)', 'icon': '💎',
                     'weights': {'fullstack': 5, 'data_analyst': 4, 'chef_projet': 3, 'marketing_digital': 2, 'mobile_dev': 5, 'cybersecurite': 5}},
                    {'text': 'Je préfère monter mon business plutôt qu\'avoir un salaire fixe', 'icon': '🚀',
                     'weights': {'fullstack': 3, 'data_analyst': 2, 'chef_projet': 4, 'marketing_digital': 5, 'mobile_dev': 3, 'cybersecurite': 1}},
                ],
            },
            # Q9 - Compétence
            {
                'text': 'Quelle matière scolaire préfériez-vous ?',
                'order': 9,
                'category': 'skill',
                'icon': '📚',
                'choices': [
                    {'text': 'Mathématiques et sciences', 'icon': '🔢',
                     'weights': {'fullstack': 4, 'data_analyst': 5, 'chef_projet': 2, 'marketing_digital': 1, 'mobile_dev': 4, 'cybersecurite': 4}},
                    {'text': 'Français et communication', 'icon': '📝',
                     'weights': {'fullstack': 1, 'data_analyst': 1, 'chef_projet': 4, 'marketing_digital': 5, 'mobile_dev': 1, 'cybersecurite': 1}},
                    {'text': 'Informatique et technologie', 'icon': '💻',
                     'weights': {'fullstack': 5, 'data_analyst': 3, 'chef_projet': 2, 'marketing_digital': 2, 'mobile_dev': 5, 'cybersecurite': 5}},
                    {'text': 'Économie et gestion', 'icon': '📈',
                     'weights': {'fullstack': 1, 'data_analyst': 3, 'chef_projet': 5, 'marketing_digital': 4, 'mobile_dev': 1, 'cybersecurite': 1}},
                ],
            },
            # Q10 - Objectif
            {
                'text': 'Comment voyez-vous le numérique au Cameroun dans 5 ans ?',
                'order': 10,
                'category': 'goal',
                'icon': '🔮',
                'choices': [
                    {'text': 'Les développeurs camerounais créeront des solutions utilisées en Afrique et dans le monde', 'icon': '🌍',
                     'weights': {'fullstack': 5, 'data_analyst': 2, 'chef_projet': 3, 'marketing_digital': 2, 'mobile_dev': 5, 'cybersecurite': 3}},
                    {'text': 'La data et l\'IA transformeront les entreprises camerounaises', 'icon': '🤖',
                     'weights': {'fullstack': 2, 'data_analyst': 5, 'chef_projet': 3, 'marketing_digital': 2, 'mobile_dev': 2, 'cybersecurite': 3}},
                    {'text': 'Le marketing digital deviendra le moteur de croissance des PME', 'icon': '📱',
                     'weights': {'fullstack': 1, 'data_analyst': 2, 'chef_projet': 3, 'marketing_digital': 5, 'mobile_dev': 2, 'cybersecurite': 1}},
                    {'text': 'La cybersécurité sera la priorité n°1 pour toutes les organisations', 'icon': '🛡️',
                     'weights': {'fullstack': 2, 'data_analyst': 2, 'chef_projet': 2, 'marketing_digital': 1, 'mobile_dev': 1, 'cybersecurite': 5}},
                ],
            },
        ]

        for q_data in questions:
            choices_data = q_data.pop('choices')
            question, created = OrientationQuestion.objects.get_or_create(
                order=q_data['order'],
                defaults=q_data
            )
            if created:
                for c_data in choices_data:
                    OrientationChoice.objects.create(question=question, **c_data)
        self.stdout.write(f'    {len(questions)} questions d\'orientation créées avec choix pondérés.')

    def create_mini_quizzes(self):
        self.stdout.write('  → Création des mini-quiz...')
        mini_quizzes = [
            {
                'text': 'Préférez-vous travailler sur le frontend (ce que l\'utilisateur voit) ou le backend (ce qui se passe côté serveur) ?',
                'icon': '🔄', 'week_number': 1,
                'choices': [
                    {'text': 'Frontend — J\'aime le design et l\'interactivité', 'weights': {'fullstack': 3, 'mobile_dev': 4, 'marketing_digital': 3, 'ui-ux': 5}},
                    {'text': 'Backend — J\'aime la logique et les algorithmes', 'weights': {'fullstack': 4, 'data_analyst': 3, 'cybersecurite': 4}},
                    {'text': 'Les deux me plaisent autant', 'weights': {'fullstack': 5, 'mobile_dev': 3, 'chef_projet': 2}},
                ],
            },
            {
                'text': 'Si vous aviez une journée libre pour apprendre, que choisiriez-vous ?',
                'icon': '📖', 'week_number': 2,
                'choices': [
                    {'text': 'Un cours de Python ou JavaScript', 'weights': {'fullstack': 5, 'data_analyst': 3, 'mobile_dev': 4, 'cybersecurite': 3}},
                    {'text': 'Un atelier marketing et réseaux sociaux', 'weights': {'marketing_digital': 5, 'chef_projet': 3, 'entrepreneuriat': 3}},
                    {'text': 'Une formation en gestion de projet', 'weights': {'chef_projet': 5, 'marketing_digital': 2, 'entrepreneuriat': 3}},
                ],
            },
            {
                'text': 'Quel réseau social utilisez-vous le plus pour vous informer professionnellement ?',
                'icon': '📲', 'week_number': 3,
                'choices': [
                    {'text': 'GitHub / Stack Overflow', 'weights': {'fullstack': 5, 'mobile_dev': 4, 'cybersecurite': 3, 'data_analyst': 3}},
                    {'text': 'LinkedIn', 'weights': {'chef_projet': 5, 'marketing_digital': 4, 'data_analyst': 3}},
                    {'text': 'Twitter/X et YouTube tech', 'weights': {'marketing_digital': 3, 'fullstack': 3, 'cybersecurite': 4, 'mobile_dev': 3}},
                ],
            },
            {
                'text': 'Dans un groupe de travail, quel rôle prenez-vous naturellement ?',
                'icon': '👥', 'week_number': 4,
                'choices': [
                    {'text': 'Le technicien — je construis et je code', 'weights': {'fullstack': 5, 'mobile_dev': 5, 'cybersecurite': 4}},
                    {'text': 'Le coordinateur — j\'organise et je répartis les tâches', 'weights': {'chef_projet': 5, 'marketing_digital': 3}},
                    {'text': 'L\'analyste — je recherche et je présente les données', 'weights': {'data_analyst': 5, 'cybersecurite': 3, 'marketing_digital': 2}},
                ],
            },
            {
                'text': 'Quel secteur camerounais vous intéresse le plus ?',
                'icon': '🇨🇲', 'week_number': 5,
                'choices': [
                    {'text': 'Fintech & Mobile Money', 'weights': {'fullstack': 4, 'mobile_dev': 5, 'cybersecurite': 4, 'data_analyst': 3}},
                    {'text': 'Agriculture & Agritech', 'weights': {'data_analyst': 4, 'mobile_dev': 3, 'chef_projet': 3}},
                    {'text': 'Commerce en ligne & E-business', 'weights': {'marketing_digital': 5, 'fullstack': 3, 'chef_projet': 3}},
                ],
            },
        ]

        for mq_data in mini_quizzes:
            choices_data = mq_data.pop('choices')
            quiz, created = MiniQuiz.objects.get_or_create(
                week_number=mq_data['week_number'],
                defaults=mq_data
            )
            if created:
                for c_data in choices_data:
                    MiniQuizChoice.objects.create(quiz=quiz, **c_data)
        self.stdout.write(f'    {len(mini_quizzes)} mini-quiz créés.')

    def create_badges(self):
        self.stdout.write('  → Création des badges...')
        badges = [
            {'slug': 'premier-pas', 'name': 'Premier Pas', 'description': 'Vous avez complété le test d\'orientation !', 'icon': '🎯', 'category': 'progression', 'condition_type': 'test_complete', 'condition_value': 1},
            {'slug': 'explorateur-100xp', 'name': 'Explorateur', 'description': 'Vous avez atteint 100 XP', 'icon': '🌟', 'category': 'progression', 'condition_type': 'xp_total', 'condition_value': 100},
            {'slug': 'apprenti-500xp', 'name': 'Apprenti Dévoué', 'description': 'Vous avez atteint 500 XP', 'icon': '📚', 'category': 'progression', 'condition_type': 'xp_total', 'condition_value': 500},
            {'slug': 'expert-1000xp', 'name': 'Expert en Herbe', 'description': 'Vous avez atteint 1000 XP', 'icon': '🏆', 'category': 'progression', 'condition_type': 'xp_total', 'condition_value': 1000},
            {'slug': 'legende-5000xp', 'name': 'Légende PathFinder', 'description': 'Vous avez atteint 5000 XP', 'icon': '👑', 'category': 'progression', 'condition_type': 'xp_total', 'condition_value': 5000},
            {'slug': 'niveau-2', 'name': 'Niveau 2 Atteint', 'description': 'Vous avez atteint le niveau Débutant Avancé', 'icon': '⬆️', 'category': 'progression', 'condition_type': 'level_reached', 'condition_value': 2},
            {'slug': 'niveau-5', 'name': 'Niveau 5 Atteint', 'description': 'Vous êtes un vrai expert !', 'icon': '🔥', 'category': 'progression', 'condition_type': 'level_reached', 'condition_value': 5},
            {'slug': 'regulier-7j', 'name': 'Régulier', 'description': '7 jours de connexion consécutifs', 'icon': '📅', 'category': 'regularite', 'condition_type': 'streak_days', 'condition_value': 7},
            {'slug': 'fidele-30j', 'name': 'Fidèle', 'description': '30 jours de connexion consécutifs', 'icon': '💪', 'category': 'regularite', 'condition_type': 'streak_days', 'condition_value': 30},
            {'slug': 'incassable-100j', 'name': 'Incassable', 'description': '100 jours de connexion consécutifs !', 'icon': '🦁', 'category': 'regularite', 'condition_type': 'streak_days', 'condition_value': 100},
            {'slug': 'premiere-etape', 'name': 'Première Étape', 'description': 'Vous avez complété votre première étape de carrière', 'icon': '✅', 'category': 'excellence', 'condition_type': 'steps_completed', 'condition_value': 1},
            {'slug': 'cinq-etapes', 'name': 'Cinq Étapes', 'description': 'Vous avez complété 5 étapes de carrière', 'icon': '🎖️', 'category': 'excellence', 'condition_type': 'steps_completed', 'condition_value': 5},
            {'slug': 'trois-competences', 'name': 'Triple Menace', 'description': 'Vous avez débloqué 3 compétences', 'icon': '🔓', 'category': 'excellence', 'condition_type': 'skills_unlocked', 'condition_value': 3},
            {'slug': 'premier-paiement', 'name': 'Investisseur', 'description': 'Vous avez effectué votre premier paiement', 'icon': '💳', 'category': 'special', 'condition_type': 'payment_made', 'condition_value': 1},
        ]
        for badge_data in badges:
            Badge.objects.get_or_create(slug=badge_data['slug'], defaults=badge_data)
        self.stdout.write(f'    {len(badges)} badges créés.')

    def create_boosters(self):
        self.stdout.write('  → Création des boosters boutique...')
        boosters = [
            {'slug': 'xp-double-7j', 'name': 'Double XP (7 jours)', 'description': 'Doublez tous vos gains d\'XP pendant 7 jours !', 'icon': '⚡', 'booster_type': 'xp_multiplier', 'price_fcfa': 2000, 'duration_days': 7, 'multiplier': 2.0},
            {'slug': 'xp-triple-3j', 'name': 'Triple XP (3 jours)', 'description': 'Triplez vos gains d\'XP pendant 3 jours intensifs !', 'icon': '🔥', 'booster_type': 'xp_multiplier', 'price_fcfa': 2500, 'duration_days': 3, 'multiplier': 3.0},
            {'slug': 'analyse-ia-pro', 'name': 'Analyse IA Pro', 'description': 'Obtenez une analyse approfondie de votre profil par notre IA avec des recommandations personnalisées.', 'icon': '🤖', 'booster_type': 'ai_analysis', 'price_fcfa': 3000, 'duration_days': 0, 'multiplier': 1.0},
            {'slug': 'pack-competences-5', 'name': 'Pack 5 Compétences', 'description': 'Débloquez 5 compétences premium d\'un coup !', 'icon': '📦', 'booster_type': 'pack_competences', 'price_fcfa': 8000, 'duration_days': 0, 'multiplier': 1.0},
            {'slug': 'theme-gold', 'name': 'Thème Gold', 'description': 'Personnalisez votre profil avec le thème exclusif Gold.', 'icon': '🏅', 'booster_type': 'theme', 'price_fcfa': 1500, 'duration_days': 0, 'multiplier': 1.0},
            {'slug': 'pack-ambassadeur', 'name': 'Pack Ambassadeur', 'description': 'Badge ambassadeur + Double XP 30 jours + Thème exclusif. Le pack ultime !', 'icon': '🌟', 'booster_type': 'pack_ambassadeur', 'price_fcfa': 15000, 'duration_days': 30, 'multiplier': 2.0},
        ]
        for booster_data in boosters:
            Booster.objects.get_or_create(slug=booster_data['slug'], defaults=booster_data)
        self.stdout.write(f'    {len(boosters)} boosters créés.')

    def create_blog_categories(self):
        self.stdout.write('  → Création des catégories blog...')
        categories = [
            {'slug': 'conseils-carriere', 'name': 'Conseils Carrière'},
            {'slug': 'tutoriels', 'name': 'Tutoriels'},
            {'slug': 'actualites-tech', 'name': 'Actualités Tech'},
            {'slug': 'temoignages', 'name': 'Témoignages'},
            {'slug': 'marche-emploi-cameroun', 'name': 'Marché de l\'emploi au Cameroun'},
            {'slug': 'entrepreneuriat', 'name': 'Entrepreneuriat'},
        ]
        for cat_data in categories:
            BlogCategory.objects.get_or_create(slug=cat_data['slug'], defaults=cat_data)
        self.stdout.write(f'    {len(categories)} catégories blog créées.')

    def create_service_categories(self):
        self.stdout.write('  → Création des catégories marketplace...')
        categories = [
            {'slug': 'dev-web', 'name': 'Développement Web', 'icon': '💻'},
            {'slug': 'dev-mobile', 'name': 'Développement Mobile', 'icon': '📲'},
            {'slug': 'design-graphique', 'name': 'Design Graphique', 'icon': '🎨'},
            {'slug': 'marketing-seo', 'name': 'Marketing & SEO', 'icon': '📈'},
            {'slug': 'redaction', 'name': 'Rédaction & Traduction', 'icon': '✍️'},
            {'slug': 'data-analyse', 'name': 'Data & Analyse', 'icon': '📊'},
            {'slug': 'formation', 'name': 'Formation & Tutorat', 'icon': '🎓'},
            {'slug': 'video-photo', 'name': 'Vidéo & Photo', 'icon': '🎬'},
        ]
        for cat_data in categories:
            ServiceCategory.objects.get_or_create(slug=cat_data['slug'], defaults=cat_data)
        self.stdout.write(f'    {len(categories)} catégories marketplace créées.')

    def create_challenges(self):
        self.stdout.write('  → Création des défis hebdomadaires...')
        today = timezone.now().date()
        challenges = [
            {'title': 'Complétez votre premier parcours', 'description': 'Terminez au moins 1 étape d\'un parcours de carrière cette semaine.', 'xp_reward': 200, 'start_date': today, 'end_date': today + timedelta(days=7)},
            {'title': 'Quiz Master', 'description': 'Répondez à tous les mini-quiz disponibles cette semaine.', 'xp_reward': 150, 'start_date': today, 'end_date': today + timedelta(days=7)},
            {'title': 'Partagez vos connaissances', 'description': 'Publiez un article sur le blog ou donnez un avis sur un projet.', 'xp_reward': 100, 'start_date': today + timedelta(days=7), 'end_date': today + timedelta(days=14)},
        ]
        for ch_data in challenges:
            Challenge.objects.get_or_create(title=ch_data['title'], defaults=ch_data)
        self.stdout.write(f'    {len(challenges)} défis créés.')
