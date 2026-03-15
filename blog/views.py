from django.shortcuts import render, get_object_or_404
from .models import BlogPost, Category, Comment, Testimonial
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.shortcuts import redirect
from django.utils.text import slugify
import uuid


def blog_list(request):
    """Liste des articles publiés."""
    posts = BlogPost.objects.filter(published=True).select_related('category', 'author')
    categories = Category.objects.all()
    cat_slug = request.GET.get('cat')
    if cat_slug:
        posts = posts.filter(category__slug=cat_slug)

    # Témoignages mis en avant
    featured_testimonials = Testimonial.objects.filter(status='approved', is_featured=True)[:3]

    context = {
        'posts': posts,
        'categories': categories,
        'active_cat': cat_slug,
        'featured_testimonials': featured_testimonials,
    }
    return render(request, 'blog/list.html', context)


def blog_detail(request, slug):
    """Détail d'un article avec commentaires."""
    post = get_object_or_404(BlogPost, slug=slug, published=True)
    comments = post.comments.select_related('user').all()

    if request.method == 'POST' and request.user.is_authenticated:
        content = request.POST.get('content', '').strip()
        if content:
            Comment.objects.create(post=post, user=request.user, content=content)
            request.user.add_xp(15, action='article_lu')
            messages.success(request, 'Commentaire ajouté ! +15 XP')
            return redirect('blog:detail', slug=slug)

    context = {
        'post': post,
        'comments': comments,
    }
    return render(request, 'blog/detail.html', context)


@login_required
def create_post(request):
    """Créer un article (Level 3+ uniquement)."""
    if request.user.level < 3:
        messages.warning(request, 'Vous devez atteindre le niveau 3 pour publier des articles.')
        return redirect('blog:list')

    categories = Category.objects.all()

    if request.method == 'POST':
        title = request.POST.get('title', '').strip()
        content = request.POST.get('content', '').strip()
        excerpt = request.POST.get('excerpt', '').strip()
        category_id = request.POST.get('category', '')

        if not title or not content:
            messages.error(request, 'Titre et contenu sont obligatoires.')
            return render(request, 'blog/create_post.html', {'categories': categories})

        slug = slugify(title) + '-' + uuid.uuid4().hex[:6]
        post = BlogPost.objects.create(
            title=title,
            slug=slug,
            content=content,
            excerpt=excerpt,
            author=request.user,
            category_id=int(category_id) if category_id else None,
            published=True,
        )
        request.user.add_xp(40, action='article_publie')
        messages.success(request, 'Article publié ! +40 XP')
        return redirect('blog:detail', slug=post.slug)

    context = {'categories': categories}
    return render(request, 'blog/create_post.html', context)


def testimonials_list(request):
    """Liste des témoignages."""
    testimonials = Testimonial.objects.filter(status='approved').select_related('user')
    context = {'testimonials': testimonials}
    return render(request, 'blog/testimonials.html', context)


@login_required
def create_testimonial(request):
    """Soumettre un témoignage."""
    if request.method == 'POST':
        title = request.POST.get('title', '').strip()
        content = request.POST.get('content', '').strip()
        company = request.POST.get('company', '').strip()
        achievement_type = request.POST.get('achievement_type', 'competence')

        if not title or not content:
            messages.error(request, 'Titre et contenu sont obligatoires.')
            return render(request, 'blog/create_testimonial.html')

        Testimonial.objects.create(
            user=request.user,
            title=title,
            content=content,
            company=company,
            achievement_type=achievement_type,
        )
        request.user.add_xp(25, action='temoignage_soumis')
        messages.success(request, 'Témoignage soumis ! +25 XP. Il sera publié après validation.')
        return redirect('blog:testimonials')

    return render(request, 'blog/create_testimonial.html')
