# A - Import Required Modules #
from django.shortcuts import render, get_object_or_404, redirect
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.contrib import messages
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from urllib.parse import urlencode
from django.db.models import Q
from django.http import JsonResponse
from datetime import timedelta, date

from .forms import RipForm
from .models import Rip
from rbp.models import Rbp

# B - Django Admin Check #
def is_django_admin(user):
    return user.is_superuser

# C - Filtering Function (Project & Resource Based) #
def filter_rips(query=None, project_name_rip=None, resource_name_rip=None,
                user=None, is_admin=False, exclude_user=None):
    # Base queryset #
    queryset = Rip.objects.all() if is_admin else Rip.objects.filter(created_by=user)

    # Exclude specific user if provided #
    if exclude_user:
        queryset = queryset.exclude(created_by=exclude_user)

    # Free text search across project & resource fields #
    if query:
        queryset = queryset.filter(
            Q(project_name_rip__icontains=query) |
            Q(resource_name_rip__icontains=query)
        )

    # Filter by project name #
    if project_name_rip:
        queryset = queryset.filter(project_name_rip__icontains=project_name_rip)

    # Filter by resource name #
    if resource_name_rip:
        queryset = queryset.filter(resource_name_rip__icontains=resource_name_rip)

    return queryset

# D - Reusable Pagination Function #
def get_paginated_queryset(request, queryset, per_page=10):
    paginator = Paginator(queryset, per_page)
    page_number = request.GET.get("page")

    try:
        return paginator.page(page_number)
    except PageNotAnInteger:
        return paginator.page(1)
    except EmptyPage:
        return paginator.page(paginator.num_pages)

# E - Dashboard View (Admin view all RIPs. Team view/add their own RIPs) #
@login_required
def rip_dashboard(request):
    query = request.GET.get("q", "").strip()
    project_name_rip = request.GET.get("project_name_rip", "").strip()
    resource_name_rip = request.GET.get("resource_name_rip", "").strip()

    is_admin = is_django_admin(request.user)
    form = None if is_admin else RipForm(request.POST or None, user=request.user)

    rips = filter_rips(
        query=query,
        project_name_rip=project_name_rip,
        resource_name_rip=resource_name_rip,
        user=request.user,
        is_admin=is_admin
    )

    rips_page = get_paginated_queryset(request, rips)

    # Expand each record into daily rows
    expanded_rows = []
    for r in rips:
        start = r.effective_from
        end = date.today() - timedelta(days=1)  # always yesterday
        current = start
        while current <= end:
            expanded_rows.append({
                "project": r.project_name_rip,
                "resource": r.resource_name_rip,
                "supplier": r.supplier_name_rip,
                "unit": r.resource_unit_rip,
                "base_price": r.base_price_rip,
                "date": current,
                "increase_decrease": r.increase_decrease_price_rip,
                "actual_price": r.actual_base_price_rip,
            })
            current += timedelta(days=1)

    if not is_admin and request.method == "POST" and form.is_valid():
        rip = form.save(commit=False)
        rip.created_by = request.user
        rip.team = getattr(
            getattr(request.user, "rip_profile", None),
            "role",
            "manager_procurement"
        )
        rip.save()
        messages.success(request, "✅ RIP record created successfully.")
        return redirect(
            f"{reverse('rip_dashboard')}?q={query}&project_name_rip={project_name_rip}&resource_name_rip={resource_name_rip}"
        )

    context = {
        "rips": rips_page,
        "expanded_rows": expanded_rows,
        "query": query,
        "project_name_rip": project_name_rip,
        "resource_name_rip": resource_name_rip,
        "form": form,
        "mode": "list",
        "readonly": is_admin,
        "is_admin": is_admin,
    }
    return render(request, "rip/rip_dashboard.html", context)

# F - Edit View (Team edit only their own RIPs. Admin cannot edit) #
@login_required
def edit_rip(request, pk):
    rip = get_object_or_404(Rip, pk=pk)
    is_admin = is_django_admin(request.user)

    if is_admin or rip.created_by != request.user:
        raise PermissionDenied

    query = (request.GET.get("q") or "").strip()
    project_name_rip = (request.GET.get("project_name_rip") or "").strip()
    resource_name_rip = (request.GET.get("resource_name_rip") or "").strip()

    form = RipForm(request.POST or None, instance=rip, user=request.user)

    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "✏️ RIP record updated successfully.")
        params = urlencode({
            "q": query,
            "project_name_rip": project_name_rip,
            "resource_name_rip": resource_name_rip,
        })
        return redirect(f"{reverse('rip_dashboard')}?{params}")

    rips = filter_rips(query=query, project_name_rip=project_name_rip,
                       resource_name_rip=resource_name_rip,
                       user=request.user, is_admin=is_admin)
    rips_page = get_paginated_queryset(request, rips)

    context = {
        "form": form,
        "mode": "edit",
        "rip": rip,
        "query": query,
        "project_name_rip": project_name_rip,
        "resource_name_rip": resource_name_rip,
        "readonly": False,
        "is_admin": is_admin,
        "rips": rips_page,
    }
    return render(request, "rip/rip_dashboard.html", context)

# G - Delete View (Team delete only their own RIPs. Admin cannot delete) #
@login_required
def delete_rip(request, pk):
    rip = get_object_or_404(Rip, pk=pk)
    is_admin = is_django_admin(request.user)

    if is_admin or rip.created_by != request.user:
        raise PermissionDenied

    query = (request.GET.get("q") or "").strip()
    project_name_rip = (request.GET.get("project_name_rip") or "").strip()
    resource_name_rip = (request.GET.get("resource_name_rip") or "").strip()

    if request.method == "POST":
        name = f"{rip.project_name_rip} - {rip.resource_name_rip}"
        rip.delete()
        messages.success(request, f"🗑️ RIP record '{name}' deleted successfully.")
        params = urlencode({
            "q": query,
            "project_name_rip": project_name_rip,
            "resource_name_rip": resource_name_rip,
        })
        return redirect(f"{reverse('rip_dashboard')}?{params}")

    context = {
        "rip": rip,
        "query": query,
        "project_name_rip": project_name_rip,
        "resource_name_rip": resource_name_rip,
        "is_admin": is_admin,
        "readonly": True,
    }
    return render(request, "rip/confirm_delete.html", context)

# H - Auto-Fill API (Used by JavaScript) #
def get_rip_details(request, pk):
    rbp = get_object_or_404(Rbp, pk=pk)
    return JsonResponse({
        "project_name_rbp": str(rbp.project_name_rbp) if rbp.project_name_rbp else "",
        "resource_name_rbp": str(rbp.resource_name_rbp) if rbp.resource_name_rbp else "",
        "resource_unit_rbp": str(rbp.resource_unit_rbp) if rbp.resource_unit_rbp else "",
        "supplier_name_rbp": str(rbp.supplier_name_rbp) if rbp.supplier_name_rbp else "",
        "resource_base_price": str(rbp.resource_base_price) if rbp.resource_base_price else "",
    })
