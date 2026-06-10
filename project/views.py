# A -Import Required Modules #
from django.shortcuts import render, get_object_or_404, redirect
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.http import JsonResponse
from django.contrib import messages
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from urllib.parse import urlencode
from django.db.models import Q

from .forms import ProjectForm
from .models import Project

# B-Django Admin Check #
def is_django_admin(user):
    return user.is_superuser

# C-Filtering Function-(Project Name-Based) #
def filter_projects(query=None, name_of_project=None, user=None, is_admin=False, exclude_user=None):
    # Base queryset #
    if is_admin:
        # Admins see all projects #
        queryset = Project.objects.all()
    else:
        # Team members see only their own projects #
        queryset = Project.objects.filter(created_by=user)

    # Exclude specific user if provided-(removes projects created by a specific user from the results) #
    if exclude_user:
        queryset = queryset.exclude(created_by=exclude_user)

    # Free text search across multiple fields #
    if query:
        queryset = queryset.filter(
            Q(name_of_project__icontains=query)
        )

    # Filter by project name #
    if name_of_project:
        queryset = queryset.filter(name_of_project__icontains=name_of_project)

    return queryset

# D-Reusable Pagination Function #
def get_paginated_queryset(request, queryset, per_page=10):
    paginator = Paginator(queryset, per_page)
    page_number = request.GET.get("page")

    try:
        return paginator.page(page_number)
    except PageNotAnInteger:
        return paginator.page(1)
    except EmptyPage:
        return paginator.page(paginator.num_pages)

# E-Dashboard View-(Admin view all projects. Team view/add their own projects) #
# Step-(A)-Dashboard view #
@login_required
def project_dashboard(request):
    # Step-(A1)-Search Query parameter-(q)-from the URL #
    query = request.GET.get("q", "").strip()

    # Step-(A2)-Name of Project-based-query parameter-from the URL #
    name_of_project = request.GET.get("name_of_project", "").strip()

    # Step-(A3)-Check if user is admin (custom helper) #
    is_admin = is_django_admin(request.user)

    # Step-(A4)-Initialize form only for non-admin users #
    form = None if is_admin else ProjectForm(request.POST or None)

    # Step-(A5)-Centralized data filter #
    projects = filter_projects(
        query=query,
        name_of_project=name_of_project,
        user=request.user,
        is_admin=is_admin
    )

    # Apply pagination #
    projects_page = get_paginated_queryset(request, projects)

    # Step-(A6)-Add new project only if user is NOT admin #
    if not is_admin and request.method == "POST" and form.is_valid():
        project = form.save(commit=False)
        project.created_by = request.user
        project.team = getattr(
            getattr(request.user, "project_profile", None),
            "role",
            "manager_construction"   # default role for customers
        )
        project.save()
        messages.success(request, "✅ Project detailed record created successfully.")
        return redirect(
            f"{reverse('project_dashboard')}?q={query}&name_of_project={name_of_project}"
        )

    # Step-(A7)-Prepare context for template #
    context = {
        "projects": projects_page,   
        "query": query,
        "name_of_project": name_of_project,
        "form": form,          
        "mode": "list",
        "readonly": is_admin,  # Admins are readonly
        "is_admin": is_admin,
    }

    # Step-(A8)-Render template #
    return render(request, "project/project_dashboard.html", context)

# F-Edit View-(Team edit only their own projects. Admin cannot edit) #
# Step-(A)-Edit view #
@login_required
def edit_project(request, pk):
    # Step-(A1)-Get project by ID #
    project = get_object_or_404(Project, pk=pk)

    # Step-(A2)-Check if user is admin (custom helper) #
    is_admin = is_django_admin(request.user)

    # Step-(A3)-Permission check based on Admin & Team #
    if not is_admin and project.created_by != request.user:
        raise PermissionDenied

    # Step-(A4)-Search Query parameter-(q)-from the URL #
    query = (request.GET.get("q") or "").strip()

    # Step-(A5)-Name of Project-based-query parameter-from the URL #
    name_of_project = (request.GET.get("name_of_project") or "").strip()

    # Step-(A6)-Initialize form with project instance #
    form = ProjectForm(request.POST or None, instance=project)

    # Step-(A7)-Edit projects based on team users #
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "✏️ Project detailed record updated successfully.")
        params = urlencode({
            "q": query,
            "name_of_project": name_of_project,
        })
        return redirect(f"{reverse('project_dashboard')}?{params}")

    # Step-(A8)-Centralized data filter #
    projects = filter_projects(
        query=query,
        name_of_project=name_of_project,
        user=request.user,
        is_admin=is_admin
    )

    # Apply pagination #
    projects_page = get_paginated_queryset(request, projects)

    # Step-(A9)-Prepare context for edit template #
    context = {
        "form": form,
        "mode": "edit",
        "project": project,
        "query": query,
        "name_of_project": name_of_project,
        "readonly": False,
        "is_admin": is_admin,
        "projects": projects_page,  
    }

    # Step-(A10)-Render template #
    return render(request, "project/project_dashboard.html", context)

# G-Delete View-(Team delete only their own projects. Admin cannot delete) #
# Step-(A)-Delete view #
@login_required
def delete_project(request, pk):
    # Step-(A1)-Get project by ID #
    project = get_object_or_404(Project, pk=pk)

    # Step-(A2)-Check if user is admin (custom helper) #
    is_admin = is_django_admin(request.user)

    # Step-(A3)-Permission check based on Admin & Team #
    if not is_admin and project.created_by != request.user:
        raise PermissionDenied

    # Step-(A4)-Search Query parameter-(q)-from the URL #
    query = (request.GET.get("q") or "").strip()

    # Step-(A5)-Name of Project-based-query parameter-from the URL #
    name_of_project = (request.GET.get("name_of_project") or "").strip()
    
    # Step-(A6)-Delete projects-(only team users can delete) #
    if request.method == "POST":
        name = project.name_of_project
        project.delete()
        messages.success(request, f"🗑️ Project '{name}' deleted successfully.")
        params = urlencode({
            "q": query,
            "name_of_project": name_of_project,
        })
        return redirect(f"{reverse('project_dashboard')}?{params}")

    # Step-(A7)-Prepare context for delete confirmation template #
    context = {
        "project": project,
        "query": query,
        "name_of_project": name_of_project,
        "is_admin": is_admin,
        "readonly": True    # Admins are readonly, team confirm delete
    }

    # Step-(A8)-Render delete confirmation template #
    return render(request, "project/confirm_delete.html", context)
