from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.utils import timezone
from django.views.decorators.cache import cache_page
from core.decorators import staff_required
from .models import News, Category
from .forms import NewsForm

@cache_page(60)
def news_list(request):
    q = (request.GET.get('q') or '').strip()
    cat = request.GET.get('category')

    qs = News.objects.published().select_related('category', 'author').order_by('-published_at')
    if q:
        qs = qs.filter(title__icontains=q) | qs.filter(content__icontains=q)
    if cat:
        qs = qs.filter(category__slug=cat)

    paginator = Paginator(qs, 10)
    page_obj = paginator.get_page(request.GET.get('page'))

    featured = News.objects.featured().select_related('category', 'author').order_by('-published_at')[:3]
    categories = Category.objects.all()
    return render(request, 'news/news_list.html', {
        'featured': featured,
        'page_obj': page_obj,
        'q': q,
        'active_category': cat,
        'categories': categories,
    })

@cache_page(60)
def news_detail(request, slug):
    article = get_object_or_404(News, slug=slug, status='published')
    # Increment views
    News.objects.filter(pk=article.pk).update(views=article.views + 1)
    related = News.objects.filter(status='published', category=article.category).exclude(pk=article.pk).order_by('-published_at')[:6]
    return render(request, 'news/news_detail.html', {
        'article': article,
        'related': related,
    })


def news_by_category(request, slug):
    category = get_object_or_404(Category, slug=slug)
    qs = News.objects.filter(status='published', category=category).order_by('-published_at')
    paginator = Paginator(qs, 10)
    page_obj = paginator.get_page(request.GET.get('page'))
    categories = Category.objects.all()
    return render(request, 'news/category_list.html', {
        'category': category,
        'page_obj': page_obj,
        'categories': categories,
    })


# ---------------- Staff management (simple CRUD) ----------------
@login_required
@staff_required
def manage_list(request):
    qs = News.objects.order_by('-updated_at')
    if request.GET.get('status'):
        qs = qs.filter(status=request.GET['status'])
    paginator = Paginator(qs, 20)
    page_obj = paginator.get_page(request.GET.get('page'))
    return render(request, 'news/admin_news_manage.html', { 'page_obj': page_obj })


@login_required
@staff_required
def create(request):
    if request.method == 'POST':
        form = NewsForm(request.POST, request.FILES)
        if form.is_valid():
            article = form.save(commit=False)
            if not article.author:
                article.author = request.user
            if article.status == 'published' and not article.published_at:
                article.published_at = timezone.now()
            article.save()
            return redirect('news:detail', slug=article.slug)
    else:
        form = NewsForm()
    return render(request, 'news/news_form.html', { 'form': form })


@login_required
@staff_required
def edit(request, slug):
    article = get_object_or_404(News, slug=slug)
    if request.method == 'POST':
        form = NewsForm(request.POST, request.FILES, instance=article)
        if form.is_valid():
            article = form.save(commit=False)
            if article.status == 'published' and not article.published_at:
                article.published_at = timezone.now()
            article.save()
            return redirect('news:detail', slug=article.slug)
    else:
        form = NewsForm(instance=article)
    return render(request, 'news/news_form.html', { 'form': form, 'article': article })


@login_required
@staff_required
def delete(request, slug):
    article = get_object_or_404(News, slug=slug)
    if request.method == 'POST':
        article.delete()
        return redirect('news:manage')
    return render(request, 'news/news_delete_confirm.html', { 'article': article })