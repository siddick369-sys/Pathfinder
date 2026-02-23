"""
Commande de gestion pour créer les données de démonstration.
Usage : python manage.py seed_demo
"""
from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta


class Command(BaseCommand):
    help = 'Crée les données de démonstration PathFinder'

    def handle(self, *args, **options):
        self.stdout.write('🌱 Création des données de démonstration...\n')

        self._create_skills()
        self._create_careers()
        self._create_questions()
        self._create_badges()
        self._create_boosters()
        self._create_challenges()
        self._create_blog()
        self._create_demo_user()

        self.stdout.write(self.style.SUCCESS('\n✅ Données de démonstration créées avec succès !'))
        self.stdout.write(self.style.SUCCESS('   Utilisateur démo : amadou / pathfinder2025'))

    def _create_skills(self):
        from competences.models import Skill, SkillResource
        skills_data = [
            {'slug': 'html-css', 'name': 'HTML & CSS', 'description': 'Maîtrise des fondamentaux du web : structure HTML sémantique et mise en page CSS responsive.', 'icon': '🎨', 'is_premium': False, 'price_fcfa': 0},
            {'slug': 'javascript', 'name': 'JavaScript', 'description': 'Programmation côté client : DOM, événements, ES6+, async/await.', 'icon': '⚡', 'is_premium': False, 'price_fcfa': 0},
            {'slug': 'python', 'name': 'Python & Django', 'description': 'Développement backend avec Python et le framework Django.', 'icon': '🐍', 'is_premium': False, 'price_fcfa': 0},
            {'slug': 'react', 'name': 'React.js', 'description': 'Création d\'interfaces modernes avec React, hooks et state management.', 'icon': '⚛️', 'is_premium': False, 'price_fcfa': 0},
            {'slug': 'database', 'name': 'Bases de données', 'description': 'Conception et requêtes SQL, ORM Django, PostgreSQL.', 'icon': '🗄️', 'is_premium': True, 'price_fcfa': 1500},
            {'slug': 'devops', 'name': 'DevOps & Déploiement', 'description': 'Docker, CI/CD, déploiement cloud, monitoring.', 'icon': '🚀', 'is_premium': True, 'price_fcfa': 2000},
        ]
        for sd in skills_data:
            skill, created = Skill.objects.get_or_create(slug=sd['slug'], defaults=sd)
            if created:
                self._create_skill_resources(skill)
                self.stdout.write(f'  ✓ Compétence: {skill.name} ({skill.resources.count()} ressources)')

    def _create_skill_resources(self, skill):
        from competences.models import SkillResource
        resources_map = {
            'html-css': [
                {'title': 'Introduction au HTML', 'description': 'Apprenez les bases du langage HTML : balises, structure, sémantique.', 'resource_type': 'tutoriel', 'level': 'debutant', 'duration_minutes': 30, 'xp_reward': 25, 'order': 1, 'is_free_preview': True,
                 'content': 'Le HTML (HyperText Markup Language) est le langage de base du web.\n\n📌 Structure de base :\n\n<!DOCTYPE html>\n<html lang="fr">\n<head>\n  <meta charset="UTF-8">\n  <title>Ma première page</title>\n</head>\n<body>\n  <h1>Bonjour le monde !</h1>\n  <p>Ma première page web.</p>\n</body>\n</html>\n\n🔑 Points clés :\n- Les balises HTML structurent le contenu\n- Le DOCTYPE indique la version HTML\n- Le <head> contient les métadonnées\n- Le <body> contient le contenu visible\n\n✅ Exercice : Créez une page HTML avec un titre, un paragraphe et une liste.'},
                {'title': 'CSS Flexbox & Grid', 'description': 'Maîtrisez les layouts modernes avec Flexbox et CSS Grid.', 'resource_type': 'tutoriel', 'level': 'intermediaire', 'duration_minutes': 45, 'xp_reward': 35, 'order': 2,
                 'content': 'Flexbox et Grid sont les deux systèmes de layout CSS modernes.\n\n📐 Flexbox (1 dimension) :\n.container {\n  display: flex;\n  justify-content: center;\n  align-items: center;\n  gap: 16px;\n}\n\n📐 Grid (2 dimensions) :\n.grid {\n  display: grid;\n  grid-template-columns: repeat(3, 1fr);\n  gap: 20px;\n}\n\n🎯 Quand utiliser quoi ?\n- Flexbox : navigation, barres d\'outils, alignement simple\n- Grid : mises en page complexes, dashboards, galeries\n\n✅ Exercice : Créez une galerie responsive en CSS Grid.'},
                {'title': 'Documentation MDN - HTML', 'description': 'Référence complète HTML par Mozilla Developer Network.', 'resource_type': 'lien', 'level': 'debutant', 'duration_minutes': 0, 'xp_reward': 15, 'order': 3, 'url': 'https://developer.mozilla.org/fr/docs/Web/HTML'},
                {'title': 'Cours vidéo CSS complet', 'description': 'Apprenez CSS de zéro avec ce cours vidéo complet de 2h.', 'resource_type': 'video', 'level': 'debutant', 'duration_minutes': 120, 'xp_reward': 40, 'order': 4, 'url': 'https://www.youtube.com/embed/1PnVor36_40'},
                {'title': 'Exercice : Reproduire une maquette', 'description': 'Reproduisez fidèlement une maquette Figma en HTML/CSS pur.', 'resource_type': 'exercice', 'level': 'intermediaire', 'duration_minutes': 90, 'xp_reward': 50, 'order': 5,
                 'content': '🎯 Objectif : Reproduire la page d\'accueil de PathFinder en HTML/CSS.\n\n📋 Consignes :\n1. Créez un fichier index.html et style.css\n2. Reproduisez la navbar avec le logo et les liens\n3. Créez la section hero avec le titre et le bouton CTA\n4. Ajoutez la section "3 étapes" avec les cartes\n5. Rendez la page responsive (mobile-first)\n\n📏 Critères de notation :\n- Fidélité visuelle : 40%\n- Code propre et sémantique : 30%\n- Responsive design : 30%\n\n⏱️ Temps estimé : 90 minutes'},
            ],
            'javascript': [
                {'title': 'Variables et types de données', 'description': 'Découvrez let, const, types primitifs et objets JavaScript.', 'resource_type': 'tutoriel', 'level': 'debutant', 'duration_minutes': 25, 'xp_reward': 25, 'order': 1, 'is_free_preview': True,
                 'content': 'JavaScript utilise trois mots-clés pour déclarer des variables.\n\n🔑 Déclarations :\nconst nom = "Amadou"; // constante, ne change pas\nlet age = 22; // variable, peut changer\nvar ancien = true; // ancienne syntaxe, à éviter\n\n📊 Types primitifs :\n- string : "Bonjour"\n- number : 42, 3.14\n- boolean : true, false\n- null : absence de valeur\n- undefined : non défini\n\n📦 Objets :\nconst etudiant = {\n  nom: "Amadou",\n  filiere: "Informatique",\n  niveau: 3\n};\n\n✅ Exercice : Créez un objet représentant votre profil étudiant.'},
                {'title': 'Fonctions et DOM', 'description': 'Manipulez le DOM et créez des interactions utilisateur.', 'resource_type': 'tutoriel', 'level': 'intermediaire', 'duration_minutes': 40, 'xp_reward': 35, 'order': 2,
                 'content': 'Le DOM (Document Object Model) permet de manipuler les éléments HTML.\n\n🎯 Sélectionner des éléments :\nconst btn = document.querySelector(".btn-primary");\nconst items = document.querySelectorAll(".card");\n\n👆 Gérer les événements :\nbtn.addEventListener("click", () => {\n  alert("Bouton cliqué !");\n});\n\n🔄 Modifier le contenu :\nconst titre = document.getElementById("title");\ntitre.textContent = "Nouveau titre";\ntitre.style.color = "blue";\n\n✅ Exercice : Créez un compteur avec +/- et affichage dynamique.'},
                {'title': 'ES6+ : Arrow functions, destructuring', 'description': 'Les fonctionnalités modernes de JavaScript.', 'resource_type': 'tutoriel', 'level': 'avance', 'duration_minutes': 35, 'xp_reward': 40, 'order': 3,
                 'content': 'ES6 a introduit des syntaxes modernes essentielles.\n\n➡️ Arrow functions :\nconst add = (a, b) => a + b;\nconst greet = name => `Bonjour ${name} !`;\n\n📦 Destructuring :\nconst { nom, age } = etudiant;\nconst [premier, ...reste] = tableau;\n\n🔄 Spread operator :\nconst newArr = [...oldArr, newItem];\nconst newObj = { ...oldObj, key: newValue };\n\n⏳ Async/Await :\nconst fetchData = async () => {\n  const response = await fetch("/api/data");\n  const data = await response.json();\n  return data;\n};\n\n✅ Exercice : Refactorez du code ES5 en ES6+.'},
                {'title': 'Documentation JavaScript - MDN', 'description': 'Guide complet JavaScript par Mozilla.', 'resource_type': 'lien', 'level': 'debutant', 'duration_minutes': 0, 'xp_reward': 15, 'order': 4, 'url': 'https://developer.mozilla.org/fr/docs/Web/JavaScript/Guide'},
                {'title': 'Quiz : JavaScript avancé', 'description': 'Testez vos connaissances JavaScript avec ce quiz interactif.', 'resource_type': 'exercice', 'level': 'avance', 'duration_minutes': 30, 'xp_reward': 50, 'order': 5,
                 'content': '📝 Quiz JavaScript Avancé\n\n1. Quelle est la différence entre == et === ?\n2. Expliquez le concept de closure en JavaScript.\n3. Comment fonctionne le event loop ?\n4. Quelle est la différence entre Promise et async/await ?\n5. Expliquez le concept de prototype en JavaScript.\n\n🎯 Bonus : Écrivez une fonction qui déduplique un tableau.\nconst unique = (arr) => [...new Set(arr)];\n\n⏱️ Temps : 30 min maximum'},
            ],
            'python': [
                {'title': 'Python pour débutants', 'description': 'Premiers pas avec Python : syntaxe, variables, boucles.', 'resource_type': 'tutoriel', 'level': 'debutant', 'duration_minutes': 35, 'xp_reward': 25, 'order': 1, 'is_free_preview': True,
                 'content': 'Python est un langage simple, lisible et puissant.\n\n🐍 Variables :\nnom = "Amadou"\nage = 22\nis_student = True\n\n🔁 Boucles :\nfor i in range(5):\n    print(f"Itération {i}")\n\nnotes = [14, 16, 12, 18]\nfor note in notes:\n    if note >= 15:\n        print(f"{note} : Bien !")\n\n📦 Fonctions :\ndef calculer_moyenne(notes):\n    return sum(notes) / len(notes)\n\nmoyenne = calculer_moyenne([14, 16, 12, 18])\nprint(f"Moyenne : {moyenne}")\n\n✅ Exercice : Créez un programme qui calcule si un étudiant est admis (moyenne >= 10).'},
                {'title': 'Django — Créer une app web', 'description': 'Construisez votre première application web avec Django.', 'resource_type': 'tutoriel', 'level': 'intermediaire', 'duration_minutes': 60, 'xp_reward': 40, 'order': 2,
                 'content': 'Django est le framework web Python le plus populaire.\n\n🚀 Créer un projet :\npip install django\ndjango-admin startproject monprojet\ncd monprojet\npython manage.py startapp blog\n\n📄 Modèle (models.py) :\nclass Article(models.Model):\n    titre = models.CharField(max_length=200)\n    contenu = models.TextField()\n    date = models.DateTimeField(auto_now_add=True)\n\n🌐 Vue (views.py) :\ndef article_list(request):\n    articles = Article.objects.all()\n    return render(request, "blog/list.html", {"articles": articles})\n\n🔗 URL (urls.py) :\nurlpatterns = [\n    path("articles/", views.article_list, name="article_list"),\n]\n\n✅ Exercice : Créez un blog avec liste et détail d\'articles.'},
                {'title': 'Documentation Django officielle', 'description': 'La documentation officielle Django en français.', 'resource_type': 'lien', 'level': 'intermediaire', 'duration_minutes': 0, 'xp_reward': 15, 'order': 3, 'url': 'https://docs.djangoproject.com/fr/5.0/'},
                {'title': 'Cours vidéo Python complet', 'description': 'Formation Python complète en vidéo.', 'resource_type': 'video', 'level': 'debutant', 'duration_minutes': 180, 'xp_reward': 50, 'order': 4, 'url': 'https://www.youtube.com/embed/HWxBtxPBCAc'},
                {'title': 'Projet : API REST avec Django', 'description': 'Créez une API RESTful complète avec Django REST Framework.', 'resource_type': 'exercice', 'level': 'avance', 'duration_minutes': 120, 'xp_reward': 60, 'order': 5,
                 'content': '🎯 Projet : API REST Gestion d\'étudiants\n\n📋 Objectif :\nCréer une API REST complète avec Django REST Framework.\n\n🛠️ Étapes :\n1. Installer DRF : pip install djangorestframework\n2. Créer le modèle Etudiant (nom, filiere, moyenne)\n3. Créer le Serializer\n4. Créer les ViewSets (CRUD complet)\n5. Configurer le Router\n6. Tester avec Postman ou curl\n\n📐 Endpoints attendus :\nGET    /api/etudiants/       → Liste\nPOST   /api/etudiants/       → Créer\nGET    /api/etudiants/{id}/   → Détail\nPUT    /api/etudiants/{id}/   → Modifier\nDELETE /api/etudiants/{id}/   → Supprimer\n\n⏱️ Temps estimé : 2 heures'},
            ],
            'react': [
                {'title': 'React : Premiers composants', 'description': 'Créez vos premiers composants React avec JSX.', 'resource_type': 'tutoriel', 'level': 'debutant', 'duration_minutes': 40, 'xp_reward': 30, 'order': 1, 'is_free_preview': True,
                 'content': 'React est une librairie JavaScript pour créer des interfaces.\n\n⚛️ Composant fonctionnel :\nfunction Bonjour({ nom }) {\n  return <h1>Bonjour {nom} !</h1>;\n}\n\n🎯 Utilisation :\n<Bonjour nom="Amadou" />\n\n🔄 State avec useState :\nimport { useState } from "react";\n\nfunction Compteur() {\n  const [count, setCount] = useState(0);\n  return (\n    <div>\n      <p>Compteur : {count}</p>\n      <button onClick={() => setCount(count + 1)}>+1</button>\n    </div>\n  );\n}\n\n✅ Exercice : Créez un composant "Card" réutilisable avec props.'},
                {'title': 'Hooks avancés (useEffect, useContext)', 'description': 'Maîtrisez les hooks React pour gérer l\'état et les effets.', 'resource_type': 'tutoriel', 'level': 'avance', 'duration_minutes': 50, 'xp_reward': 45, 'order': 2,
                 'content': 'Les hooks permettent d\'utiliser les fonctionnalités React sans classes.\n\n🔄 useEffect :\nuseEffect(() => {\n  fetch("/api/data")\n    .then(res => res.json())\n    .then(data => setData(data));\n}, []); // [] = exécuté une seule fois\n\n🌐 useContext :\nconst ThemeContext = createContext("light");\n\nfunction App() {\n  return (\n    <ThemeContext.Provider value="dark">\n      <MonComposant />\n    </ThemeContext.Provider>\n  );\n}\n\nfunction MonComposant() {\n  const theme = useContext(ThemeContext);\n  return <p>Thème : {theme}</p>;\n}'},
                {'title': 'Documentation React officielle', 'description': 'Apprenez React avec la documentation officielle.', 'resource_type': 'lien', 'level': 'debutant', 'duration_minutes': 0, 'xp_reward': 15, 'order': 3, 'url': 'https://react.dev/learn'},
                {'title': 'Cours vidéo React', 'description': 'Formation React complète en vidéo.', 'resource_type': 'video', 'level': 'intermediaire', 'duration_minutes': 150, 'xp_reward': 45, 'order': 4, 'url': 'https://www.youtube.com/embed/Tn6-PIqc4UM'},
                {'title': 'Projet : Dashboard React', 'description': 'Construisez un dashboard interactif avec React et Chart.js.', 'resource_type': 'exercice', 'level': 'avance', 'duration_minutes': 150, 'xp_reward': 60, 'order': 5,
                 'content': '🎯 Projet : Dashboard étudiant\n\nCréez un dashboard React avec :\n- Composant Header avec navigation\n- Carte statistiques (nombre d\'étudiants, moyenne)\n- Graphique Chart.js (barres des notes)\n- Liste filtrable d\'étudiants\n- Formulaire d\'ajout\n\n⏱️ Temps : 2h30'},
            ],
            'database': [
                {'title': 'SQL pour débutants', 'description': 'Les requêtes SQL essentielles : SELECT, INSERT, UPDATE, DELETE.', 'resource_type': 'tutoriel', 'level': 'debutant', 'duration_minutes': 40, 'xp_reward': 30, 'order': 1, 'is_free_preview': True,
                 'content': 'SQL est le langage de gestion des bases de données.\n\n📊 SELECT :\nSELECT nom, filiere FROM etudiants WHERE moyenne >= 12 ORDER BY nom;\n\n➕ INSERT :\nINSERT INTO etudiants (nom, filiere, moyenne) VALUES ("Amadou", "Info", 15.5);\n\n✏️ UPDATE :\nUPDATE etudiants SET moyenne = 16.0 WHERE nom = "Amadou";\n\n🗑️ DELETE :\nDELETE FROM etudiants WHERE moyenne < 8;\n\n🔗 JOIN :\nSELECT e.nom, c.nom FROM etudiants e JOIN cours c ON e.cours_id = c.id;'},
                {'title': 'PostgreSQL avancé', 'description': 'Index, transactions, vues, procédures stockées.', 'resource_type': 'tutoriel', 'level': 'avance', 'duration_minutes': 60, 'xp_reward': 45, 'order': 2,
                 'content': 'PostgreSQL offre des fonctionnalités avancées.\n\n📊 Index :\nCREATE INDEX idx_nom ON etudiants(nom);\n\n🔒 Transactions :\nBEGIN;\nUPDATE comptes SET solde = solde - 1000 WHERE id = 1;\nUPDATE comptes SET solde = solde + 1000 WHERE id = 2;\nCOMMIT;\n\n👁️ Vues :\nCREATE VIEW top_etudiants AS\nSELECT nom, moyenne FROM etudiants WHERE moyenne >= 15;'},
                {'title': 'Documentation PostgreSQL', 'description': 'Documentation officielle PostgreSQL.', 'resource_type': 'lien', 'level': 'intermediaire', 'duration_minutes': 0, 'xp_reward': 15, 'order': 3, 'url': 'https://www.postgresql.org/docs/'},
                {'title': 'ORM Django — Requêtes avancées', 'description': 'Maîtrisez les QuerySets Django.', 'resource_type': 'tutoriel', 'level': 'intermediaire', 'duration_minutes': 45, 'xp_reward': 35, 'order': 4,
                 'content': 'L\'ORM Django traduit Python en SQL.\n\n🔍 QuerySets :\nEtudiant.objects.filter(filiere="informatique", moyenne__gte=12)\nEtudiant.objects.exclude(niveau="licence1")\nEtudiant.objects.order_by("-moyenne")[:10]\n\n📊 Agrégations :\nfrom django.db.models import Avg, Count, Max\nEtudiant.objects.aggregate(moy=Avg("moyenne"), total=Count("id"))'},
                {'title': 'Modélisation : schéma E-R', 'description': 'Concevez un schéma entité-relation complet.', 'resource_type': 'exercice', 'level': 'intermediaire', 'duration_minutes': 60, 'xp_reward': 40, 'order': 5,
                 'content': '🎯 Exercice : Modélisez la base PathFinder\n\nCréez le schéma E-R avec :\n- Utilisateur (nom, email, filière, xp)\n- Compétence (nom, niveau_max, premium)\n- Parcours (titre, description)\n- Étape (titre, ordre, prix)\n- Progression (user, compétence, %)\n\nRelations à définir, cardinalités, clés primaires et étrangères.'},
            ],
            'devops': [
                {'title': 'Git & GitHub essentiels', 'description': 'Maîtrisez le versioning avec Git et la collaboration GitHub.', 'resource_type': 'tutoriel', 'level': 'debutant', 'duration_minutes': 35, 'xp_reward': 25, 'order': 1, 'is_free_preview': True,
                 'content': 'Git est l\'outil de versioning standard.\n\n📦 Commandes essentielles :\ngit init\ngit add .\ngit commit -m "Premier commit"\ngit push origin main\n\n🌿 Branches :\ngit checkout -b feature/login\ngit merge feature/login\n\n🤝 Collaboration :\ngit clone https://github.com/user/repo.git\ngit pull origin main\ngit push origin feature\n\n✅ Créez un repo GitHub et pushez un projet.'},
                {'title': 'Docker pour développeurs', 'description': 'Conteneurisez vos applications avec Docker.', 'resource_type': 'tutoriel', 'level': 'intermediaire', 'duration_minutes': 50, 'xp_reward': 40, 'order': 2,
                 'content': 'Docker permet d\'isoler vos applications.\n\n🐳 Dockerfile :\nFROM python:3.11\nWORKDIR /app\nCOPY requirements.txt .\nRUN pip install -r requirements.txt\nCOPY . .\nCMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]\n\n📦 Docker Compose :\nversion: "3"\nservices:\n  web:\n    build: .\n    ports: ["8000:8000"]\n  db:\n    image: postgres:15\n    environment:\n      POSTGRES_DB: pathfinder'},
                {'title': 'CI/CD avec GitHub Actions', 'description': 'Automatisez vos tests et déploiements.', 'resource_type': 'tutoriel', 'level': 'avance', 'duration_minutes': 45, 'xp_reward': 45, 'order': 3,
                 'content': 'GitHub Actions automatise votre workflow.\n\n⚙️ .github/workflows/ci.yml :\nname: CI\non: [push, pull_request]\njobs:\n  test:\n    runs-on: ubuntu-latest\n    steps:\n      - uses: actions/checkout@v4\n      - uses: actions/setup-python@v5\n      - run: pip install -r requirements.txt\n      - run: python manage.py test'},
                {'title': 'Documentation Docker', 'description': 'Documentation officielle Docker.', 'resource_type': 'lien', 'level': 'intermediaire', 'duration_minutes': 0, 'xp_reward': 15, 'order': 4, 'url': 'https://docs.docker.com/get-started/'},
                {'title': 'Déployer sur Railway/Render', 'description': 'Déployez votre app Django gratuitement.', 'resource_type': 'exercice', 'level': 'avance', 'duration_minutes': 60, 'xp_reward': 50, 'order': 5,
                 'content': '🎯 Déployez PathFinder sur Render.com\n\n1. Créez un compte Render (gratuit)\n2. Connectez votre repo GitHub\n3. Configurez les variables d\'environnement\n4. Ajoutez un Procfile : web: gunicorn finder.wsgi\n5. Configurez la base PostgreSQL\n6. Déployez et testez !'},
            ],
        }
        for res_data in resources_map.get(skill.slug, []):
            SkillResource.objects.create(skill=skill, **res_data)

    def _create_careers(self):
        from parcours.models import CareerPath, CareerStep
        from competences.models import Skill

        careers = [
            {
                'slug': 'fullstack', 'title': 'Développeur Full Stack', 'icon': '💻',
                'description': 'Maîtrisez le développement web de A à Z : frontend, backend, bases de données et déploiement.',
                'tags': ['Informatique', 'Web', 'Développement'],
                'skills': ['html-css', 'javascript', 'python', 'react', 'database', 'devops'],
                'steps': [
                    {'order': 1, 'title': 'Découvrir votre profil', 'description': 'Identifiez vos forces et vos affinités avec le développement web.', 'is_free': True, 'price_fcfa': 0, 'icon': '🔍', 'features': ['Test de profil', 'Analyse IA']},
                    {'order': 2, 'title': 'Bases de la programmation', 'description': 'Apprentissage de HTML, CSS et des fondamentaux de JavaScript.', 'is_free': True, 'price_fcfa': 0, 'icon': '📘', 'features': ['Cours vidéo 8h', '5 exercices']},
                    {'order': 3, 'title': 'Développement Frontend', 'description': 'Maîtrisez React, Tailwind CSS et créez des interfaces dynamiques.', 'is_free': False, 'price_fcfa': 500, 'icon': '🎨', 'features': ['Cours vidéo 10h', '6 projets']},
                    {'order': 4, 'title': 'Développement Backend', 'description': 'Node.js, bases de données et APIs REST.', 'is_free': False, 'price_fcfa': 1000, 'icon': '⚙️', 'features': ['Cours vidéo 12h', '8 projets', 'Certificat']},
                    {'order': 5, 'title': 'Bases de données avancées', 'description': 'PostgreSQL, MongoDB, optimisation des requêtes.', 'is_free': False, 'price_fcfa': 1500, 'icon': '🗄️', 'features': ['Cours vidéo 8h', '4 projets']},
                    {'order': 6, 'title': 'Stage en entreprise', 'description': 'Immersion professionnelle de 2 semaines.', 'is_free': False, 'price_fcfa': 2500, 'icon': '🏢', 'features': ['Mise en relation', 'Suivi mentor']},
                    {'order': 7, 'title': 'Spécialisation Full Stack', 'description': 'Expertise approfondie sur les technologies frontend et backend modernes.', 'is_free': False, 'price_fcfa': 3500, 'icon': '🎯', 'features': ['Projet complet', 'Portfolio']},
                    {'order': 8, 'title': 'Insertion professionnelle', 'description': 'Coaching CV, préparation aux entretiens et mise en relation avec nos partenaires.', 'is_free': False, 'is_premium': True, 'price_fcfa': 5000, 'icon': '🏆', 'features': ['CV coaching', 'Entretiens simulés', 'Réseau partenaires']},
                ],
            },
            {
                'slug': 'chef_projet', 'title': 'Chef de projet digital', 'icon': '📋',
                'description': 'Apprenez à gérer des projets numériques de bout en bout avec les méthodologies agiles.',
                'tags': ['Management', 'Digital', 'Agile'],
                'skills': ['html-css', 'javascript'],
                'steps': [
                    {'order': 1, 'title': 'Fondamentaux du digital', 'description': 'Comprendre l\'écosystème numérique.', 'is_free': True, 'price_fcfa': 0, 'icon': '📘'},
                    {'order': 2, 'title': 'Méthodologies agiles', 'description': 'Scrum, Kanban, sprints.', 'is_free': True, 'price_fcfa': 0, 'icon': '🔄'},
                    {'order': 3, 'title': 'Gestion d\'équipe', 'description': 'Leadership et communication.', 'is_free': False, 'price_fcfa': 500, 'icon': '👥'},
                    {'order': 4, 'title': 'Outils de projet', 'description': 'Jira, Trello, Notion, Git.', 'is_free': False, 'price_fcfa': 1000, 'icon': '🛠️'},
                    {'order': 5, 'title': 'Budget & planning', 'description': 'Gestion financière de projet.', 'is_free': False, 'price_fcfa': 1500, 'icon': '💰'},
                    {'order': 6, 'title': 'UX/UI Design', 'description': 'Principes de design centré utilisateur.', 'is_free': False, 'price_fcfa': 2000, 'icon': '🎨'},
                    {'order': 7, 'title': 'Certification PMI', 'description': 'Préparation à la certification.', 'is_free': False, 'price_fcfa': 3000, 'icon': '📜'},
                    {'order': 8, 'title': 'Insertion pro', 'description': 'Coaching et mise en relation.', 'is_free': False, 'is_premium': True, 'price_fcfa': 5000, 'icon': '🏆'},
                ],
            },
            {
                'slug': 'data_analyst', 'title': 'Data Analyst', 'icon': '📊',
                'description': 'Transformez les données en insights stratégiques avec Python, SQL et la visualisation.',
                'tags': ['Data', 'Analyse', 'IA'],
                'skills': ['python', 'database'],
                'steps': [
                    {'order': 1, 'title': 'Intro à la data', 'description': 'Comprendre le monde des données.', 'is_free': True, 'price_fcfa': 0, 'icon': '📘'},
                    {'order': 2, 'title': 'Python pour la data', 'description': 'NumPy, Pandas, Matplotlib.', 'is_free': True, 'price_fcfa': 0, 'icon': '🐍'},
                    {'order': 3, 'title': 'SQL avancé', 'description': 'Requêtes complexes, jointures.', 'is_free': False, 'price_fcfa': 500, 'icon': '🗄️'},
                    {'order': 4, 'title': 'Visualisation', 'description': 'Power BI, Tableau, Plotly.', 'is_free': False, 'price_fcfa': 1000, 'icon': '📈'},
                    {'order': 5, 'title': 'Machine Learning', 'description': 'Modèles prédictifs avec Scikit-learn.', 'is_free': False, 'price_fcfa': 2000, 'icon': '🤖'},
                    {'order': 6, 'title': 'Big Data', 'description': 'Spark, Hadoop, data lakes.', 'is_free': False, 'price_fcfa': 2500, 'icon': '☁️'},
                    {'order': 7, 'title': 'Projet data réel', 'description': 'Analyse complète sur données réelles.', 'is_free': False, 'price_fcfa': 3000, 'icon': '🎯'},
                    {'order': 8, 'title': 'Insertion pro Data', 'description': 'Portfolio et entretiens techniques.', 'is_free': False, 'is_premium': True, 'price_fcfa': 5000, 'icon': '🏆'},
                ],
            },
        ]

        for cd in careers:
            career, created = CareerPath.objects.get_or_create(
                slug=cd['slug'],
                defaults={'title': cd['title'], 'description': cd['description'], 'tags': cd['tags'], 'icon': cd['icon']}
            )
            if created:
                # Ajouter les skills M2M
                for skill_slug in cd.get('skills', []):
                    try:
                        skill = Skill.objects.get(slug=skill_slug)
                        career.skills.add(skill)
                    except Skill.DoesNotExist:
                        pass

                # Créer les étapes
                for sd in cd['steps']:
                    CareerStep.objects.create(career=career, **sd)
                self.stdout.write(f'  ✓ Carrière: {career.title} ({career.steps.count()} étapes)')

    def _create_questions(self):
        from orientation.models import OrientationQuestion, OrientationChoice
        questions = [
            {
                'text': 'Qu\'est-ce qui vous passionne le plus ?', 'order': 1, 'category': 'interest', 'icon': '💡',
                'choices': [
                    {'text': 'Créer des interfaces visuelles', 'icon': '🎨', 'weights': {'fullstack': 3, 'chef_projet': 1, 'data_analyst': 0}},
                    {'text': 'Résoudre des problèmes logiques', 'icon': '🧩', 'weights': {'fullstack': 2, 'chef_projet': 0, 'data_analyst': 3}},
                    {'text': 'Organiser et coordonner des équipes', 'icon': '👥', 'weights': {'fullstack': 0, 'chef_projet': 3, 'data_analyst': 1}},
                    {'text': 'Analyser des données et des tendances', 'icon': '📊', 'weights': {'fullstack': 1, 'chef_projet': 1, 'data_analyst': 3}},
                ],
            },
            {
                'text': 'Comment préférez-vous travailler ?', 'order': 2, 'category': 'workstyle', 'icon': '🏢',
                'choices': [
                    {'text': 'Seul, avec du code', 'icon': '💻', 'weights': {'fullstack': 3, 'chef_projet': 0, 'data_analyst': 2}},
                    {'text': 'En équipe, en collaboration', 'icon': '🤝', 'weights': {'fullstack': 1, 'chef_projet': 3, 'data_analyst': 1}},
                    {'text': 'Avec des données et des tableaux', 'icon': '📋', 'weights': {'fullstack': 0, 'chef_projet': 1, 'data_analyst': 3}},
                    {'text': 'En alternant technique et gestion', 'icon': '🔄', 'weights': {'fullstack': 2, 'chef_projet': 2, 'data_analyst': 1}},
                ],
            },
            {
                'text': 'Quel est votre objectif principal ?', 'order': 3, 'category': 'goal', 'icon': '🎯',
                'choices': [
                    {'text': 'Devenir développeur dans une startup', 'icon': '🚀', 'weights': {'fullstack': 3, 'chef_projet': 1, 'data_analyst': 0}},
                    {'text': 'Diriger des projets tech', 'icon': '📋', 'weights': {'fullstack': 1, 'chef_projet': 3, 'data_analyst': 0}},
                    {'text': 'Travailler dans la data science', 'icon': '🔬', 'weights': {'fullstack': 0, 'chef_projet': 0, 'data_analyst': 3}},
                    {'text': 'Lancer ma propre entreprise tech', 'icon': '💼', 'weights': {'fullstack': 2, 'chef_projet': 2, 'data_analyst': 2}},
                ],
            },
            {
                'text': 'Quelle matière préférez-vous ?', 'order': 4, 'category': 'interest', 'icon': '📚',
                'choices': [
                    {'text': 'Programmation / Algorithmique', 'icon': '🖥️', 'weights': {'fullstack': 3, 'chef_projet': 0, 'data_analyst': 2}},
                    {'text': 'Mathématiques / Statistiques', 'icon': '📐', 'weights': {'fullstack': 0, 'chef_projet': 0, 'data_analyst': 3}},
                    {'text': 'Gestion / Management', 'icon': '📊', 'weights': {'fullstack': 0, 'chef_projet': 3, 'data_analyst': 1}},
                    {'text': 'Design / Communication', 'icon': '🎨', 'weights': {'fullstack': 2, 'chef_projet': 2, 'data_analyst': 0}},
                ],
            },
            {
                'text': 'Comment gérez-vous les deadlines ?', 'order': 5, 'category': 'workstyle', 'icon': '⏰',
                'choices': [
                    {'text': 'Je code jusqu\'à ce que ce soit parfait', 'icon': '🔧', 'weights': {'fullstack': 3, 'chef_projet': 0, 'data_analyst': 1}},
                    {'text': 'Je planifie et délègue efficacement', 'icon': '📅', 'weights': {'fullstack': 0, 'chef_projet': 3, 'data_analyst': 1}},
                    {'text': 'J\'analyse les priorités avec des données', 'icon': '📈', 'weights': {'fullstack': 0, 'chef_projet': 1, 'data_analyst': 3}},
                    {'text': 'Je m\'adapte selon la situation', 'icon': '🔄', 'weights': {'fullstack': 2, 'chef_projet': 2, 'data_analyst': 1}},
                ],
            },
            {
                'text': 'Quel outil vous attire le plus ?', 'order': 6, 'category': 'skill', 'icon': '🛠️',
                'choices': [
                    {'text': 'VS Code / Terminal', 'icon': '💻', 'weights': {'fullstack': 3, 'chef_projet': 0, 'data_analyst': 1}},
                    {'text': 'Jira / Trello / Notion', 'icon': '📋', 'weights': {'fullstack': 0, 'chef_projet': 3, 'data_analyst': 0}},
                    {'text': 'Jupyter Notebook / Excel avancé', 'icon': '📊', 'weights': {'fullstack': 0, 'chef_projet': 0, 'data_analyst': 3}},
                    {'text': 'Figma / Canva', 'icon': '🎨', 'weights': {'fullstack': 2, 'chef_projet': 2, 'data_analyst': 0}},
                ],
            },
            {
                'text': 'Quel type de projet vous motive ?', 'order': 7, 'category': 'goal', 'icon': '🏗️',
                'choices': [
                    {'text': 'Développer une application web complète', 'icon': '🌐', 'weights': {'fullstack': 3, 'chef_projet': 1, 'data_analyst': 0}},
                    {'text': 'Gérer le lancement d\'un produit', 'icon': '🚀', 'weights': {'fullstack': 0, 'chef_projet': 3, 'data_analyst': 0}},
                    {'text': 'Créer un dashboard d\'analyse', 'icon': '📈', 'weights': {'fullstack': 1, 'chef_projet': 0, 'data_analyst': 3}},
                    {'text': 'Automatiser des processus', 'icon': '⚙️', 'weights': {'fullstack': 2, 'chef_projet': 1, 'data_analyst': 2}},
                ],
            },
            {
                'text': 'Quelle compétence voulez-vous développer en priorité ?', 'order': 8, 'category': 'skill', 'icon': '💪',
                'choices': [
                    {'text': 'React / Vue.js', 'icon': '⚛️', 'weights': {'fullstack': 3, 'chef_projet': 0, 'data_analyst': 0}},
                    {'text': 'Leadership & communication', 'icon': '🗣️', 'weights': {'fullstack': 0, 'chef_projet': 3, 'data_analyst': 0}},
                    {'text': 'Python / Machine Learning', 'icon': '🐍', 'weights': {'fullstack': 1, 'chef_projet': 0, 'data_analyst': 3}},
                    {'text': 'Architecture & DevOps', 'icon': '🏛️', 'weights': {'fullstack': 2, 'chef_projet': 2, 'data_analyst': 1}},
                ],
            },
            {
                'text': 'Comment vous décrivent vos amis ?', 'order': 9, 'category': 'workstyle', 'icon': '🪞',
                'choices': [
                    {'text': 'Créatif et technique', 'icon': '🎭', 'weights': {'fullstack': 3, 'chef_projet': 0, 'data_analyst': 1}},
                    {'text': 'Organisé et leader', 'icon': '👑', 'weights': {'fullstack': 0, 'chef_projet': 3, 'data_analyst': 0}},
                    {'text': 'Analytique et curieux', 'icon': '🔍', 'weights': {'fullstack': 0, 'chef_projet': 0, 'data_analyst': 3}},
                    {'text': 'Polyvalent et adaptable', 'icon': '🌟', 'weights': {'fullstack': 2, 'chef_projet': 2, 'data_analyst': 2}},
                ],
            },
            {
                'text': 'Où vous voyez-vous dans 5 ans ?', 'order': 10, 'category': 'goal', 'icon': '🔮',
                'choices': [
                    {'text': 'Tech lead dans une entreprise innovante', 'icon': '💼', 'weights': {'fullstack': 3, 'chef_projet': 1, 'data_analyst': 0}},
                    {'text': 'Directeur de projet / Product Manager', 'icon': '📊', 'weights': {'fullstack': 0, 'chef_projet': 3, 'data_analyst': 1}},
                    {'text': 'Data scientist / ingénieur IA', 'icon': '🤖', 'weights': {'fullstack': 0, 'chef_projet': 0, 'data_analyst': 3}},
                    {'text': 'Entrepreneur tech / freelance', 'icon': '🚀', 'weights': {'fullstack': 2, 'chef_projet': 2, 'data_analyst': 2}},
                ],
            },
        ]
        if not OrientationQuestion.objects.exists():
            for qd in questions:
                choices = qd.pop('choices')
                q = OrientationQuestion.objects.create(**qd)
                for cd in choices:
                    OrientationChoice.objects.create(question=q, **cd)
                self.stdout.write(f'  ✓ Question {q.order}: {q.text[:40]}...')

    def _create_badges(self):
        from gamification.models import Badge
        badges = [
            {'slug': 'first-steps', 'name': 'Premiers pas', 'description': 'Inscription complétée', 'icon': '🌱', 'category': 'progression', 'condition_type': 'xp_total', 'condition_value': 50},
            {'slug': 'orientation-done', 'name': 'Orienté', 'description': 'Test d\'orientation complété', 'icon': '🧭', 'category': 'progression', 'condition_type': 'test_complete', 'condition_value': 1},
            {'slug': 'level-3', 'name': 'Pratiquant', 'description': 'Niveau 3 atteint', 'icon': '⚡', 'category': 'progression', 'condition_type': 'level_reached', 'condition_value': 3},
            {'slug': 'level-5', 'name': 'Expert', 'description': 'Niveau 5 atteint', 'icon': '🏆', 'category': 'excellence', 'condition_type': 'level_reached', 'condition_value': 5},
            {'slug': 'first-payment', 'name': 'Investisseur', 'description': 'Premier paiement effectué', 'icon': '💳', 'category': 'special', 'condition_type': 'payment_made', 'condition_value': 1},
            {'slug': 'streak-7', 'name': 'Régulier', 'description': '7 jours consécutifs de connexion', 'icon': '🔥', 'category': 'regularite', 'condition_type': 'streak_days', 'condition_value': 7},
            {'slug': 'skills-3', 'name': 'Compétent', 'description': '3 compétences débloquées', 'icon': '💡', 'category': 'progression', 'condition_type': 'skills_unlocked', 'condition_value': 3},
        ]
        for bd in badges:
            Badge.objects.get_or_create(slug=bd['slug'], defaults=bd)
        self.stdout.write(f'  ✓ {len(badges)} badges créés')

    def _create_boosters(self):
        from gamification.models import Booster
        boosters = [
            {'slug': 'xp-boost', 'name': 'Boost XP ×2', 'description': 'Double l\'XP gagné par vos actions pendant 7 jours.', 'icon': '⚡', 'booster_type': 'xp_multiplier', 'price_fcfa': 500, 'duration_days': 7, 'multiplier': 2.0},
            {'slug': 'ai-analysis', 'name': 'Analyse IA Pro', 'description': 'Rapport d\'orientation détaillé avec IA avancée.', 'icon': '🤖', 'booster_type': 'ai_analysis', 'price_fcfa': 1000, 'duration_days': 0, 'multiplier': 1.0},
            {'slug': 'pack-competences', 'name': 'Pack Compétences', 'description': 'Débloque 1 compétence premium de votre choix.', 'icon': '💡', 'booster_type': 'pack_competences', 'price_fcfa': 1500, 'duration_days': 0, 'multiplier': 1.0},
            {'slug': 'theme-gold', 'name': 'Thème Gold', 'description': 'Personnalisation visuelle premium de votre profil.', 'icon': '✨', 'booster_type': 'theme', 'price_fcfa': 500, 'duration_days': 0, 'multiplier': 1.0},
            {'slug': 'pack-ambassadeur', 'name': 'Pack Ambassadeur', 'description': 'Boost XP ×2 + Analyse IA + Badge exclusif.', 'icon': '👑', 'booster_type': 'pack_ambassadeur', 'price_fcfa': 2000, 'duration_days': 30, 'multiplier': 2.0},
        ]
        for bd in boosters:
            Booster.objects.get_or_create(slug=bd['slug'], defaults=bd)
        self.stdout.write(f'  ✓ {len(boosters)} boosters créés')

    def _create_challenges(self):
        from gamification.models import Challenge
        today = timezone.now().date()
        challenges = [
            {'title': 'Complétez 2 étapes cette semaine', 'description': 'Progressez dans votre parcours en terminant 2 étapes du curriculum.', 'xp_reward': 200, 'start_date': today, 'end_date': today + timedelta(days=7)},
            {'title': 'Lisez 3 articles du blog', 'description': 'Informez-vous sur les carrières et compétences du numérique.', 'xp_reward': 150, 'start_date': today, 'end_date': today + timedelta(days=7)},
        ]
        if not Challenge.objects.exists():
            for cd in challenges:
                Challenge.objects.create(**cd)
            self.stdout.write(f'  ✓ {len(challenges)} défis créés')

    def _create_blog(self):
        from blog.models import Category, BlogPost
        from accounts.models import CustomUser

        cat, _ = Category.objects.get_or_create(slug='carrieres', defaults={'name': 'Carrières'})
        cat2, _ = Category.objects.get_or_create(slug='competences', defaults={'name': 'Compétences'})
        cat3, _ = Category.objects.get_or_create(slug='conseils', defaults={'name': 'Conseils'})

        admin = CustomUser.objects.filter(is_superuser=True).first()

        posts = [
            {'title': 'Les 5 métiers tech les plus demandés en 2025', 'slug': 'metiers-tech-2025', 'category': cat, 'excerpt': 'Découvrez les carrières qui recrutent le plus dans le numérique en Afrique.', 'content': 'Le secteur tech en Afrique connaît une croissance fulgurante...', 'published': True},
            {'title': 'Comment réussir son premier entretien tech', 'slug': 'reussir-entretien-tech', 'category': cat3, 'excerpt': 'Nos conseils pour impressionner les recruteurs.', 'content': 'La préparation est la clé du succès...', 'published': True},
            {'title': 'Python vs JavaScript : lequel apprendre en premier ?', 'slug': 'python-vs-javascript', 'category': cat2, 'excerpt': 'Comparaison des deux langages les plus populaires.', 'content': 'Les deux langages ont leurs forces...', 'published': True},
            {'title': 'Construire son portfolio développeur', 'slug': 'portfolio-dev', 'category': cat3, 'excerpt': 'Le portfolio est votre meilleur CV.', 'content': 'Un bon portfolio montre vos compétences réelles...', 'published': True},
            {'title': 'L\'IA au service de l\'orientation professionnelle', 'slug': 'ia-orientation', 'category': cat, 'excerpt': 'Comment l\'intelligence artificielle peut guider votre carrière.', 'content': 'Les algorithmes d\'orientation analysent...', 'published': True},
        ]
        if not BlogPost.objects.exists():
            for pd in posts:
                BlogPost.objects.create(author=admin, **pd)
            self.stdout.write(f'  ✓ {len(posts)} articles créés')

    def _create_demo_user(self):
        from accounts.models import CustomUser
        from payments.models import UserProgress
        from orientation.models import OrientationResult
        from parcours.models import CareerPath
        from competences.models import UserSkillProgress, Skill
        from gamification.models import UserBadge, Badge, XPEvent

        if CustomUser.objects.filter(username='amadou').exists():
            self.stdout.write('  → Utilisateur démo existe déjà')
            return

        user = CustomUser.objects.create_user(
            username='amadou', password='pathfinder2025',
            first_name='Amadou', last_name='Diallo',
            email='amadou.diallo@univ-douala.cm',
            filiere='informatique', niveau='licence3',
            avatar_initials='AD', total_xp=450, level=3,
            global_progress=35.0,
        )

        # UserProgress
        progress = UserProgress.objects.create(user=user, global_percent=35.0)

        # Orientation result
        career = CareerPath.objects.filter(slug='fullstack').first()
        if career:
            steps = career.steps.all().order_by('order')
            # Marquer les 2 premières étapes comme complétées
            for step in steps[:2]:
                progress.completed_steps.add(step)
                progress.unlocked_steps.add(step)
            # Débloquer la 3e étape
            if steps.count() > 2:
                progress.unlocked_steps.add(steps[2])

            OrientationResult.objects.create(
                user=user,
                scores={'fullstack': 92, 'chef_projet': 78, 'data_analyst': 65},
                recommended_career=career,
                summary='D\'après l\'analyse de vos réponses, votre profil correspond à 92% au métier de Développeur Full Stack. C\'est une excellente correspondance !',
                career_projection_3y='📅 Année 1 : Formation intensive...\n📅 Année 2 : Spécialisation...\n📅 Année 3 : Insertion professionnelle.',
                priority_skills=[{'name': 'HTML & CSS', 'slug': 'html-css', 'icon': '🎨'}, {'name': 'JavaScript', 'slug': 'javascript', 'icon': '⚡'}],
            )

        # Skill progress
        for skill in Skill.objects.filter(is_premium=False):
            UserSkillProgress.objects.create(user=user, skill=skill, current_level=2, progress_percent=65.0, unlocked=True)

        # Badges
        for slug in ['first-steps', 'orientation-done']:
            badge = Badge.objects.filter(slug=slug).first()
            if badge:
                UserBadge.objects.create(user=user, badge=badge)

        # XP history
        XPEvent.objects.create(user=user, action='inscription_complete', xp_earned=50)
        XPEvent.objects.create(user=user, action='test_orientation_complete', xp_earned=100)
        XPEvent.objects.create(user=user, action='etape_completee:Découvrir votre profil', xp_earned=75)
        XPEvent.objects.create(user=user, action='etape_completee:Bases de la programmation', xp_earned=75)

        self.stdout.write(f'  ✓ Utilisateur démo: amadou / pathfinder2025 (450 XP, niveau 3)')

        # Créer des utilisateurs pour le classement
        self._create_leaderboard_users()

    def _create_leaderboard_users(self):
        from accounts.models import CustomUser
        from gamification.models import XPEvent, Badge, UserBadge

        leaderboard_users = [
            {'username': 'fatou', 'first_name': 'Fatou', 'last_name': 'Mbarga', 'email': 'fatou@univ-yaounde.cm', 'filiere': 'informatique', 'niveau': 'master1', 'total_xp': 820, 'level': 5},
            {'username': 'jean', 'first_name': 'Jean', 'last_name': 'Nkoulou', 'email': 'jean@univ-douala.cm', 'filiere': 'gestion', 'niveau': 'licence3', 'total_xp': 650, 'level': 4},
            {'username': 'aissatou', 'first_name': 'Aissatou', 'last_name': 'Bello', 'email': 'aissatou@univ-ngaoundere.cm', 'filiere': 'sciences', 'niveau': 'master2', 'total_xp': 380, 'level': 3},
            {'username': 'paul', 'first_name': 'Paul', 'last_name': 'Essomba', 'email': 'paul@univ-douala.cm', 'filiere': 'informatique', 'niveau': 'licence2', 'total_xp': 210, 'level': 2},
            {'username': 'marie', 'first_name': 'Marie', 'last_name': 'Fotso', 'email': 'marie@univ-dschang.cm', 'filiere': 'marketing', 'niveau': 'licence3', 'total_xp': 150, 'level': 2},
        ]
        for ud in leaderboard_users:
            if not CustomUser.objects.filter(username=ud['username']).exists():
                user = CustomUser.objects.create_user(
                    username=ud['username'], password='pathfinder2025',
                    first_name=ud['first_name'], last_name=ud['last_name'],
                    email=ud['email'], filiere=ud['filiere'], niveau=ud['niveau'],
                    avatar_initials=(ud['first_name'][0] + ud['last_name'][0]).upper(),
                    total_xp=ud['total_xp'], level=ud['level'],
                )
                XPEvent.objects.create(user=user, action='inscription_complete', xp_earned=50)
                # Award badges based on level
                if ud['level'] >= 3:
                    badge = Badge.objects.filter(slug='level-3').first()
                    if badge:
                        UserBadge.objects.create(user=user, badge=badge)
                if ud['level'] >= 5:
                    badge = Badge.objects.filter(slug='level-5').first()
                    if badge:
                        UserBadge.objects.create(user=user, badge=badge)
                self.stdout.write(f'  ✓ Classement: {user.first_name} {user.last_name} ({user.total_xp} XP)')
