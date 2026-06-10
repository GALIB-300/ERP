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
from datetime import datetime

from .forms import RwcForm
from .models import Rwc, Company

# B - Django Admin Check #
def is_django_admin(user):
    return user.is_superuser

# C-Filtering Function-(Requisition Date-Based) #
def filter_rwcs(query=None, requisition_date=None, user=None, is_admin=False, exclude_user=None):
    # Base queryset
    if is_admin:
        queryset = Rwc.objects.all()
    else:
        queryset = Rwc.objects.filter(created_by=user)

    # Exclude specific user if provided
    if exclude_user:
        queryset = queryset.exclude(created_by=exclude_user)

    # Free text search across requisition_no (string field)
    if query:
        queryset = queryset.filter(
            Q(requisition_no__icontains=query)
        )

    # Filter by requisition_date (exact match)
    if requisition_date:
        try:
            # Convert string like "01-05-2026" into a date object
            parsed_date = datetime.strptime(requisition_date, "%d-%m-%Y").date()
            queryset = queryset.filter(requisition_date=parsed_date)
        except ValueError:
            # If parsing fails, no results
            queryset = queryset.none()

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

# E-Dashboard View-(Admin view all requisitions. Team view/add their own requisitions) #
# Step-(A)-Dashboard view #
@login_required
def rwc_dashboard(request):
    # Step-(A1)-Search Query parameter-(q)-from the URL #
    query = request.GET.get("q", "").strip()

    # Step-(A2)-Requisition Date-based-query parameter-from the URL #
    requisition_date = request.GET.get("requisition_date", "").strip()

    # Step-(A3)-Check if user is admin (custom helper) #
    is_admin = is_django_admin(request.user)

    # Step-(A4)-Initialize form only for non-admin users #
    form = None if is_admin else RwcForm(request.POST or None, user=request.user)

    # Step-(A5)-Centralized data filter #
    rwcs = filter_rwcs(
        query=query,
        requisition_date=requisition_date,
        user=request.user,
        is_admin=is_admin
    )

    # Apply pagination #
    rwcs_page = get_paginated_queryset(request, rwcs)

    # Step-(A6)-Add new requisition only if user is NOT admin #
    if not is_admin and request.method == "POST" and form.is_valid():
        requisition = form.save(commit=False)
        requisition.created_by = request.user
        requisition.team = getattr(
            getattr(request.user, "rwc_profile", None),
            "role",
            "manager_construction"   # default role for team
        )
        requisition.manager_construction = request.user
        requisition.save()
        messages.success(request, "✅ Requisition record created successfully.")
        return redirect(
            f"{reverse('rwc_dashboard')}?q={query}&requisition_date={requisition_date}"
        )

    # Step-(A7)-Prepare context for template #
    context = {
        "rwcs": rwcs_page,
        "query": query,
        "requisition_date": requisition_date,
        "form": form,
        "mode": "list",
        "readonly": is_admin,  # Admins are readonly
        "is_admin": is_admin,
    }

    # Step-(A8)-Render template #
    return render(request, "rwc/rwc_dashboard.html", context)

# F-Edit View-(Team edit only their own requisitions. Admin cannot edit) #
# Step-(A)-Edit view #
@login_required
def edit_rwc(request, pk):
    # Step-(A1)-Get requisition by ID #
    requisition = get_object_or_404(Rwc, pk=pk)

    # Step-(A2)-Check if user is admin (custom helper) #
    is_admin = is_django_admin(request.user)

    # Step-(A3)-Permission check based on Admin & Team #
    if is_admin or requisition.created_by != request.user:
        raise PermissionDenied

    # Step-(A4)-Search Query parameter-(q)-from the URL #
    query = (request.GET.get("q") or "").strip()

    # Step-(A5)-Requisition Date-based-query parameter-from the URL #
    requisition_date = (request.GET.get("requisition_date") or "").strip()

    # Step-(A6)-Initialize form with requisition instance #
    form = RwcForm(request.POST or None, instance=requisition)

    # Step-(A7)-Edit requisition based on team users #
    if request.method == "POST" and form.is_valid():
        updated = form.save(commit=False)
        updated.updated_by = request.user
        updated.save()
        messages.success(request, "✏️ Requisition record updated successfully.")
        params = urlencode({
            "q": query,
            "requisition_date": requisition_date,
        })
        return redirect(f"{reverse('rwc_dashboard')}?{params}")

    # Step-(A8)-Centralized data filter #
    rwcs = filter_rwcs(
        query=query,
        requisition_date=requisition_date,
        user=request.user,
        is_admin=is_admin
    )

    # Apply pagination #
    rwcs_page = get_paginated_queryset(request, rwcs)

    # Step-(A9)-Prepare context for edit template #
    context = {
        "form": form,
        "mode": "edit",
        "rwc": requisition,
        "query": query,
        "requisition_date": requisition_date,
        "readonly": False,
        "is_admin": is_admin,
        "rwcs": rwcs_page,
    }

    # Step-(A10)-Render template #
    return render(request, "rwc/rwc_dashboard.html", context)

# G-Delete View-(Team delete only their own requisitions. Admin cannot delete) #
# Step-(A)-Delete view #
@login_required
def delete_rwc(request, pk):
    # Step-(A1)-Get requisition by ID #
    requisition = get_object_or_404(Rwc, pk=pk)

    # Step-(A2)-Check if user is admin (custom helper) #
    is_admin = is_django_admin(request.user)

    # Step-(A3)-Permission check based on Admin & Team #
    if is_admin or requisition.created_by != request.user:
        raise PermissionDenied

    # Step-(A4)-Search Query parameter-(q)-from the URL #
    query = (request.GET.get("q") or "").strip()

    # Step-(A5)-Requisition Date-based-query parameter-from the URL #
    requisition_date = (request.GET.get("requisition_date") or "").strip()

    # Step-(A6)-Delete requisition-(only team users can delete) #
    if request.method == "POST":
        req_no = requisition.requisition_no
        requisition.delete()
        messages.success(request, f"🗑️ Requisition '{req_no}' deleted successfully.")
        params = urlencode({
            "q": query,
            "requisition_date": requisition_date,
        })
        return redirect(f"{reverse('rwc_dashboard')}?{params}")

    # Step-(A7)-Prepare context for delete confirmation template #
    context = {
        "rwc": requisition,
        "query": query,
        "requisition_date": requisition_date,
        "is_admin": is_admin,
        "readonly": True    # Admins are readonly, team confirm delete
    }

    # Step-(A8)-Render delete confirmation template #
    return render(request, "rwc/confirm_delete.html", context)


@login_required
def rwc_print_view(request, pk):
    """
    ERP-style requisition print view:
    - Fetches company info for the logged-in user
    - Loads the requisition record by primary key
    - Retrieves related requisitions for the same project
    - Renders the print template (rwc/rwc_print.html)
    """

    # 🔹 Company info for the logged-in user
    company = get_object_or_404(Company, created_by=request.user)

    # 🔹 Specific requisition record
    rwc = get_object_or_404(Rwc, pk=pk)

    # 🔹 Related requisitions for the same project (for list table)
    rwc_list = Rwc.objects.filter(
        project_name_rwc=rwc.project_name_rwc
    ).order_by('requisition_date')

    # 🔹 Render the ERP-style print template
    return render(request, 'rwc/rwc_print.html', {
        'company': company,
        'rwc': rwc,
        'rwc_list': rwc_list,
    })