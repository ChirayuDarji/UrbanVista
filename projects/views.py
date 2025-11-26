# projects/views.py

from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.shortcuts import render, get_object_or_404, redirect
from django.db.models import Q, Count
from django.core.paginator import Paginator
from django.utils import timezone
from .models import CityProject, ProjectCategory, ProjectUpdate, ProjectDocument
from .forms import CityProjectForm, ProjectUpdateForm, ProjectDocumentForm, ProjectCategoryForm
from reports.models import Department


def is_staff_or_authority(user):
    """Check if user is staff or has authority permissions"""
    if not user.is_authenticated:
        return False
    return user.is_staff or user.groups.filter(name='Authority').exists()


# ========================================
# LIST VIEWS
# ========================================

def project_list(request):
    """List all public projects with filters"""
    projects = CityProject.objects.filter(is_public=True)
    
    # Filters
    category_slug = request.GET.get('category', '')
    status = request.GET.get('status', '')
    search_query = request.GET.get('q', '')
    
    if category_slug:
        projects = projects.filter(category__slug=category_slug)
    
    if status:
        projects = projects.filter(status=status)
    
    if search_query:
        projects = projects.filter(
            Q(title__icontains=search_query) |
            Q(description__icontains=search_query) |
            Q(location__icontains=search_query) |
            Q(ward__icontains=search_query)
        )
    
    # Pagination
    paginator = Paginator(projects.order_by('-created_at'), 12)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    # Get categories for filter
    categories = ProjectCategory.objects.annotate(
        project_count=Count('projects', filter=Q(projects__is_public=True))
    ).filter(project_count__gt=0)
    
    # Get stats for all public projects (not filtered)
    all_public_projects = CityProject.objects.filter(is_public=True)
    total_projects = all_public_projects.count()
    in_progress_count = all_public_projects.filter(status='in_progress').count()
    completed_count = all_public_projects.filter(status='completed').count()
    unique_cities = all_public_projects.values_list('location', flat=True).distinct().count()
    
    context = {
        'projects': page_obj,
        'categories': categories,
        'selected_category': category_slug,
        'selected_status': status,
        'search_query': search_query,
        'stats': {
            'total': total_projects,
            'in_progress': in_progress_count,
            'completed': completed_count,
            'cities': unique_cities,
        },
    }
    return render(request, 'projects/project_list.html', context)


def project_detail(request, slug):
    """View project details"""
    project = get_object_or_404(
        CityProject.objects.select_related('category', 'department', 'created_by', 'updated_by').prefetch_related('updates', 'documents'),
        slug=slug,
        is_public=True
    )
    
    # Optimize view count increment using F() expression
    from django.db.models import F
    CityProject.objects.filter(pk=project.pk).update(views_count=F('views_count') + 1)
    # Refresh from DB to get updated count
    project.refresh_from_db()
    
    # Get related data (already prefetched)
    updates = project.updates.all()[:10]
    documents = project.documents.all()
    
    context = {
        'project': project,
        'updates': updates,
        'documents': documents,
    }
    return render(request, 'projects/project_detail.html', context)


# ========================================
# CREATE VIEWS
# ========================================

@login_required
@user_passes_test(is_staff_or_authority)
def project_create(request):
    """Create a new project"""
    if request.method == 'POST':
        form = CityProjectForm(request.POST, request.FILES)
        if form.is_valid():
            project = form.save(commit=False)
            project.created_by = request.user
            project.updated_by = request.user
            project.save()
            messages.success(request, f'Project "{project.title}" created successfully!')
            return redirect('projects:detail', slug=project.slug)
    else:
        form = CityProjectForm()
    
    context = {
        'form': form,
        'title': 'Create New Project',
    }
    return render(request, 'projects/project_form.html', context)


