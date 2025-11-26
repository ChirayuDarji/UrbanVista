from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse, HttpResponseForbidden, HttpResponseBadRequest
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.urls import reverse
from django.db.models import Count
from .models import (
    TravelExperience,
    ExperienceUpvote,
    ExperienceBookmark,
    ExperienceMedia,  # <-- This line is required!
)
from .forms import TravelExperienceForm, ExperienceCommentForm, ExperienceMediaFormSet  # <-- This too!
from core.decorators import rate_limit

# ===========================
# Home/List View (Login Required)
# ===========================
@login_required
def experience_home(request):
    experiences = TravelExperience.objects.filter(status='published').select_related('user').order_by('-created_at')
    return render(request, "FreeContribution/experience_home.html", {
        "experiences": experiences,
    })

# ===========================
# List by Type
# ===========================
@login_required
def experience_list_by_type(request, experience_type):
    experiences = TravelExperience.objects.filter(
        status='published',
        experience_type=experience_type
    ).select_related('user').order_by('-created_at')
    return render(request, "FreeContribution/experience_list_by_type.html", {
        "experiences": experiences,
        "experience_type": experience_type,
    })

# ===========================
# Experience Detail View
# ===========================
@login_required
def experience_detail(request, slug):
    experience = get_object_or_404(TravelExperience, slug=slug, status='published')
    experience.increment_views()
    comments = experience.comments.filter(parent=None, is_approved=True).order_by('-created_at')
    comment_form = ExperienceCommentForm()
    is_upvoted = False
    is_bookmarked = False
    if request.user.is_authenticated:
        is_upvoted = ExperienceUpvote.objects.filter(experience=experience, user=request.user).exists()
        is_bookmarked = ExperienceBookmark.objects.filter(experience=experience, user=request.user).exists()
    return render(request, "FreeContribution/experience_detail.html", {
        "experience": experience,
        "comments": comments,
        "comment_form": comment_form,
        "is_upvoted": is_upvoted,
        "is_bookmarked": is_bookmarked,
    })

# ===========================
# Create Experience View
# ===========================
@login_required
@rate_limit("experience_create", limit=5, window_seconds=60)
def experience_create(request, experience_type=None):
    if request.method == "POST":
        form = TravelExperienceForm(request.POST, request.FILES, experience_type=experience_type)
        if form.is_valid():
            experience = form.save(commit=False)
            experience.user = request.user
            if experience_type:
                experience.experience_type = experience_type
            experience.save()
            return redirect(experience.get_absolute_url())
    else:
        form = TravelExperienceForm(experience_type=experience_type)
    return render(request, "FreeContribution/experience_form.html", {
        "form": form,
        "experience_type": experience_type,
    })

# ===========================
# Toggle Upvote (AJAX)
# ===========================
@login_required
@require_POST
def toggle_experience_upvote(request, pk):
    experience = get_object_or_404(TravelExperience, pk=pk, status='published')
    upvote, created = ExperienceUpvote.objects.get_or_create(experience=experience, user=request.user)
    if not created:
        upvote.delete()
        upvoted = False
    else:
        upvoted = True
    return JsonResponse({
        "upvoted": upvoted,
        "upvotes_count": experience.upvotes.count(),
    })

# ===========================
# Toggle Bookmark (AJAX)
# ===========================
@login_required
@require_POST
def toggle_experience_bookmark(request, pk):
    experience = get_object_or_404(TravelExperience, pk=pk, status='published')
    bookmark, created = ExperienceBookmark.objects.get_or_create(experience=experience, user=request.user)
    if not created:
        bookmark.delete()
        bookmarked = False
    else:
        bookmarked = True
    return JsonResponse({
        "bookmarked": bookmarked,
        "bookmarks_count": experience.bookmarks.count(),
    })

# ===========================
# Map Data API (for frontend maps)
# ===========================
@login_required
def experience_map_data(request):
    """Return map markers for published experiences.
    Supports optional filter: ?type=place|activity|story|tip
    """
    qs = TravelExperience.objects.filter(
        status='published',
        latitude__isnull=False,
        longitude__isnull=False,
    )
    type_filter = request.GET.get('type')
    if type_filter:
        qs = qs.filter(experience_type=type_filter)

    markers = []
    for exp in qs.only('id', 'title', 'slug', 'latitude', 'longitude', 'experience_type', 'location'):
        markers.append({
            'id': str(exp.id),
            'title': exp.title,
            'url': reverse('freecontribution:experience_detail', kwargs={'slug': exp.slug}),
            'lat': float(exp.latitude),
            'lng': float(exp.longitude),
            'type': exp.experience_type,
            'desc': exp.location or '',
        })

    return JsonResponse({'markers': markers})

# ===========================
# (Optional) Add Comment (POST)
# ===========================
@login_required
@require_POST
def add_experience_comment(request, slug):
    experience = get_object_or_404(TravelExperience, slug=slug, status='published')
    form = ExperienceCommentForm(request.POST)
    if form.is_valid():
        comment = form.save(commit=False)
        comment.user = request.user
        comment.experience = experience
        comment.save()
        return redirect(experience.get_absolute_url())
    # If invalid, re-render detail with errors
    comments = experience.comments.filter(parent=None, is_approved=True).order_by('-created_at')
    return render(request, "FreeContribution/experience_detail.html", {
        "experience": experience,
        "comments": comments,
        "comment_form": form,
    })
    
    
    
from .forms import TravelExperienceForm, ExperienceMediaFormSet

@login_required
def experience_create(request, experience_type=None):
    if request.method == "POST":
        form = TravelExperienceForm(request.POST, request.FILES, experience_type=experience_type)
        formset = ExperienceMediaFormSet(request.POST, request.FILES, queryset=ExperienceMedia.objects.none())
        if form.is_valid() and formset.is_valid():
            experience = form.save(commit=False)
            experience.user = request.user
            if experience_type:
                experience.experience_type = experience_type
            experience.save()
            # Save media files
            for media_form in formset:
                if media_form.cleaned_data and not media_form.cleaned_data.get('DELETE', False):
                    media = media_form.save(commit=False)
                    media.experience = experience
                    media.save()
            return redirect(experience.get_absolute_url())
    else:
        form = TravelExperienceForm(experience_type=experience_type)
        formset = ExperienceMediaFormSet(queryset=ExperienceMedia.objects.none())
    return render(request, "FreeContribution/experience_form.html", {
        "form": form,
        "formset": formset,
        "experience_type": experience_type,
    })    