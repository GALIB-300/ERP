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
from datetime import datetime

from .forms import PrForm
from .models import Pr
from resource.models import Resource
from company.models import Company

# B-Django Admin Check #
def is_django_admin(user):
    return user.is_superuser

# C-Filtering Function-(Project name & PR date and PR no-Based) #
def filter_prs(query=None, project_name_pr=None, requisition_date_pr=None, requisition_no_pr=None,
               user=None, is_admin=False, exclude_user=None):
    # Base queryset #
    if is_admin:
        queryset = Pr.objects.all()
    else:
        queryset = Pr.objects.filter(created_by=user)

    # Exclude specific user if provided #
    if exclude_user:
        queryset = queryset.exclude(created_by=exclude_user)

    # Free text search across project, requisition date & requisition no fields #
    if query:
        queryset = queryset.filter(
            Q(project_name_pr__name_of_project__icontains=query) |
            Q(requisition_date_pr__icontains=query) |
            Q(requisition_no_pr__icontains=query)
        )

    # Filter by project name #
    if project_name_pr:
        queryset = queryset.filter(project_name_pr__name_of_project__icontains=project_name_pr)

    # Filter by requisition date (exact match) #
    if requisition_date_pr:
        try:
            parsed_date = datetime.strptime(requisition_date_pr, "%d-%m-%Y").date()
            queryset = queryset.filter(requisition_date_pr=parsed_date)
        except ValueError:
            queryset = queryset.none()

    # Filter by requisition number #
    if requisition_no_pr:
        queryset = queryset.filter(requisition_no_pr__icontains=requisition_no_pr)

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

# E-Dashboard View-(Admin view all PRs. Team view/add their own PRs) #
@login_required
def pr_dashboard(request):
    query = request.GET.get("q", "").strip()
    project_name_pr = request.GET.get("project_name_pr", "").strip()
    requisition_date_pr = request.GET.get("requisition_date_pr", "").strip()
    requisition_no_pr = request.GET.get("requisition_no_pr", "").strip()

    is_admin = is_django_admin(request.user)
    form = None if is_admin else PrForm(request.POST or None, user=request.user)

    prs = filter_prs(
        query=query,
        project_name_pr=project_name_pr,
        requisition_date_pr=requisition_date_pr,
        requisition_no_pr=requisition_no_pr,
        user=request.user,
        is_admin=is_admin
    )

    prs_page = get_paginated_queryset(request, prs)

    if not is_admin and request.method == "POST" and form.is_valid():
        pr = form.save(commit=False)
        pr.created_by = request.user
        pr.team = getattr(
            getattr(request.user, "pr_profile", None),
            "role",
            "manager_construction"
        )
        pr.save()
        messages.success(request, "✅ PR record created successfully.")
        return redirect(
            f"{reverse('pr_dashboard')}?q={query}&project_name_pr={project_name_pr}&requisition_date_pr={requisition_date_pr}&requisition_no_pr={requisition_no_pr}"
        )

    context = {
        "prs": prs_page,
        "query": query,
        "project_name_pr": project_name_pr,
        "requisition_date_pr": requisition_date_pr,
        "requisition_no_pr": requisition_no_pr,
        "form": form,
        "mode": "list",
        "readonly": is_admin,
        "is_admin": is_admin,
    }
    return render(request, "pr/pr_dashboard.html", context)

