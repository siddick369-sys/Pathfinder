"""
seed_resources.py — Peuple la banque de formations PathFinder avec 108+ ressources.
Usage: python manage.py seed_resources
"""
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = 'Crée 108+ ressources de formation pour toutes les compétences'

    def handle(self, *args, **options):
        from competences.models import Skill, SkillResource
        self.stdout.write('🎓 Création de la banque de formations...\n')
        total = 0
        for skill in Skill.objects.all():
            data = RESOURCES.get(skill.slug, [])
            for i, r in enumerate(data, 1):
                SkillResource.objects.get_or_create(
                    skill=skill, title=r['title'],
                    defaults={
                        'description': r.get('description', ''),
                        'resource_type': r['resource_type'],
                        'level': r.get('level', 'debutant'),
                        'duration_minutes': r.get('duration_minutes', 0),
                        'xp_reward': r.get('xp_reward', 15),
                        'order': i,
                        'is_free_preview': r.get('is_free_preview', False),
                        'url': r.get('url', ''),
                        'content': r.get('content', ''),
                    }
                )
            total += len(data)
            self.stdout.write(f'  ✓ {skill.name}: {len(data)} ressources')
        self.stdout.write(self.style.SUCCESS(f'\n✅ {total} ressources créées !'))


# ━━━━━━━━━━━━━━━  DATA  ━━━━━━━━━━━━━━━
RESOURCES = {

# ───────────────── HTML & CSS ─────────────────
'html-css': [
    {'title': 'Introduction au HTML', 'description': 'Les bases du langage HTML : balises, structure, sémantique.', 'resource_type': 'tutoriel', 'level': 'debutant', 'duration_minutes': 30, 'xp_reward': 25, 'is_free_preview': True,
     'content': "Le HTML (HyperText Markup Language) est le langage de base du web.\n\n📌 Structure de base :\n<!DOCTYPE html>\n<html lang=\"fr\">\n<head>\n  <meta charset=\"UTF-8\">\n  <title>Ma page</title>\n</head>\n<body>\n  <h1>Bonjour !</h1>\n  <p>Mon premier paragraphe.</p>\n</body>\n</html>\n\n🔑 Points clés :\n- Les balises HTML structurent le contenu\n- Le DOCTYPE indique la version HTML\n- Le <head> contient les métadonnées\n- Le <body> contient le contenu visible"},
    {'title': 'Les balises sémantiques HTML5', 'description': 'header, nav, main, section, article, aside, footer.', 'resource_type': 'tutoriel', 'level': 'debutant', 'duration_minutes': 25, 'xp_reward': 20,
     'content': "Les balises sémantiques donnent du sens au contenu.\n\n<header> — En-tête de page ou section\n<nav> — Navigation principale\n<main> — Contenu principal\n<section> — Section thématique\n<article> — Contenu autonome\n<aside> — Contenu latéral\n<footer> — Pied de page\n\n✅ Avantages : meilleur SEO, accessibilité, lisibilité du code."},
    {'title': 'Formulaires HTML avancés', 'description': 'input types, validation, fieldset, datalist.', 'resource_type': 'tutoriel', 'level': 'intermediaire', 'duration_minutes': 40, 'xp_reward': 30,
     'content': "Les formulaires sont essentiels pour les interactions.\n\nTypes d'input : text, email, password, number, date, range, color, file, checkbox, radio.\n\nValidation native :\n- required, minlength, maxlength\n- pattern (regex), min, max\n- type=email valide le format\n\n<fieldset> regroupe les champs\n<legend> titre le groupe\n<datalist> propose des suggestions"},
    {'title': 'CSS Flexbox maîtrisé', 'description': 'Layouts 1D modernes avec Flexbox.', 'resource_type': 'tutoriel', 'level': 'intermediaire', 'duration_minutes': 45, 'xp_reward': 35,
     'content': "Flexbox gère les layouts en 1 dimension.\n\n.container { display:flex; justify-content:center; align-items:center; gap:16px; flex-wrap:wrap; }\n\nPropriétés container : flex-direction, justify-content, align-items, flex-wrap, gap.\nPropriétés enfants : flex-grow, flex-shrink, flex-basis, align-self, order."},
    {'title': 'CSS Grid Layout', 'description': 'Layouts 2D complexes avec CSS Grid.', 'resource_type': 'tutoriel', 'level': 'intermediaire', 'duration_minutes': 50, 'xp_reward': 35,
     'content': "CSS Grid gère les layouts en 2 dimensions.\n\n.grid { display:grid; grid-template-columns:repeat(3,1fr); grid-template-rows:auto 1fr auto; gap:20px; }\n\nFonctions : repeat(), minmax(), fr, auto-fill, auto-fit.\nPlacement : grid-column, grid-row, grid-area."},
    {'title': 'Responsive Design & Media Queries', 'description': 'Mobile-first, breakpoints, unités relatives.', 'resource_type': 'tutoriel', 'level': 'intermediaire', 'duration_minutes': 35, 'xp_reward': 30,
     'content': "Le responsive design adapte le site à tous les écrans.\n\nApproche mobile-first :\n@media (min-width:768px) { /* tablette */ }\n@media (min-width:1024px) { /* desktop */ }\n\nUnités relatives : rem, em, %, vw, vh, clamp().\nImages responsives : max-width:100%; height:auto;"},
    {'title': 'Animations CSS & Transitions', 'description': 'Transitions, keyframes, transform, performance.', 'resource_type': 'tutoriel', 'level': 'avance', 'duration_minutes': 40, 'xp_reward': 40,
     'content': "Les animations améliorent l'expérience utilisateur.\n\nTransitions : transition: property duration easing;\nTransform : translate, rotate, scale, skew.\nKeyframes :\n@keyframes fadeIn { from{opacity:0} to{opacity:1} }\n.el { animation: fadeIn 0.3s ease; }\n\n⚡ Performance : animer uniquement transform et opacity."},
    {'title': 'Variables CSS & Thèmes', 'description': 'Custom properties, dark mode, design tokens.', 'resource_type': 'tutoriel', 'level': 'avance', 'duration_minutes': 30, 'xp_reward': 35,
     'content': "Les variables CSS permettent un design maintenable.\n\n:root { --primary:#1a56db; --bg:#f9fafb; --text:#1a1a2e; }\n[data-theme='dark'] { --primary:#3b82f6; --bg:#0f172a; --text:#e2e8f0; }\n\nUtilisation : color: var(--primary);"},
    {'title': 'Cours vidéo HTML complet', 'description': 'Apprenez HTML de A à Z avec ce cours vidéo de 2h.', 'resource_type': 'video', 'level': 'debutant', 'duration_minutes': 120, 'xp_reward': 40, 'url': 'https://www.youtube.com/embed/pQN-pnXPaVg'},
    {'title': 'Cours vidéo CSS pour débutants', 'description': 'Les fondamentaux CSS en vidéo : sélecteurs, box model, couleurs.', 'resource_type': 'video', 'level': 'debutant', 'duration_minutes': 90, 'xp_reward': 35, 'url': 'https://www.youtube.com/embed/1PnVor36_40'},
    {'title': 'Flexbox en 20 minutes', 'description': 'Comprendre Flexbox rapidement avec des exemples pratiques.', 'resource_type': 'video', 'level': 'intermediaire', 'duration_minutes': 20, 'xp_reward': 20, 'url': 'https://www.youtube.com/embed/JJSoEo8JSnc'},
    {'title': 'CSS Grid crash course', 'description': 'Maîtrisez CSS Grid avec ce crash course complet.', 'resource_type': 'video', 'level': 'intermediaire', 'duration_minutes': 30, 'xp_reward': 25, 'url': 'https://www.youtube.com/embed/EFafSYg-PkI'},
    {'title': 'Documentation MDN — HTML', 'description': 'Référence complète HTML par Mozilla Developer Network.', 'resource_type': 'lien', 'level': 'debutant', 'xp_reward': 10, 'url': 'https://developer.mozilla.org/fr/docs/Web/HTML'},
    {'title': 'Documentation MDN — CSS', 'description': 'Référence complète CSS par Mozilla.', 'resource_type': 'lien', 'level': 'debutant', 'xp_reward': 10, 'url': 'https://developer.mozilla.org/fr/docs/Web/CSS'},
    {'title': 'CSS-Tricks — Flexbox Guide', 'description': 'Le guide visuel de référence pour Flexbox.', 'resource_type': 'lien', 'level': 'intermediaire', 'xp_reward': 10, 'url': 'https://css-tricks.com/snippets/css/a-guide-to-flexbox/'},
    {'title': 'Can I Use', 'description': 'Compatibilité navigateur de toutes les propriétés CSS.', 'resource_type': 'lien', 'level': 'intermediaire', 'xp_reward': 5, 'url': 'https://caniuse.com/'},
    {'title': 'Exercice : Page portfolio', 'description': 'Créez votre page portfolio en HTML/CSS pur.', 'resource_type': 'exercice', 'level': 'debutant', 'duration_minutes': 60, 'xp_reward': 45,
     'content': "🎯 Objectif : Créer un portfolio personnel.\n\n📋 Consignes :\n1. Header avec nom et navigation\n2. Section hero avec photo et bio\n3. Section projets (3 cartes)\n4. Footer avec liens sociaux\n5. Responsive (mobile + desktop)"},
    {'title': 'Exercice : Reproduire une maquette', 'description': 'Reproduisez fidèlement une maquette Figma.', 'resource_type': 'exercice', 'level': 'intermediaire', 'duration_minutes': 90, 'xp_reward': 55,
     'content': "🎯 Objectif : Reproduire la page d'accueil de PathFinder.\n\n📋 Consignes :\n1. Navbar avec logo et liens\n2. Section hero avec titre CTA\n3. Section '3 étapes' avec cartes\n4. Responsive mobile-first\n\n📏 Critères : Fidélité 40%, Code propre 30%, Responsive 30%"},
    {'title': 'Mini-formation : Site web complet', 'description': 'Construisez un site vitrine de A à Z en 5 parties.', 'resource_type': 'mini_formation', 'level': 'intermediaire', 'duration_minutes': 180, 'xp_reward': 80,
     'content': "🎓 Formation complète : site vitrine.\n\nPartie 1 : Structure HTML (30min)\nPartie 2 : Styles de base CSS (30min)\nPartie 3 : Layout Flexbox/Grid (40min)\nPartie 4 : Responsive design (30min)\nPartie 5 : Animations et polish (30min)"},
],

# ───────────────── JAVASCRIPT ─────────────────
'javascript': [
    {'title': 'Variables et types de données', 'description': 'let, const, types primitifs, objets.', 'resource_type': 'tutoriel', 'level': 'debutant', 'duration_minutes': 25, 'xp_reward': 25, 'is_free_preview': True,
     'content': "JavaScript utilise 3 mots-clés pour les variables.\n\nlet — variable réassignable\nconst — constante\nvar — ancien, à éviter\n\nTypes : string, number, boolean, null, undefined, symbol, bigint.\nObjets : {}, [], function, Date, RegExp."},
    {'title': 'Fonctions et closures', 'description': 'Déclaration, arrow functions, closures, callbacks.', 'resource_type': 'tutoriel', 'level': 'debutant', 'duration_minutes': 35, 'xp_reward': 30,
     'content': "Les fonctions sont la base de JS.\n\nfunction greet(name) { return `Bonjour ${name}`; }\nconst greet = (name) => `Bonjour ${name}`;\n\nClosure : une fonction qui capture les variables de son scope englobant.\nCallback : une fonction passée en argument."},
    {'title': 'Manipulation du DOM', 'description': 'querySelector, événements, création d\'éléments.', 'resource_type': 'tutoriel', 'level': 'debutant', 'duration_minutes': 40, 'xp_reward': 30,
     'content': "Le DOM est l'interface entre JS et le HTML.\n\ndocument.querySelector('.class');\ndocument.getElementById('id');\nelement.addEventListener('click', handler);\ndocument.createElement('div');\nelement.appendChild(child);\nelement.innerHTML = '<p>Contenu</p>';"},
    {'title': 'ES6+ : Destructuring, Spread, Modules', 'description': 'Syntaxe moderne ES6 à ES2023.', 'resource_type': 'tutoriel', 'level': 'intermediaire', 'duration_minutes': 45, 'xp_reward': 35,
     'content': "Destructuring : const {name, age} = user;\nSpread : const arr2 = [...arr1, 4, 5];\nTemplate literals : `Bonjour ${name}`\nModules : import/export\nOptional chaining : user?.address?.city\nNullish coalescing : value ?? default"},
    {'title': 'Promesses et Async/Await', 'description': 'Programmation asynchrone en JS moderne.', 'resource_type': 'tutoriel', 'level': 'intermediaire', 'duration_minutes': 50, 'xp_reward': 40,
     'content': "L'asynchrone est central en JS.\n\nPromise : new Promise((resolve, reject) => { ... });\n.then().catch().finally()\n\nasync function fetchData() {\n  try {\n    const res = await fetch(url);\n    const data = await res.json();\n  } catch(err) { console.error(err); }\n}"},
    {'title': 'Fetch API et requêtes HTTP', 'description': 'GET, POST, headers, JSON, gestion d\'erreurs.', 'resource_type': 'tutoriel', 'level': 'intermediaire', 'duration_minutes': 35, 'xp_reward': 30,
     'content': "Fetch remplace XMLHttpRequest.\n\nGET : const res = await fetch('/api/users');\nPOST : await fetch('/api', { method:'POST', headers:{'Content-Type':'application/json'}, body:JSON.stringify(data) });\n\nGestion d'erreurs : vérifier res.ok avant res.json()"},
    {'title': 'LocalStorage et gestion d\'état', 'description': 'Persistance côté client, patterns de state.', 'resource_type': 'tutoriel', 'level': 'intermediaire', 'duration_minutes': 25, 'xp_reward': 25,
     'content': "localStorage persiste les données dans le navigateur.\n\nlocalStorage.setItem('key', JSON.stringify(data));\nconst data = JSON.parse(localStorage.getItem('key'));\nlocalStorage.removeItem('key');\n\nLimite : 5-10 Mo par domaine, synchrone, strings uniquement."},
    {'title': 'Design Patterns JS', 'description': 'Module, Observer, Factory, Singleton.', 'resource_type': 'tutoriel', 'level': 'avance', 'duration_minutes': 60, 'xp_reward': 50,
     'content': "Les design patterns structurent le code.\n\nModule : IIFE ou ES Modules pour encapsuler\nObserver : addEventListener / custom events\nFactory : fonctions qui créent des objets\nSingleton : instance unique partagée\nProxy : intercepter les opérations sur un objet"},
    {'title': 'Cours vidéo JavaScript complet', 'description': 'Apprendre JS de zéro à héros.', 'resource_type': 'video', 'level': 'debutant', 'duration_minutes': 180, 'xp_reward': 50, 'url': 'https://www.youtube.com/embed/W6NZfCJ1iT8'},
    {'title': 'Async/Await expliqué visuellement', 'description': 'Comprendre l\'asynchrone avec des animations.', 'resource_type': 'video', 'level': 'intermediaire', 'duration_minutes': 25, 'xp_reward': 25, 'url': 'https://www.youtube.com/embed/vn3tm0quoqE'},
    {'title': 'ES6 en 30 minutes', 'description': 'Toutes les nouvelles fonctionnalités ES6 résumées.', 'resource_type': 'video', 'level': 'intermediaire', 'duration_minutes': 30, 'xp_reward': 25, 'url': 'https://www.youtube.com/embed/NCwa_xi0Uuc'},
    {'title': 'JavaScript avancé : Closures & Prototypes', 'description': 'Concepts avancés expliqués clairement.', 'resource_type': 'video', 'level': 'avance', 'duration_minutes': 45, 'xp_reward': 35, 'url': 'https://www.youtube.com/embed/vMdrKLf_hSo'},
    {'title': 'MDN — JavaScript Guide', 'description': 'Guide de référence JavaScript par Mozilla.', 'resource_type': 'lien', 'level': 'debutant', 'xp_reward': 10, 'url': 'https://developer.mozilla.org/fr/docs/Web/JavaScript/Guide'},
    {'title': 'JavaScript.info', 'description': 'Tutoriel JavaScript moderne et complet.', 'resource_type': 'lien', 'level': 'debutant', 'xp_reward': 10, 'url': 'https://fr.javascript.info/'},
    {'title': 'Exercice : Todo List', 'description': 'Créez une application Todo en JS vanilla.', 'resource_type': 'exercice', 'level': 'debutant', 'duration_minutes': 60, 'xp_reward': 45,
     'content': "🎯 Todo App en JS pur.\n\n1. Ajouter/supprimer des tâches\n2. Marquer comme fait\n3. Filtrer (tout/actif/fait)\n4. Persistance localStorage\n5. Compteur de tâches restantes"},
    {'title': 'Exercice : Jeu du pendu', 'description': 'Codez le jeu du pendu en JavaScript.', 'resource_type': 'exercice', 'level': 'intermediaire', 'duration_minutes': 90, 'xp_reward': 55,
     'content': "🎯 Jeu du pendu.\n\n1. Liste de mots aléatoires\n2. Afficher les lettres trouvées\n3. Clavier virtuel cliquable\n4. Compteur de vies\n5. Animation de pendu SVG"},
    {'title': 'Exercice : API Météo', 'description': 'App météo avec Fetch API et géolocalisation.', 'resource_type': 'exercice', 'level': 'avance', 'duration_minutes': 120, 'xp_reward': 65,
     'content': "🎯 App météo avec API.\n\n1. Géolocalisation du navigateur\n2. Appel API OpenWeatherMap\n3. Afficher température, humidité, vent\n4. Recherche par ville\n5. Prévisions sur 5 jours"},
    {'title': 'Mini-formation : App interactive complète', 'description': 'Construisez un quiz interactif en 4 parties.', 'resource_type': 'mini_formation', 'level': 'intermediaire', 'duration_minutes': 150, 'xp_reward': 75,
     'content': "🎓 Quiz interactif.\n\nPartie 1 : Structure HTML du quiz\nPartie 2 : Logique JS questions/réponses\nPartie 3 : Score et progression\nPartie 4 : Timer et animations"},
],

# ───────────────── PYTHON & DJANGO ─────────────────
'python': [
    {'title': 'Python : les fondamentaux', 'description': 'Variables, types, opérateurs, structures de contrôle.', 'resource_type': 'tutoriel', 'level': 'debutant', 'duration_minutes': 35, 'xp_reward': 25, 'is_free_preview': True,
     'content': "Python est un langage simple et puissant.\n\nVariables : name = 'PathFinder'\nTypes : str, int, float, bool, list, dict, tuple, set\nConditions : if/elif/else\nBoucles : for item in liste: / while condition:\nFonctions : def greet(name): return f'Bonjour {name}'"},
    {'title': 'Structures de données Python', 'description': 'Listes, dictionnaires, sets, compréhensions.', 'resource_type': 'tutoriel', 'level': 'debutant', 'duration_minutes': 40, 'xp_reward': 30,
     'content': "Listes : [1,2,3], append, pop, slice, sort\nDicts : {'key':'value'}, get, items, keys, values\nSets : {1,2,3}, union, intersection, difference\nTuples : (1,2,3), immuable\n\nCompréhensions : [x**2 for x in range(10) if x%2==0]"},
    {'title': 'POO en Python', 'description': 'Classes, héritage, méthodes, properties, dunder methods.', 'resource_type': 'tutoriel', 'level': 'intermediaire', 'duration_minutes': 50, 'xp_reward': 40,
     'content': "La POO organise le code en objets.\n\nclass User:\n    def __init__(self, name, email):\n        self.name = name\n        self.email = email\n\n    @property\n    def display(self):\n        return f'{self.name} <{self.email}>'\n\nHéritage : class Admin(User): ..."},
    {'title': 'Django : premiers pas', 'description': 'Installation, projet, app, modèles, vues, URLs.', 'resource_type': 'tutoriel', 'level': 'debutant', 'duration_minutes': 60, 'xp_reward': 40,
     'content': "Django est un framework web Python.\n\npip install django\ndjango-admin startproject monprojet\npython manage.py startapp monapp\n\nModèles → Base de données\nVues → Logique métier\nURLs → Routes\nTemplates → Interface HTML"},
    {'title': 'Django Modèles avancés', 'description': 'Relations, managers, querysets, signals, migrations.', 'resource_type': 'tutoriel', 'level': 'intermediaire', 'duration_minutes': 55, 'xp_reward': 40,
     'content': "Relations : ForeignKey, ManyToMany, OneToOne\nQuerysets : filter, exclude, annotate, aggregate\nManagers : objects = CustomManager()\nSignals : post_save, pre_delete\nMigrations : makemigrations, migrate"},
    {'title': 'Django Templates & Forms', 'description': 'Système de templates, formulaires, CSRF, validation.', 'resource_type': 'tutoriel', 'level': 'intermediaire', 'duration_minutes': 45, 'xp_reward': 35,
     'content': "Templates : héritage avec extends/block, tags {% %}, variables {{ }}\nForms : class ContactForm(forms.Form): ...\nModelForm : formulaire lié à un modèle\nCSRF : {% csrf_token %} obligatoire\nValidation : clean_fieldname(), validators"},
    {'title': 'Django REST Framework', 'description': 'Créer une API REST avec DRF.', 'resource_type': 'tutoriel', 'level': 'avance', 'duration_minutes': 70, 'xp_reward': 50,
     'content': "DRF simplifie la création d'APIs.\n\nSerializers : transformer les modèles en JSON\nViewSets : CRUD automatique\nRouters : URLs auto-générées\nPermissions : IsAuthenticated, IsAdminUser\nPagination, filtrage, recherche"},
    {'title': 'Tests en Django', 'description': 'TestCase, Client, Factory, coverage.', 'resource_type': 'tutoriel', 'level': 'avance', 'duration_minutes': 45, 'xp_reward': 40,
     'content': "Les tests garantissent la qualité.\n\nclass UserTest(TestCase):\n    def setUp(self):\n        self.user = User.objects.create_user('test')\n\n    def test_login(self):\n        response = self.client.post('/login/', data)\n        self.assertEqual(response.status_code, 302)\n\npython manage.py test --verbosity=2"},
    {'title': 'Cours vidéo Python pour débutants', 'description': 'Apprendre Python de zéro.', 'resource_type': 'video', 'level': 'debutant', 'duration_minutes': 180, 'xp_reward': 50, 'url': 'https://www.youtube.com/embed/rfscVS0vtbw'},
    {'title': 'Django tutoriel complet', 'description': 'Construire une app web Django de A à Z.', 'resource_type': 'video', 'level': 'debutant', 'duration_minutes': 240, 'xp_reward': 60, 'url': 'https://www.youtube.com/embed/F5mRW0jo-U4'},
    {'title': 'Django REST Framework crash course', 'description': 'Créer une API REST en 1h.', 'resource_type': 'video', 'level': 'avance', 'duration_minutes': 60, 'xp_reward': 40, 'url': 'https://www.youtube.com/embed/cJveiktaOSQ'},
    {'title': 'Python OOP en 40 minutes', 'description': 'Programmation orientée objet Python.', 'resource_type': 'video', 'level': 'intermediaire', 'duration_minutes': 40, 'xp_reward': 30, 'url': 'https://www.youtube.com/embed/JeznW_7DlB0'},
    {'title': 'Documentation Python officielle', 'description': 'Référence complète du langage Python.', 'resource_type': 'lien', 'level': 'debutant', 'xp_reward': 10, 'url': 'https://docs.python.org/fr/3/'},
    {'title': 'Documentation Django', 'description': 'Documentation officielle de Django.', 'resource_type': 'lien', 'level': 'debutant', 'xp_reward': 10, 'url': 'https://docs.djangoproject.com/fr/5.0/'},
    {'title': 'Real Python', 'description': 'Tutoriels Python de qualité professionnelle.', 'resource_type': 'lien', 'level': 'intermediaire', 'xp_reward': 10, 'url': 'https://realpython.com/'},
    {'title': 'Exercice : Script de scraping', 'description': 'Scraper des offres d\'emploi avec BeautifulSoup.', 'resource_type': 'exercice', 'level': 'intermediaire', 'duration_minutes': 90, 'xp_reward': 55,
     'content': "🎯 Web scraping.\n\n1. pip install requests beautifulsoup4\n2. Récupérer une page d'annonces\n3. Parser les titres et liens\n4. Sauvegarder en CSV\n5. Ajouter la pagination"},
    {'title': 'Exercice : Blog Django', 'description': 'Créez un blog complet avec Django.', 'resource_type': 'exercice', 'level': 'intermediaire', 'duration_minutes': 120, 'xp_reward': 65,
     'content': "🎯 Blog Django.\n\n1. Modèles Post, Category, Comment\n2. CRUD avec vues génériques\n3. Formulaire de commentaire\n4. Pagination\n5. Système de recherche"},
    {'title': 'Mini-formation : API complète', 'description': 'Construire une API REST de A à Z avec DRF.', 'resource_type': 'mini_formation', 'level': 'avance', 'duration_minutes': 200, 'xp_reward': 90,
     'content': "🎓 API REST complète.\n\nPartie 1 : Modèles et Serializers\nPartie 2 : Views et Permissions\nPartie 3 : Auth JWT\nPartie 4 : Tests et documentation\nPartie 5 : Déploiement"},
],

# ───────────────── REACT.JS ─────────────────
'react': [
    {'title': 'Introduction à React', 'description': 'JSX, composants, props, rendering.', 'resource_type': 'tutoriel', 'level': 'debutant', 'duration_minutes': 40, 'xp_reward': 30, 'is_free_preview': True,
     'content': "React est une bibliothèque UI de Facebook.\n\nJSX : syntaxe <div>{variable}</div>\nComposants : function App() { return <h1>Hello</h1>; }\nProps : <User name='Alice' age={25} />\nRendering : ReactDOM.createRoot(el).render(<App />)"},
    {'title': 'State et Hooks', 'description': 'useState, useEffect, useRef, useContext.', 'resource_type': 'tutoriel', 'level': 'debutant', 'duration_minutes': 45, 'xp_reward': 35,
     'content': "Les Hooks gèrent l'état et les effets.\n\nconst [count, setCount] = useState(0);\nuseEffect(() => { document.title = count; }, [count]);\nconst ref = useRef(null);\nconst value = useContext(ThemeContext);"},
    {'title': 'Listes et formulaires React', 'description': 'map, key, controlled components, validation.', 'resource_type': 'tutoriel', 'level': 'intermediaire', 'duration_minutes': 35, 'xp_reward': 30,
     'content': "Listes : items.map(item => <li key={item.id}>{item.name}</li>)\nFormulaires contrôlés : value={state} onChange={handler}\nValidation : erreurs d'état, regex, bibliothèques (Yup, Zod)"},
    {'title': 'React Router v6', 'description': 'Navigation SPA, routes imbriquées, paramètres.', 'resource_type': 'tutoriel', 'level': 'intermediaire', 'duration_minutes': 40, 'xp_reward': 35,
     'content': "React Router gère la navigation.\n\n<BrowserRouter>\n<Routes>\n  <Route path='/' element={<Home/>} />\n  <Route path='/users/:id' element={<User/>} />\n</Routes>\n</BrowserRouter>\n\nuseNavigate(), useParams(), useLocation()"},
    {'title': 'State Management avec Zustand', 'description': 'Gestion d\'état global simple et performante.', 'resource_type': 'tutoriel', 'level': 'intermediaire', 'duration_minutes': 30, 'xp_reward': 30,
     'content': "Zustand simplifie le state management.\n\nconst useStore = create((set) => ({\n  count: 0,\n  increment: () => set(s => ({count: s.count + 1})),\n}));\n\nfunction Counter() {\n  const count = useStore(s => s.count);\n}"},
    {'title': 'Custom Hooks', 'description': 'Créer ses propres hooks réutilisables.', 'resource_type': 'tutoriel', 'level': 'avance', 'duration_minutes': 40, 'xp_reward': 40,
     'content': "Les custom hooks encapsulent la logique.\n\nfunction useDebounce(value, delay) {\n  const [debounced, setDebounced] = useState(value);\n  useEffect(() => {\n    const timer = setTimeout(() => setDebounced(value), delay);\n    return () => clearTimeout(timer);\n  }, [value, delay]);\n  return debounced;\n}"},
    {'title': 'Performance React', 'description': 'memo, useMemo, useCallback, lazy, Suspense.', 'resource_type': 'tutoriel', 'level': 'avance', 'duration_minutes': 45, 'xp_reward': 45,
     'content': "Optimiser les performances React.\n\nReact.memo(Component) — évite les re-renders\nuseMemo(() => compute(), [deps]) — mémoiser un calcul\nuseCallback(fn, [deps]) — mémoiser une fonction\nlazy(() => import('./Heavy')) — code splitting\n<Suspense fallback={<Loading/>}> — loading states"},
    {'title': 'Next.js fondamentaux', 'description': 'SSR, SSG, API routes, App Router.', 'resource_type': 'tutoriel', 'level': 'avance', 'duration_minutes': 60, 'xp_reward': 50,
     'content': "Next.js ajoute le SSR à React.\n\nApp Router : app/page.tsx = route /\nServer Components : par défaut dans Next 13+\nAPI Routes : app/api/route.ts\nSSG : generateStaticParams()\nMiddleware : middleware.ts"},
    {'title': 'Cours vidéo React complet', 'description': 'React de zéro avec projets pratiques.', 'resource_type': 'video', 'level': 'debutant', 'duration_minutes': 300, 'xp_reward': 70, 'url': 'https://www.youtube.com/embed/bMknfKXIFA8'},
    {'title': 'React Hooks expliqués', 'description': 'Tous les hooks React expliqués avec exemples.', 'resource_type': 'video', 'level': 'intermediaire', 'duration_minutes': 45, 'xp_reward': 30, 'url': 'https://www.youtube.com/embed/TNhaISOUy6Q'},
    {'title': 'Next.js crash course', 'description': 'Apprendre Next.js en 1h.', 'resource_type': 'video', 'level': 'avance', 'duration_minutes': 60, 'xp_reward': 40, 'url': 'https://www.youtube.com/embed/mTz0GXj8NN0'},
    {'title': 'Documentation React officielle', 'description': 'Documentation React.dev.', 'resource_type': 'lien', 'level': 'debutant', 'xp_reward': 10, 'url': 'https://fr.react.dev/'},
    {'title': 'React Patterns', 'description': 'Patterns et bonnes pratiques React.', 'resource_type': 'lien', 'level': 'intermediaire', 'xp_reward': 10, 'url': 'https://www.patterns.dev/react'},
    {'title': 'Exercice : Dashboard React', 'description': 'Créez un dashboard interactif avec React.', 'resource_type': 'exercice', 'level': 'intermediaire', 'duration_minutes': 120, 'xp_reward': 60,
     'content': "🎯 Dashboard React.\n\n1. Layout avec sidebar et contenu\n2. Composants : StatCard, Chart, Table\n3. State management avec Zustand\n4. Fetch de données simulées\n5. Thème dark/light"},
    {'title': 'Exercice : E-commerce React', 'description': 'App e-commerce avec panier et filtre.', 'resource_type': 'exercice', 'level': 'avance', 'duration_minutes': 180, 'xp_reward': 80,
     'content': "🎯 E-commerce.\n\n1. Liste produits avec filtres\n2. Page détail produit\n3. Panier avec quantités\n4. Recherche en temps réel\n5. Checkout form"},
    {'title': 'Mini-formation : App React complète', 'description': 'Projet complet avec auth, API, et déploiement.', 'resource_type': 'mini_formation', 'level': 'avance', 'duration_minutes': 240, 'xp_reward': 100,
     'content': "🎓 App React complète.\n\nPartie 1 : Setup Vite + Routing\nPartie 2 : Auth avec JWT\nPartie 3 : CRUD avec API\nPartie 4 : State management\nPartie 5 : Tests et déploiement"},
],

# ───────────────── BASES DE DONNÉES ─────────────────
'database': [
    {'title': 'SQL : les bases', 'description': 'SELECT, INSERT, UPDATE, DELETE, WHERE.', 'resource_type': 'tutoriel', 'level': 'debutant', 'duration_minutes': 40, 'xp_reward': 30, 'is_free_preview': True,
     'content': "SQL gère les données relationnelles.\n\nSELECT * FROM users WHERE age > 18;\nINSERT INTO users (name, email) VALUES ('Alice', 'a@b.cm');\nUPDATE users SET name='Bob' WHERE id=1;\nDELETE FROM users WHERE id=1;\n\nClauses : WHERE, ORDER BY, LIMIT, OFFSET, GROUP BY, HAVING"},
    {'title': 'Jointures SQL', 'description': 'INNER JOIN, LEFT JOIN, subqueries, UNION.', 'resource_type': 'tutoriel', 'level': 'intermediaire', 'duration_minutes': 45, 'xp_reward': 35,
     'content': "Les jointures relient les tables.\n\nINNER JOIN : seulement les correspondances\nLEFT JOIN : toutes les lignes de gauche\nRIGHT JOIN : toutes les lignes de droite\nCROSS JOIN : produit cartésien\n\nSubquery : SELECT * FROM users WHERE id IN (SELECT user_id FROM orders)"},
    {'title': 'Conception de bases de données', 'description': 'MCD, MLD, normalisation, relations.', 'resource_type': 'tutoriel', 'level': 'intermediaire', 'duration_minutes': 50, 'xp_reward': 40,
     'content': "La conception est cruciale.\n\nMCD : Modèle Conceptuel de Données (entités, relations)\nMLD : Modèle Logique de Données (tables, colonnes)\nNormalisation : 1NF, 2NF, 3NF\nRelations : 1:1, 1:N, N:N\nClés : primaire, étrangère, composite"},
    {'title': 'PostgreSQL avancé', 'description': 'Index, vues, triggers, fonctions PL/pgSQL.', 'resource_type': 'tutoriel', 'level': 'avance', 'duration_minutes': 60, 'xp_reward': 50,
     'content': "PostgreSQL offre des fonctionnalités avancées.\n\nIndex : CREATE INDEX idx ON users(email);\nVues : CREATE VIEW active_users AS SELECT...;\nTriggers : exécuter du code après INSERT/UPDATE\nFonctions : CREATE FUNCTION... RETURNS...;\nJSON : JSONB, opérateurs ->, ->>"},
    {'title': 'Django ORM mastery', 'description': 'QuerySet API, F(), Q(), annotations, raw SQL.', 'resource_type': 'tutoriel', 'level': 'avance', 'duration_minutes': 55, 'xp_reward': 45,
     'content': "L'ORM Django abstrait le SQL.\n\nFilter : User.objects.filter(age__gte=18)\nQ : Q(name='Alice') | Q(name='Bob')\nF : F('price') * F('quantity')\nAnnotate : .annotate(total=Sum('amount'))\nAggregate : .aggregate(Avg('age'))\nRaw : User.objects.raw('SELECT ...')"},
    {'title': 'Redis et caching', 'description': 'Cache, sessions, queues avec Redis.', 'resource_type': 'tutoriel', 'level': 'avance', 'duration_minutes': 40, 'xp_reward': 40,
     'content': "Redis est un store clé-valeur en mémoire.\n\nUsages : cache, sessions, pub/sub, queues.\nDjango : CACHES = {'default': {'BACKEND': 'django.core.cache.backends.redis.RedisCache'}}\nCommandes : SET, GET, DEL, EXPIRE, TTL"},
    {'title': 'Cours vidéo SQL complet', 'description': 'Maîtriser SQL de A à Z.', 'resource_type': 'video', 'level': 'debutant', 'duration_minutes': 240, 'xp_reward': 60, 'url': 'https://www.youtube.com/embed/HXV3zeQKqGY'},
    {'title': 'PostgreSQL pour développeurs', 'description': 'PostgreSQL avancé en pratique.', 'resource_type': 'video', 'level': 'intermediaire', 'duration_minutes': 120, 'xp_reward': 45, 'url': 'https://www.youtube.com/embed/qw--VYLpxG4'},
    {'title': 'Django ORM queries', 'description': 'Requêtes ORM Django optimisées.', 'resource_type': 'video', 'level': 'avance', 'duration_minutes': 50, 'xp_reward': 35, 'url': 'https://www.youtube.com/embed/2OcN2BsOeDM'},
    {'title': 'SQLZoo', 'description': 'Exercices SQL interactifs en ligne.', 'resource_type': 'lien', 'level': 'debutant', 'xp_reward': 10, 'url': 'https://sqlzoo.net/'},
    {'title': 'PostgreSQL Documentation', 'description': 'Documentation officielle PostgreSQL.', 'resource_type': 'lien', 'level': 'intermediaire', 'xp_reward': 10, 'url': 'https://www.postgresql.org/docs/'},
    {'title': 'DB Fiddle', 'description': 'Tester des requêtes SQL en ligne.', 'resource_type': 'lien', 'level': 'debutant', 'xp_reward': 5, 'url': 'https://www.db-fiddle.com/'},
    {'title': 'Exercice : Modéliser une école', 'description': 'Concevoir le schéma BD d\'une école.', 'resource_type': 'exercice', 'level': 'intermediaire', 'duration_minutes': 60, 'xp_reward': 50,
     'content': "🎯 Modéliser une école.\n\n1. Tables : Etudiants, Professeurs, Cours, Notes\n2. Relations et clés étrangères\n3. 10 requêtes : moyennes, classements, absences\n4. Index sur les champs fréquents\n5. Vue pour le bulletin"},
    {'title': 'Exercice : Optimisation de requêtes', 'description': 'Optimiser des requêtes SQL lentes.', 'resource_type': 'exercice', 'level': 'avance', 'duration_minutes': 90, 'xp_reward': 60,
     'content': "🎯 Optimisation SQL.\n\n1. Analyser avec EXPLAIN ANALYZE\n2. Ajouter des index manquants\n3. Réécrire les subqueries en JOIN\n4. Utiliser les CTE\n5. Mesurer les gains de performance"},
    {'title': 'Mini-formation : Base de données production', 'description': 'Gérer une BD en production.', 'resource_type': 'mini_formation', 'level': 'avance', 'duration_minutes': 180, 'xp_reward': 85,
     'content': "🎓 BD en production.\n\nPartie 1 : Backup et restauration\nPartie 2 : Monitoring et alertes\nPartie 3 : Migrations sans downtime\nPartie 4 : Réplication et haute dispo"},
],

# ───────────────── DEVOPS & DÉPLOIEMENT ─────────────────
'devops': [
    {'title': 'Git : les fondamentaux', 'description': 'init, add, commit, push, pull, branches.', 'resource_type': 'tutoriel', 'level': 'debutant', 'duration_minutes': 35, 'xp_reward': 25, 'is_free_preview': True,
     'content': "Git est le système de versioning standard.\n\ngit init — initialiser un repo\ngit add . — ajouter les fichiers\ngit commit -m 'message' — créer un commit\ngit push origin main — envoyer au serveur\ngit pull — récupérer les changements\ngit branch feature — créer une branche"},
    {'title': 'Git avancé', 'description': 'Rebase, stash, cherry-pick, bisect, hooks.', 'resource_type': 'tutoriel', 'level': 'intermediaire', 'duration_minutes': 40, 'xp_reward': 35,
     'content': "Git avancé pour les pros.\n\ngit rebase main — rebaser sur main\ngit stash — mettre de côté\ngit cherry-pick abc123 — prendre un commit\ngit bisect — trouver un bug par dichotomie\ngit hooks — scripts automatiques\n.gitignore — fichiers à ignorer"},
    {'title': 'Docker : conteneurisation', 'description': 'Dockerfile, images, containers, volumes.', 'resource_type': 'tutoriel', 'level': 'intermediaire', 'duration_minutes': 50, 'xp_reward': 40,
     'content': "Docker conteneurise les applications.\n\nDockerfile :\nFROM python:3.11\nWORKDIR /app\nCOPY . .\nRUN pip install -r requirements.txt\nCMD [\"python\", \"manage.py\", \"runserver\", \"0.0.0.0:8000\"]\n\ndocker build -t app .\ndocker run -p 8000:8000 app"},
    {'title': 'Docker Compose', 'description': 'Multi-conteneurs, networks, services.', 'resource_type': 'tutoriel', 'level': 'intermediaire', 'duration_minutes': 40, 'xp_reward': 35,
     'content': "Docker Compose orchestre plusieurs services.\n\nservices:\n  web:\n    build: .\n    ports: ['8000:8000']\n    depends_on: [db]\n  db:\n    image: postgres:15\n    environment:\n      POSTGRES_DB: pathfinder\n\ndocker-compose up -d"},
    {'title': 'CI/CD avec GitHub Actions', 'description': 'Pipeline automatisé, tests, déploiement.', 'resource_type': 'tutoriel', 'level': 'avance', 'duration_minutes': 55, 'xp_reward': 45,
     'content': "GitHub Actions automatise le workflow.\n\n.github/workflows/ci.yml\non: [push]\njobs:\n  test:\n    runs-on: ubuntu-latest\n    steps:\n    - uses: actions/checkout@v4\n    - uses: actions/setup-python@v5\n    - run: pip install -r requirements.txt\n    - run: python manage.py test"},
    {'title': 'Nginx et reverse proxy', 'description': 'Configuration Nginx, SSL, proxy_pass.', 'resource_type': 'tutoriel', 'level': 'avance', 'duration_minutes': 40, 'xp_reward': 40,
     'content': "Nginx sert de reverse proxy.\n\nserver {\n  listen 80;\n  server_name pathfinder.cm;\n  location / {\n    proxy_pass http://127.0.0.1:8000;\n    proxy_set_header Host $host;\n  }\n  location /static/ {\n    alias /app/static/;\n  }\n}"},
    {'title': 'Déploiement sur serveur Linux', 'description': 'VPS, SSH, Gunicorn, Supervisor.', 'resource_type': 'tutoriel', 'level': 'avance', 'duration_minutes': 60, 'xp_reward': 50,
     'content': "Déployer Django sur un VPS.\n\n1. Connecter en SSH\n2. Installer Python, PostgreSQL, Nginx\n3. Cloner le projet\n4. Configurer venv, pip install\n5. Gunicorn : gunicorn finder.wsgi:application\n6. Supervisor pour le process\n7. Nginx reverse proxy\n8. Certbot pour HTTPS"},
    {'title': 'Monitoring et logs', 'description': 'Sentry, logging, métriques, alertes.', 'resource_type': 'tutoriel', 'level': 'avance', 'duration_minutes': 35, 'xp_reward': 35,
     'content': "Le monitoring détecte les problèmes.\n\nSentry : erreurs en production\nDjango logging : logger.error(), logger.info()\nMétriques : temps de réponse, CPU, mémoire\nAlertes : webhook, email, SMS\nHealthcheck : endpoint /health/ pour le monitoring"},
    {'title': 'Cours vidéo Git & GitHub', 'description': 'Git de débutant à avancé.', 'resource_type': 'video', 'level': 'debutant', 'duration_minutes': 120, 'xp_reward': 40, 'url': 'https://www.youtube.com/embed/RGOj5yH7evk'},
    {'title': 'Docker en 2h', 'description': 'Docker et Docker Compose complet.', 'resource_type': 'video', 'level': 'intermediaire', 'duration_minutes': 120, 'xp_reward': 45, 'url': 'https://www.youtube.com/embed/fqMOX6JJhGo'},
    {'title': 'GitHub Actions CI/CD', 'description': 'CI/CD automatisé avec GitHub Actions.', 'resource_type': 'video', 'level': 'avance', 'duration_minutes': 50, 'xp_reward': 35, 'url': 'https://www.youtube.com/embed/R8_veQiYBjI'},
    {'title': 'Déployer Django en production', 'description': 'VPS + Docker + Nginx + SSL.', 'resource_type': 'video', 'level': 'avance', 'duration_minutes': 90, 'xp_reward': 50, 'url': 'https://www.youtube.com/embed/SA_iS4gc_bg'},
    {'title': 'Git Documentation', 'description': 'Documentation officielle de Git.', 'resource_type': 'lien', 'level': 'debutant', 'xp_reward': 10, 'url': 'https://git-scm.com/doc'},
    {'title': 'Docker Hub', 'description': 'Registre d\'images Docker.', 'resource_type': 'lien', 'level': 'intermediaire', 'xp_reward': 5, 'url': 'https://hub.docker.com/'},
    {'title': 'DigitalOcean Tutorials', 'description': 'Tutoriels DevOps de qualité.', 'resource_type': 'lien', 'level': 'intermediaire', 'xp_reward': 10, 'url': 'https://www.digitalocean.com/community/tutorials'},
    {'title': 'Exercice : Dockeriser une app Django', 'description': 'Conteneuriser PathFinder avec Docker.', 'resource_type': 'exercice', 'level': 'intermediaire', 'duration_minutes': 90, 'xp_reward': 55,
     'content': "🎯 Dockeriser Django.\n\n1. Créer un Dockerfile\n2. docker-compose.yml avec web + db + redis\n3. Variables d'environnement .env\n4. Volume pour les static files\n5. Script d'entrypoint"},
    {'title': 'Exercice : Pipeline CI/CD', 'description': 'Créer un pipeline GitHub Actions complet.', 'resource_type': 'exercice', 'level': 'avance', 'duration_minutes': 120, 'xp_reward': 65,
     'content': "🎯 Pipeline CI/CD.\n\n1. Tests automatisés sur push\n2. Linting avec flake8\n3. Build Docker image\n4. Push vers registry\n5. Déploiement auto sur staging"},
    {'title': 'Mini-formation : Du dev au prod', 'description': 'Pipeline complet de développement à production.', 'resource_type': 'mini_formation', 'level': 'avance', 'duration_minutes': 240, 'xp_reward': 100,
     'content': "🎓 Du dev au prod.\n\nPartie 1 : Environnement de dev (Docker)\nPartie 2 : Tests et CI\nPartie 3 : Staging et review apps\nPartie 4 : Déploiement production\nPartie 5 : Monitoring et maintenance"},
],

}
