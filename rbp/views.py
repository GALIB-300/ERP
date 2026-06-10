# A -Import Required Modules #
from django.shortcuts import render, get_object_or_404, redirect
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.contrib import messages
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from urllib.parse import urlencode
from django.db.models import Q
from django.http import JsonResponse

from .forms import RbpForm
from .models import Rbp
from resource.models import Resource


# B-Django Admin Check #
def is_django_admin(user):
    return user.is_superuser

# C-Filtering Function-(Project Name & Resource Name-Based) #
def filter_rbps(query=None, project_name_rbp=None, resource_name_rbp=None, user=None, is_admin=False, exclude_user=None):
    # Base queryset #
    if is_admin:
        queryset = Rbp.objects.all()
    else:
        queryset = Rbp.objects.filter(created_by=user)

    # Exclude specific user if provided #
    if exclude_user:
        queryset = queryset.exclude(created_by=exclude_user)

    # Free text search across project & resource fields #
    if query:
        queryset = queryset.filter(
            Q(project_name_rbp__name_of_project__icontains=query) |
            Q(resource_name_rbp__name_of_resource__icontains=query)
        )

    # Filter by project name #
    if project_name_rbp:
        queryset = queryset.filter(project_name_rbp__name_of_project__icontains=project_name_rbp)

    # Filter by resource name #
    if resource_name_rbp:
        queryset = queryset.filter(resource_name_rbp__name_of_resource__icontains=resource_name_rbp)

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

# E-Dashboard View-(Admin view all RBPs. Team view/add their own RBPs) #
@login_required
def rbp_dashboard(request):
    query = request.GET.get("q", "").strip()
    project_name_rbp = request.GET.get("project_name_rbp", "").strip()
    resource_name_rbp = request.GET.get("resource_name_rbp", "").strip()

    is_admin = is_django_admin(request.user)
    form = None if is_admin else RbpForm(request.POST or None, user=request.user)

    rbps = filter_rbps(
        query=query,
        project_name_rbp=project_name_rbp,
        resource_name_rbp=resource_name_rbp,
        user=request.user,
        is_admin=is_admin
    )

    rbps_page = get_paginated_queryset(request, rbps)

    if not is_admin and request.method == "POST" and form.is_valid():
        rbp = form.save(commit=False)
        rbp.created_by = request.user
        rbp.team = getattr(
            getattr(request.user, "rbp_profile", None),
            "role",
            "manager_procurement"
        )
        rbp.save()
        messages.success(request, "✅ RBP record created successfully.")
        return redirect(
            f"{reverse('rbp_dashboard')}?q={query}&project_name_rbp={project_name_rbp}&resource_name_rbp={resource_name_rbp}"
        )

    context = {
        "rbps": rbps_page,
        "query": query,
        "project_name_rbp": project_name_rbp,
        "resource_name_rbp": resource_name_rbp,
        "form": form,
        "mode": "list",
        "readonly": is_admin,
        "is_admin": is_admin,
    }
    return render(request, "rbp/rbp_dashboard.html", context)

# F-Edit View-(Team edit only their own RBPs. Admin cannot edit) #
@login_required
def edit_rbp(request, pk):
    rbp = get_object_or_404(Rbp, pk=pk)
    is_admin = is_django_admin(request.user)

    if is_admin or rbp.created_by != request.user:
        raise PermissionDenied

    query = (request.GET.get("q") or "").strip()
    project_name_rbp = (request.GET.get("project_name_rbp") or "").strip()
    resource_name_rbp = (request.GET.get("resource_name_rbp") or "").strip()

    form = RbpForm(request.POST or None, instance=rbp, user=request.user)

    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "✏️ RBP record updated successfully.")
        params = urlencode({
            "q": query,
            "project_name_rbp": project_name_rbp,
            "resource_name_rbp": resource_name_rbp,
        })
        return redirect(f"{reverse('rbp_dashboard')}?{params}")

    rbps = filter_rbps(query=query, project_name_rbp=project_name_rbp, resource_name_rbp=resource_name_rbp, user=request.user, is_admin=is_admin)
    rbps_page = get_paginated_queryset(request, rbps)

    context = {
        "form": form,
        "mode": "edit",
        "rbp": rbp,
        "query": query,
        "project_name_rbp": project_name_rbp,
        "resource_name_rbp": resource_name_rbp,
        "readonly": False,
        "is_admin": is_admin,
        "rbps": rbps_page,
    }
    return render(request, "rbp/rbp_dashboard.html", context)

# G-Delete View-(Team delete only their own RBPs. Admin cannot delete) #
@login_required
def delete_rbp(request, pk):
    rbp = get_object_or_404(Rbp, pk=pk)
    is_admin = is_django_admin(request.user)

    if is_admin or rbp.created_by != request.user:
        raise PermissionDenied

    query = (request.GET.get("q") or "").strip()
    project_name_rbp = (request.GET.get("project_name_rbp") or "").strip()
    resource_name_rbp = (request.GET.get("resource_name_rbp") or "").strip()

    if request.method == "POST":
        name = f"{rbp.project_name_rbp} - {rbp.resource_name_rbp}"
        rbp.delete()
        messages.success(request, f"🗑️ RBP record '{name}' deleted successfully.")
        params = urlencode({
            "q": query,
            "project_name_rbp": project_name_rbp,
            "resource_name_rbp": resource_name_rbp,
        })
        return redirect(f"{reverse('rbp_dashboard')}?{params}")

    context = {
        "rbp": rbp,
        "query": query,
        "project_name_rbp": project_name_rbp,
        "resource_name_rbp": resource_name_rbp,
        "is_admin": is_admin,
        "readonly": True,
    }
    return render(request, "rbp/confirm_delete.html", context)

# H - Auto-Fill API (Used by JavaScript) #
def get_rbp_details(request, pk):
    resource = get_object_or_404(Resource, pk=pk)
    return JsonResponse({
        "unit": resource.unit or "",   # <-- match your model field name
    })

