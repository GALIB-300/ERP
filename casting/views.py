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

from .forms import CastingForm
from .models import Casting

# B-Django Admin Check #
def is_django_admin(user):
    # Adjust this to match your custom user model #
    return getattr(user, "role", None) == "admin"

# C-Filtering Function-(Project Name and Location-Based) #
def filter_castings(query=None, project_name_casting=None, location=None, user=None, is_admin=False, exclude_user=None):
    # Base queryset #
    if is_admin:
        # Admins see all castings #
        queryset = Casting.objects.all()
    else:
        # Team members see only their own castings #
        queryset = Casting.objects.filter(created_by=user)

    # Exclude specific user if provided-(removes castings created by a specific user from the results) #
    if exclude_user:
        queryset = queryset.exclude(created_by=exclude_user)

    # Free text search across multiple fields #
    if query:
        queryset = queryset.filter(
            Q(project_name_casting__name_of_project__icontains=query) |  # adjust field name if needed
            Q(location__icontains=query)
        )

    # Filter by project name #
    if project_name_casting:
        queryset = queryset.filter(project_name_casting__name_of_project__icontains=project_name_casting)

    # Filter by Location #
    if location:
        queryset = queryset.filter(location__icontains=location)

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

# E-Team will view their own castings #
@login_required
def casting_list(request):
    # Search filters
    query = request.GET.get("q", "").strip()
    project_name_casting = request.GET.get("project_name_casting", "").strip()

    # Check if user is admin
    is_admin = is_django_admin(request.user)

    # Filter castings: admin sees all, team sees only their own
    castings_queryset = filter_castings(
        query=query,
        project_name_casting=project_name_casting,
        user=request.user,
        is_admin=is_admin
    )

    # ✅ Apply pagination
    castings = get_paginated_queryset(request, castings_queryset, per_page=10)

    context = {
        "castings": castings,
        "query": query,
        "project_name_casting": project_name_casting,
        "readonly": is_admin,   # admins are readonly
        "is_admin": is_admin,
    }
    return render(request, "casting/casting_list.html", context)

# F-Team will add casting #
@login_required
def casting_add(request):
    form = CastingForm(request.POST or None, user=request.user)

    if request.method == "POST" and form.is_valid():
        casting = form.save(commit=False)
        casting.created_by = request.user
        casting.team = getattr(
            getattr(request.user, "casting_profile", None),
            "role",
            "manager_construction"   # default role
        )
        casting.save()
        messages.success(request, "✅ Casting record created successfully.")
        return redirect(
            f"{reverse('casting_list')}?q=&project_name_casting="
        )

    context = {
        "form": form,
        "readonly": False,
        "is_admin": False,
    }
    return render(request, "casting/casting_form.html", context)

# G-Admin will view all castings #
@login_required
def casting_list(request):
    # Search filters
    query = request.GET.get("q", "").strip()
    project_name_casting = request.GET.get("project_name_casting", "").strip()

    # Check if user is admin
    is_admin = is_django_admin(request.user)

    # Filter castings: admin sees all, team sees only their own
    castings_queryset = filter_castings(
        query=query,
        project_name_casting=project_name_casting,
        user=request.user,
        is_admin=is_admin
    )

    # ✅ Apply pagination
    castings = get_paginated_queryset(request, castings_queryset, per_page=10)

    context = {
        "castings": castings,
        "query": query,
        "project_name_casting": project_name_casting,
        "readonly": is_admin,   # admins are readonly
        "is_admin": is_admin,
    }
    return render(request, "casting/casting_list.html", context)

# H-Team will edit their own casting. Admin cannot edit #
@login_required
def edit_casting(request, pk):
    # Step-(A1)-Get casting by ID
    casting = get_object_or_404(Casting, pk=pk)

    # Step-(A2)-Check if user is admin (custom helper)
    is_admin = is_django_admin(request.user)

    # Step-(A3)-Permission check: only team member who created casting can edit
    if is_admin or casting.created_by != request.user:
        raise PermissionDenied

    # Step-(A4)-Search Query parameter-(q)-from the URL
    query = (request.GET.get("q") or "").strip()

    # Step-(A5)-Project name-based query parameter-from the URL
    project_name_casting = (request.GET.get("project_name_casting") or "").strip()

    # Step-(A6)-Initialize form with casting instance
    form = CastingForm(request.POST or None, instance=casting, user=request.user)

    # Step-(A7)-Save edits if valid
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "✏️ Casting record updated successfully.")
        params = urlencode({
            "q": query,
            "project_name_casting": project_name_casting,
        })
        return redirect(f"{reverse('casting_list')}?{params}")

    # Step-(A8)-Prepare context for edit template
    context = {
        "form": form,
        "mode": "edit",
        "casting": casting,
        "query": query,
        "project_name_casting": project_name_casting,
        "readonly": False,
        "is_admin": is_admin,
    }

    # Step-(A9)-Render dedicated form template
    return render(request, "casting/casting_form.html", context)

# I-Team delete their own casting. Admin cannot delete #
@login_required
def delete_casting(request, pk):
    # Step-(A1)-Get casting by ID
    casting = get_object_or_404(Casting, pk=pk)

    # Step-(A2)-Check if user is admin (custom helper)
    is_admin = is_django_admin(request.user)

    # Step-(A3)-Permission check: only team member who created casting can delete
    if is_admin or casting.created_by != request.user:
        raise PermissionDenied

    # Step-(A4)-Search Query parameter-(q)-from the URL
    query = (request.GET.get("q") or "").strip()

    # Step-(A5)-Project name-based query parameter-from the URL
    project_name_casting = (request.GET.get("project_name_casting") or "").strip()
    
    # Step-(A6)-Delete casting (only team users can delete)
    if request.method == "POST":
        name = casting.project_name_casting.name_of_project if casting.project_name_casting else f"ID {casting.pk}"
        casting.delete()
        messages.success(request, f"🗑️ Casting '{name}' deleted successfully.")
        params = urlencode({
            "q": query,
            "project_name_casting": project_name_casting,
        })
        return redirect(f"{reverse('casting_list')}?{params}")

    # Step-(A7)-Prepare context for delete confirmation template
    context = {
        "casting": casting,
        "query": query,
        "project_name_casting": project_name_casting,
        "is_admin": is_admin,
        "readonly": True    # Admins are readonly, team confirm delete
    }

    # Step-(A8)-Render delete confirmation template
    return render(request, "casting/confirm_delete.html", context)

