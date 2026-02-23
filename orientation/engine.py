"""
PathFinder — Moteur IA d'orientation pondéré.

Algorithme :
    score_brut[carrière] = Σ poids(choix sélectionné, carrière)
    score_max[carrière]  = Σ max(poids par question, carrière)
    adéquation%          = (brut / max) × 100

Fonctionnalités :
    - Top 3 carrières classées par score
    - Compétences prioritaires identifiées
    - Résumé personnalisé dynamique
    - Projection carrière 3 ans
"""
from orientation.models import OrientationQuestion, OrientationChoice, OrientationResult
from parcours.models import CareerPath


def compute_orientation_scores(selected_choices):
    """
    Calcule les scores d'adéquation par carrière.

    Args:
        selected_choices: dict {question_id: choice_id}

    Returns:
        dict {career_slug: percentage}
    """
    # Initialiser les scores bruts et max possibles
    career_slugs = set()
    for question in OrientationQuestion.objects.prefetch_related('choices'):
        for choice in question.choices.all():
            career_slugs.update(choice.weights.keys())

    scores_brut = {slug: 0 for slug in career_slugs}
    scores_max = {slug: 0 for slug in career_slugs}

    for question in OrientationQuestion.objects.prefetch_related('choices'):
        choices = question.choices.all()
        q_id_str = str(question.id)

        # Calculer le max possible par carrière pour cette question
        for slug in career_slugs:
            max_w = max((c.weights.get(slug, 0) for c in choices), default=0)
            scores_max[slug] += max_w

        # Ajouter le score du choix sélectionné
        choice_id = selected_choices.get(q_id_str) or selected_choices.get(question.id)
        if choice_id:
            try:
                chosen = OrientationChoice.objects.get(id=choice_id)
                for slug, weight in chosen.weights.items():
                    scores_brut[slug] += weight
            except OrientationChoice.DoesNotExist:
                pass

    # Normaliser en pourcentage
    percentages = {}
    for slug in career_slugs:
        if scores_max[slug] > 0:
            percentages[slug] = round(scores_brut[slug] / scores_max[slug] * 100)
        else:
            percentages[slug] = 0

    return dict(sorted(percentages.items(), key=lambda x: x[1], reverse=True))


def get_top_careers(scores, limit=3):
    """Retourne les top N carrières avec leurs objets CareerPath."""
    results = []
    for slug, pct in list(scores.items())[:limit]:
        try:
            career = CareerPath.objects.get(slug=slug)
            results.append({'career': career, 'percentage': pct, 'slug': slug})
        except CareerPath.DoesNotExist:
            results.append({'career': None, 'percentage': pct, 'slug': slug})
    return results


def generate_summary(user, top_careers):
    """Génère un résumé personnalisé basé sur les résultats."""
    if not top_careers:
        return "Nous n'avons pas pu déterminer votre profil. Veuillez refaire le test."

    best = top_careers[0]
    career_name = best['career'].title if best['career'] else best['slug']
    pct = best['percentage']

    summary = (
        f"D'après l'analyse de vos réponses, votre profil correspond à "
        f"{pct}% au métier de {career_name}. "
    )

    if pct >= 85:
        summary += (
            f"C'est une excellente correspondance ! Votre profil montre une forte "
            f"affinité avec ce domaine. Nous vous recommandons de commencer "
            f"immédiatement votre parcours de formation."
        )
    elif pct >= 70:
        summary += (
            f"C'est une très bonne correspondance. Avec un développement ciblé "
            f"de vos compétences, vous pourrez exceller dans ce domaine."
        )
    else:
        summary += (
            f"Votre profil présente un potentiel intéressant dans ce domaine. "
            f"En renforçant certaines compétences clés, vous pourrez "
            f"progresser rapidement."
        )

    if len(top_careers) > 1:
        second = top_careers[1]
        second_name = second['career'].title if second['career'] else second['slug']
        summary += (
            f"\n\nVotre deuxième option est {second_name} avec {second['percentage']}% "
            f"d'adéquation, ce qui vous offre une alternative solide."
        )

    return summary


def generate_projection_3y(career_name, pct):
    """Génère une projection de carrière sur 3 ans."""
    return (
        f"📅 Année 1 : Formation intensive sur les fondamentaux de {career_name}. "
        f"Objectif : maîtriser les compétences de base et décrocher un premier stage.\n\n"
        f"📅 Année 2 : Spécialisation et projets concrets. Construction de votre "
        f"portfolio professionnel et développement de votre réseau.\n\n"
        f"📅 Année 3 : Insertion professionnelle. Avec votre niveau d'adéquation "
        f"de {pct}%, vous serez en position favorable pour décrocher un poste "
        f"de {career_name} junior ou lancer votre activité indépendante."
    )


def get_priority_skills(career):
    """Identifie les compétences prioritaires pour une carrière."""
    if not career:
        return []
    skills = career.skills.all()[:5]
    return [{'name': s.name, 'slug': s.slug, 'icon': s.icon} for s in skills]


def process_orientation(user, selected_choices):
    """
    Fonction principale : traite les réponses et crée le résultat.

    Args:
        user: CustomUser
        selected_choices: dict {question_id: choice_id}

    Returns:
        OrientationResult
    """
    scores = compute_orientation_scores(selected_choices)
    top_careers = get_top_careers(scores)

    best_career = top_careers[0]['career'] if top_careers else None
    best_pct = top_careers[0]['percentage'] if top_careers else 0

    summary = generate_summary(user, top_careers)
    projection = generate_projection_3y(
        best_career.title if best_career else 'votre métier',
        best_pct
    )
    priority = get_priority_skills(best_career)

    result = OrientationResult.objects.create(
        user=user,
        scores=scores,
        recommended_career=best_career,
        summary=summary,
        career_projection_3y=projection,
        priority_skills=priority,
        selected_choices=selected_choices,
    )

    # Accorder l'XP pour avoir complété le test
    user.add_xp(100, action='test_orientation_complete')

    return result