# F-Edit View-(Team edit only their own PRs. Admin cannot edit) #
@login_required
def edit_pr(request, pk):
    pr = get_object_or_404(Pr, pk=pk)
    is_admin = is_django_admin(request.user)

    # Admins cannot edit, and team members can only edit their own PRs
    if is_admin or pr.created_by != request.user:
        raise PermissionDenied

    query = (request.GET.get("q") or "").strip()
    project_name_pr = (request.GET.get("project_name_pr") or "").strip()
    requisition_date_pr = (request.GET.get("requisition_date_pr") or "").strip()
    requisition_no_pr = (request.GET.get("requisition_no_pr") or "").strip()

    form = PrForm(request.POST or None, instance=pr, user=request.user)

    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "✏️ PR record updated successfully.")
        params = urlencode({
            "q": query,
            "project_name_pr": project_name_pr,
            "requisition_date_pr": requisition_date_pr,
            "requisition_no_pr": requisition_no_pr,
        })
        return redirect(f"{reverse('pr_dashboard')}?{params}")

    prs = filter_prs(
        query=query,
        project_name_pr=project_name_pr,
        requisition_date_pr=requisition_date_pr,
        requisition_no_pr=requisition_no_pr,
        user=request.user,
        is_admin=is_admin
    )
    prs_page = get_paginated_queryset(request, prs)

    context = {
        "form": form,
        "mode": "edit",
        "pr": pr,
        "query": query,
        "project_name_pr": project_name_pr,
        "requisition_date_pr": requisition_date_pr,
        "requisition_no_pr": requisition_no_pr,
        "readonly": False,
        "is_admin": is_admin,
        "prs": prs_page,
    }
    return render(request, "pr/pr_dashboard.html", context)

# G-Delete View-(Team delete only their own PRs. Admin cannot delete) #
@login_required
def delete_pr(request, pk):
    pr = get_object_or_404(Pr, pk=pk)
    is_admin = is_django_admin(request.user)

    # Admins cannot delete, and team members can only delete their own PRs
    if is_admin or pr.created_by != request.user:
        raise PermissionDenied

    query = (request.GET.get("q") or "").strip()
    project_name_pr = (request.GET.get("project_name_pr") or "").strip()
    requisition_date_pr = (request.GET.get("requisition_date_pr") or "").strip()
    requisition_no_pr = (request.GET.get("requisition_no_pr") or "").strip()

    if request.method == "POST":
        name = f"{pr.project_name_pr} - {pr.resource_name_pr}"
        pr.delete()
        messages.success(request, f"🗑️ PR record '{name}' deleted successfully.")
        params = urlencode({
            "q": query,
            "project_name_pr": project_name_pr,
            "requisition_date_pr": requisition_date_pr,
            "requisition_no_pr": requisition_no_pr,
        })
        return redirect(f"{reverse('pr_dashboard')}?{params}")

    context = {
        "pr": pr,
        "query": query,
        "project_name_pr": project_name_pr,
        "requisition_date_pr": requisition_date_pr,
        "requisition_no_pr": requisition_no_pr,
        "is_admin": is_admin,
        "readonly": True,
    }
    return render(request, "pr/confirm_delete.html", context)

# H - Auto-Fill API (Used by JavaScript) #
def get_pr_details(request, pk):
    resource = get_object_or_404(Resource, pk=pk)
    return JsonResponse({
        "unit": resource.unit or "",   # <-- match your model field name
    })

# I - Print Dashboard View #
@login_required
def print_dashboard(request):
    project_name_pr = request.GET.get("project_name_pr")
    requisition_date_pr = request.GET.get("requisition_date_pr")
    requisition_no_pr = request.GET.get("requisition_no_pr")

    pr_list = Pr.objects.all()

    if project_name_pr:
        pr_list = pr_list.filter(project_name_pr__name_of_project__iexact=project_name_pr)

    if requisition_date_pr:
        try:
            parsed_date = datetime.strptime(requisition_date_pr, "%d-%m-%Y").date()
            pr_list = pr_list.filter(requisition_date_pr=parsed_date)
        except ValueError:
            pr_list = pr_list.none()

    if requisition_no_pr:
        pr_list = pr_list.filter(requisition_no_pr__iexact=requisition_no_pr)

    pr_header = pr_list.first()
    company = Company.objects.filter(created_by=request.user).first()

    return render(request, "pr/print_dashboard.html", {
        "pr": pr_header,
        "company": company,
        "pr_list": pr_list,
    })