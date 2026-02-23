from django.shortcuts import render, get_object_or_404
from .models import BlogPost, Category, Comment
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.shortcuts import redirect


def blog_list(request):
    """Liste des articles publiés."""
    posts = BlogPost.objects.filter(published=True).select_related('category', 'author')
    categories = Category.objects.all()
    cat_slug = request.GET.get('cat')
    if cat_slug:
        posts = posts.filter(category__slug=cat_slug)

    context = {
        'posts': posts,
        'categories': categories,
        'active_cat': cat_slug,
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
