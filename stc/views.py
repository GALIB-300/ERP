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

from .forms import StcForm
from .models import Stc

# B-Django Admin Check #
def is_django_admin(user):
    return user.is_superuser

# C-Filtering Function-(Project Name and PO No and Supplier Name-Based) #
def filter_stcs(query=None, project_name_stc=None, po_no_stc=None, supplier_name_stc=None,
                user=None, is_admin=False, exclude_user=None):

    # Base queryset #
    if is_admin:
        queryset = Stc.objects.all()
    else:
        queryset = Stc.objects.filter(created_by=user)

    # Exclude specific user if provided #
    if exclude_user:
        queryset = queryset.exclude(created_by=exclude_user)

    # Free text search across project name, PO no, and supplier name #
    if query:
        queryset = queryset.filter(
            Q(project_name_stc__name_of_project__icontains=query) |
            Q(po_no_stc__icontains=query) |
            Q(supplier_name_stc__name_of_supplier__icontains=query)
        )

    # Filter by Project name #
    if project_name_stc:
        queryset = queryset.filter(
            project_name_stc__name_of_project__icontains=project_name_stc
        )

    # Filter by PO No #
    if po_no_stc:
        queryset = queryset.filter(
            po_no_stc__icontains=po_no_stc
        )

    # Filter by Supplier name #
    if supplier_name_stc:
        queryset = queryset.filter(
            supplier_name_stc__name_of_supplier__icontains=supplier_name_stc
        )

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

# E-Dashboard View-(Admin view all STCs. Team view/add their own STCs) #
@login_required
def stc_dashboard(request):
    # Step-(A1)-Collect query parameters from URL #
    query = request.GET.get("q", "").strip()
    project_name_stc = request.GET.get("project_name_stc", "").strip()
    po_no_stc = request.GET.get("po_no_stc", "").strip()
    supplier_name_stc = request.GET.get("supplier_name_stc", "").strip()

    # Step-(A2)-Check if user is admin #
    is_admin = is_django_admin(request.user)

    # Step-(A3)-Initialize form only for non-admin users #
    form = None if is_admin else StcForm(request.POST or None, user=request.user)

    # Step-(A4)-Centralized data filter #
    stcs = filter_stcs(
        query=query,
        project_name_stc=project_name_stc,
        po_no_stc=po_no_stc,
        supplier_name_stc=supplier_name_stc,
        user=request.user,
        is_admin=is_admin
    )

    # Step-(A5)-Apply pagination #
    stcs_page = get_paginated_queryset(request, stcs)

    # Step-(A6)-Add new STC only if user is NOT admin #
    if not is_admin and request.method == "POST" and form.is_valid():
        stc = form.save(commit=False)
        stc.created_by = request.user
        stc.team = getattr(
            getattr(request.user, "stc_profile", None),
            "role",
            "manager_construction"   # default role for team users
        )
        stc.save()
        messages.success(request, "✅ STC record created successfully.")
        return redirect(
            f"{reverse('stc_dashboard')}?q={query}&project_name_stc={project_name_stc}&po_no_stc={po_no_stc}&supplier_name_stc={supplier_name_stc}"
        )

    # Step-(A8)-Prepare context for template #
    context = {
        "stcs": stcs_page,
        "query": query,
        "project_name_stc": project_name_stc,
        "po_no_stc": po_no_stc,
        "supplier_name_stc": supplier_name_stc,
        "form": form,
        "mode": "list",
        "readonly": is_admin,   # Admins are readonly
        "is_admin": is_admin,
    }

    # Step-(A9)-Render template #
    return render(request, "stc/stc_dashboard.html", context)

# F-Edit View-(Team edit only their own STCs. Admin cannot edit) #
@login_required
def edit_stc(request, pk):
    stc = get_object_or_404(Stc, pk=pk)
    is_admin = is_django_admin(request.user)

    # Admins cannot edit, and team members can only edit their own STCs
    if is_admin or stc.created_by != request.user:
        raise PermissionDenied

    query = (request.GET.get("q") or "").strip()
    project_name_stc = (request.GET.get("project_name_stc") or "").strip()
    po_no_stc = (request.GET.get("po_no_stc") or "").strip()
    supplier_name_stc = (request.GET.get("supplier_name_stc") or "").strip()

    form = StcForm(request.POST or None, instance=stc, user=request.user)

    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "✏️ STC record updated successfully.")
        params = urlencode({
            "q": query,
            "project_name_stc": project_name_stc,
            "po_no_stc": po_no_stc,
            "supplier_name_stc": supplier_name_stc,
        })
        return redirect(f"{reverse('stc_dashboard')}?{params}")

    stcs = filter_stcs(
        query=query,
        project_name_stc=project_name_stc,
        po_no_stc=po_no_stc,
        supplier_name_stc=supplier_name_stc,
        user=request.user,
        is_admin=is_admin
    )
    stcs_page = get_paginated_queryset(request, stcs)

    context = {
        "form": form,
        "mode": "edit",
        "stc": stc,
        "query": query,
        "project_name_stc": project_name_stc,
        "po_no_stc": po_no_stc,
        "supplier_name_stc": supplier_name_stc,
        "readonly": False,
        "is_admin": is_admin,
        "stcs": stcs_page,
    }
    return render(request, "stc/stc_dashboard.html", context)

# G-Delete View-(Team delete only their own STCs. Admin cannot delete) #
@login_required
def delete_stc(request, pk):
    stc = get_object_or_404(Stc, pk=pk)
    is_admin = is_django_admin(request.user)

    # Admins cannot delete, and team members can only delete their own STCs
    if is_admin or stc.created_by != request.user:
        raise PermissionDenied

    query = (request.GET.get("q") or "").strip()
    project_name_stc = (request.GET.get("project_name_stc") or "").strip()
    po_no_stc = (request.GET.get("po_no_stc") or "").strip()
    supplier_name_stc = (request.GET.get("supplier_name_stc") or "").strip()

    if request.method == "POST":
        name = f"{stc.project_name_stc} - {stc.supplier_name_stc}"
        stc.delete()
        messages.success(request, f"🗑️ STC record '{name}' deleted successfully.")
        params = urlencode({
            "q": query,
            "project_name_stc": project_name_stc,
            "po_no_stc": po_no_stc,
            "supplier_name_stc": supplier_name_stc,
        })
        return redirect(f"{reverse('stc_dashboard')}?{params}")

    context = {
        "stc": stc,
        "query": query,
        "project_name_stc": project_name_stc,
        "po_no_stc": po_no_stc,
        "supplier_name_stc": supplier_name_stc,
        "is_admin": is_admin,
        "readonly": True,
    }
    return render(request, "stc/confirm_delete.html", context)
