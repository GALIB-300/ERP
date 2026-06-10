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

from .forms import ResourceForm
from .models import Resource

# B-Django Admin Check #
def is_django_admin(user):
    role = getattr(getattr(user, "resource_profile", None), "role", None)
    # ✅ Treat superuser and manager_sales as admin-like (read-only)
    return user.is_superuser or role == "manager_sales"

# C-Filtering Function-(Resource Name-Based) #
def filter_resources(query=None, name_of_resource=None, user=None, is_admin=False, exclude_user=None):
    # Safely get role from user profile
    role = getattr(getattr(user, "resource_profile", None), "role", None)

    # Base queryset by role
    if is_admin or role in ["manager_sales", "manager_finance", "gm_sales"]:
        # Admins and privileged roles see all resources
        queryset = Resource.objects.all()
    elif role == "manager_construction":
        # Construction managers see only their own resources
        queryset = Resource.objects.filter(created_by=user)
    else:
        # Default: team members see only their own resources
        queryset = Resource.objects.filter(created_by=user)

    # Exclude specific user if provided
    if exclude_user:
        queryset = queryset.exclude(created_by=exclude_user)

    # Free text search
    if query:
        queryset = queryset.filter(Q(name_of_resource__icontains=query))

    # Resource name filter
    if name_of_resource:
        queryset = queryset.filter(name_of_resource__icontains=name_of_resource)

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

# E-Dashboard View-(Admin view all resources. Team view/add their own resources) #
# Step-(A)-Dashboard view #
@login_required
def resource_dashboard(request):
    # Step-(A1)-Search Query parameter-(q)-from the URL #
    query = request.GET.get("q", "").strip()

    # Step-(A2)-Name of Resource-based-query parameter-from the URL #
    name_of_resource = request.GET.get("name_of_resource", "").strip()

    # Step-(A3)-Check if user is admin (custom helper) #
    is_admin = is_django_admin(request.user)
    role = getattr(getattr(request.user, "resource_profile", None), "role", None)

    # Step-(A4)-Initialize form only for construction managers #
    form = None if is_admin else ResourceForm(request.POST or None)

    # Step-(A5)-Centralized data filter #
    resources = filter_resources(
        query=query,
        name_of_resource=name_of_resource,
        user=request.user,
        is_admin=is_admin
    )

    # Apply pagination #
    resources_page = get_paginated_queryset(request, resources)

    # Step-(A6)-Add new resource only if construction manager #
    if role == "manager_construction" and request.method == "POST" and form.is_valid():
        resource = form.save(commit=False)
        resource.created_by = request.user
        resource.team = role or "manager_construction"
        resource.save()
        messages.success(request, "✅ Resource detailed record created successfully.")
        return redirect(
            f"{reverse('resource_dashboard')}?q={query}&name_of_resource={name_of_resource}"
        )

    # Step-(A7)-Prepare context for template #
    context = {
        "resources": resources_page,
        "query": query,
        "name_of_resource": name_of_resource,
        "form": form,
        "mode": "list",
        "readonly": is_admin,  # Admin & manager_sales are readonly
        "is_admin": is_admin,
        "role": role,
    }

    # Step-(A8)-Render template #
    return render(request, "resource/resource_dashboard.html", context)

# F-Edit View-(Team edit only their own resources. Admin cannot edit) #
# Step-(A)-Edit view #
@login_required
def edit_resource(request, pk):
    # Step-(A1)-Get resource by ID #
    resource = get_object_or_404(Resource, pk=pk)

    # Step-(A2)-Check if user is admin (custom helper) #
    is_admin = is_django_admin(request.user)

    # Step-(A3)-Permission check based on Admin & Team #
    if is_admin or resource.created_by != request.user:
        raise PermissionDenied

    # Step-(A4)-Search Query parameter-(q)-from the URL #
    query = (request.GET.get("q") or "").strip()

    # Step-(A5)-Name of Resource-based-query parameter-from the URL #
    name_of_resource = (request.GET.get("name_of_resource") or "").strip()

    # Step-(A6)-Initialize form with resource instance #
    form = ResourceForm(request.POST or None, instance=resource)

    # Step-(A7)-Edit resources based on team users #
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "✏️ Resource detailed record updated successfully.")
        params = urlencode({
            "q": query,
            "name_of_resource": name_of_resource,
        })
        return redirect(f"{reverse('resource_dashboard')}?{params}")

    # Step-(A8)-Centralized data filter #
    resources = filter_resources(
        query=query,
        name_of_resource=name_of_resource,
        user=request.user,
        is_admin=is_admin
    )

    # Apply pagination #
    resources_page = get_paginated_queryset(request, resources)

    # Step-(A9)-Prepare context for edit template #
    context = {
        "form": form,
        "mode": "edit",
        "resource": resource,
        "query": query,
        "name_of_resource": name_of_resource,
        "readonly": False,
        "is_admin": is_admin,
        "resources": resources_page,  
    }

    # Step-(A10)-Render template #
    return render(request, "resource/resource_dashboard.html", context)

# G-Delete View-(Team delete only their own resources. Admin cannot delete) #
# Step-(A)-Delete view #
@login_required
def delete_resource(request, pk):
    # Step-(A1)-Get resource by ID #
    resource = get_object_or_404(Resource, pk=pk)

    # Step-(A2)-Check if user is admin (custom helper) #
    is_admin = is_django_admin(request.user)

    # Step-(A3)-Permission check based on Admin & Team #
    if is_admin or resource.created_by != request.user:
        raise PermissionDenied

    # Step-(A4)-Search Query parameter-(q)-from the URL #
    query = (request.GET.get("q") or "").strip()

    # Step-(A5)-Name of Resource-based-query parameter-from the URL #
    name_of_resource = (request.GET.get("name_of_resource") or "").strip()
    
    # Step-(A6)-Delete resources-(only team users can delete) #
    if request.method == "POST":
        name = resource.name_of_resource
        resource.delete()
        messages.success(request, f"🗑️ Resource '{name}' deleted successfully.")
        params = urlencode({
            "q": query,
            "name_of_resource": name_of_resource,
        })
        return redirect(f"{reverse('resource_dashboard')}?{params}")

    # Step-(A7)-Prepare context for delete confirmation template #
    context = {
        "resource": resource,
        "query": query,
        "name_of_resource": name_of_resource,
        "is_admin": is_admin,
        "readonly": True    # Admins are readonly, team confirm delete
    }

    # Step-(A8)-Render delete confirmation template #
    return render(request, "resource/confirm_delete.html", context)

# H-Views for only-List Table show #
@login_required
def resource_list_only(request):
    query = request.GET.get("q", "").strip()
    name_of_resource = request.GET.get("name_of_resource", "").strip()

    is_admin = is_django_admin(request.user)

    resources = filter_resources(
        query=query,
        name_of_resource=name_of_resource,
        user=request.user,
        is_admin=is_admin
    )

    resources_page = get_paginated_queryset(request, resources)

    context = {
        "resources": resources_page,
        "query": query,
        "name_of_resource": name_of_resource,
        "is_admin": is_admin,
        "mode": "list",
    }
    return render(request, "resource/resource_list_only.html", context)