@login_required
@user_passes_test(is_staff_or_authority)
def project_update_add(request, slug):
    """Add an update to a project"""
    project = get_object_or_404(CityProject, slug=slug)
    
    if request.method == 'POST':
        form = ProjectUpdateForm(request.POST, request.FILES)
        if form.is_valid():
            update = form.save(commit=False)
            update.project = project
            update.created_by = request.user
            update.save()
            
            # Update project progress if provided
            if update.progress_percentage is not None:
                project.progress_percentage = update.progress_percentage
                project.save(update_fields=['progress_percentage'])
            
            messages.success(request, 'Project update added successfully!')
            return redirect('projects:detail', slug=project.slug)
    else:
        form = ProjectUpdateForm()
    
    context = {
        'form': form,
        'project': project,
        'title': f'Add Update to {project.title}',
    }
    return render(request, 'projects/project_update_form.html', context)


@login_required
@user_passes_test(is_staff_or_authority)
def project_document_add(request, slug):
    """Add a document to a project"""
    project = get_object_or_404(CityProject, slug=slug)
    
    if request.method == 'POST':
        form = ProjectDocumentForm(request.POST, request.FILES)
        if form.is_valid():
            document = form.save(commit=False)
            document.project = project
            document.uploaded_by = request.user
            document.save()
            messages.success(request, 'Document uploaded successfully!')
            return redirect('projects:detail', slug=project.slug)
    else:
        form = ProjectDocumentForm()
    
    context = {
        'form': form,
        'project': project,
        'title': f'Add Document to {project.title}',
    }
    return render(request, 'projects/project_document_form.html', context)


# ========================================
# UPDATE VIEWS
# ========================================

@login_required
@user_passes_test(is_staff_or_authority)
def project_edit(request, slug):
    """Edit an existing project"""
    project = get_object_or_404(CityProject, slug=slug)
    
    if request.method == 'POST':
        form = CityProjectForm(request.POST, request.FILES, instance=project)
        if form.is_valid():
            project = form.save(commit=False)
            project.updated_by = request.user
            project.save()
            messages.success(request, f'Project "{project.title}" updated successfully!')
            return redirect('projects:detail', slug=project.slug)
    else:
        form = CityProjectForm(instance=project)
    
    context = {
        'form': form,
        'project': project,
        'title': f'Edit {project.title}',
    }
    return render(request, 'projects/project_form.html', context)


# ========================================
# DELETE VIEWS
# ========================================

@login_required
@user_passes_test(is_staff_or_authority)
def project_delete(request, slug):
    """Delete a project"""
    project = get_object_or_404(CityProject, slug=slug)
    
    if request.method == 'POST':
        project_title = project.title
        project.delete()
        messages.success(request, f'Project "{project_title}" deleted successfully!')
        return redirect('projects:list')
    
    context = {
        'project': project,
    }
    return render(request, 'projects/project_delete_confirm.html', context)


@login_required
@user_passes_test(is_staff_or_authority)
def project_update_delete(request, pk):
    """Delete a project update"""
    update = get_object_or_404(ProjectUpdate, pk=pk)
    project_slug = update.project.slug
    
    if request.method == 'POST':
        update.delete()
        messages.success(request, 'Update deleted successfully!')
        return redirect('projects:detail', slug=project_slug)
    
    context = {
        'update': update,
    }
    return render(request, 'projects/project_update_delete_confirm.html', context)


@login_required
@user_passes_test(is_staff_or_authority)
def project_document_delete(request, pk):
    """Delete a project document"""
    document = get_object_or_404(ProjectDocument, pk=pk)
    project_slug = document.project.slug
    
    if request.method == 'POST':
        document.delete()
        messages.success(request, 'Document deleted successfully!')
        return redirect('projects:detail', slug=project_slug)
    
    context = {
        'document': document,
    }
    return render(request, 'projects/project_document_delete_confirm.html', context)


# ========================================
# CATEGORY MANAGEMENT (Optional)
# ========================================

@login_required
@user_passes_test(is_staff_or_authority)
def category_create(request):
    """Create a new project category"""
    if request.method == 'POST':
        form = ProjectCategoryForm(request.POST)
        if form.is_valid():
            category = form.save()
            messages.success(request, f'Category "{category.name}" created successfully!')
            return redirect('projects:list')
    else:
        form = ProjectCategoryForm()
    
    context = {
        'form': form,
        'title': 'Create Category',
    }
    return render(request, 'projects/category_form.html', context)

