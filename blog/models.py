from django.db import models
from django.conf import settings


class Category(models.Model):
    """Catégorie d'article de blog."""
    name = models.CharField(max_length=100, verbose_name='Nom')
    slug = models.SlugField(unique=True)

    class Meta:
        verbose_name = 'Catégorie'
        verbose_name_plural = 'Catégories'

    def __str__(self):
        return self.name


class BlogPost(models.Model):
    """Article de blog."""
    title = models.CharField(max_length=300, verbose_name='Titre')
    slug = models.SlugField(unique=True)
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, blank=True, related_name='posts')
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, related_name='posts')
    excerpt = models.TextField(max_length=500, blank=True, verbose_name='Extrait')
    content = models.TextField(verbose_name='Contenu')
    image_url = models.URLField(blank=True)
    published = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Article'
        verbose_name_plural = 'Articles'

    def __str__(self):
        return self.title


class Comment(models.Model):
    """Commentaire sur un article."""
    post = models.ForeignKey(BlogPost, on_delete=models.CASCADE, related_name='comments')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='comments')
    content = models.TextField(verbose_name='Commentaire')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['created_at']
        verbose_name = 'Commentaire'
        verbose_name_plural = 'Commentaires'

    def __str__(self):
        return f'{self.user} sur {self.post.title[:30]}'


class Testimonial(models.Model):
    """Témoignage d'un étudiant ayant trouvé un stage/emploi grâce à PathFinder."""
    STATUS_CHOICES = [
        ('pending', 'En attente'),
        ('approved', 'Approuvé'),
        ('rejected', 'Rejeté'),
    ]

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='testimonials')
    title = models.CharField(max_length=200, verbose_name='Titre')
    content = models.TextField(verbose_name='Votre témoignage')
    company = models.CharField(max_length=200, blank=True, verbose_name='Entreprise / Stage')
    achievement_type = models.CharField(max_length=50, default='emploi', choices=[
        ('emploi', 'Emploi trouvé'),
        ('stage', 'Stage obtenu'),
        ('freelance', 'Mission freelance'),
        ('projet', 'Projet réussi'),
        ('competence', 'Compétence acquise'),
    ])
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    is_featured = models.BooleanField(default=False, verbose_name='Mis en avant')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Témoignage'
        verbose_name_plural = 'Témoignages'

    def __str__(self):
        return f'{self.user} — {self.title}'
