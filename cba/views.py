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
from django.db.models import Sum

from .forms import CbaForm
from .models import Cba

# B - Django Admin Check #
def is_django_admin(user):
    return user.is_superuser

# C - Filtering Function (Client Name & WO No & Bill No-Based) #
def filter_cbas(query=None, client_name_cba=None, wo_no_cba=None, bill_no_cba=None,
                user=None, is_admin=False, exclude_user=None):
    # Base queryset
    queryset = Cba.objects.all() if is_admin else Cba.objects.filter(created_by=user)

    # Exclude specific user if provided
    if exclude_user:
        queryset = queryset.exclude(created_by=exclude_user)

    # Free text search across client name (Pt field) OR WO No OR Bill No
    if query:
        queryset = queryset.filter(
            Q(client_name_cba__client_name_ctv__client_name_pt__icontains=query) |
            Q(wo_no_cba__wo_no_ctv__icontains=query) |
            Q(bill_no_cba__icontains=query)
        )

    # Filter by client name (Pt field)
    if client_name_cba:
        queryset = queryset.filter(
            client_name_cba__client_name_ctv__client_name_pt__icontains=client_name_cba
        )

    # Filter by WO No
    if wo_no_cba:
        queryset = queryset.filter(wo_no_cba__wo_no_ctv__icontains=wo_no_cba)

    # Filter by Bill No
    if bill_no_cba:
        queryset = queryset.filter(bill_no_cba__icontains=bill_no_cba)

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

# E - Dashboard View (Admin view all CBA records. Team view/add their own CBA records) #
@login_required
def cba_dashboard(request):
    query = request.GET.get("q", "").strip()
    client_name_cba = request.GET.get("client_name_cba", "").strip()
    wo_no_cba = request.GET.get("wo_no_cba", "").strip()
    bill_no_cba = request.GET.get("bill_no_cba", "").strip()
    is_admin = is_django_admin(request.user)

    # Form only for team members #
    form = None if is_admin else CbaForm(request.POST or None, user=request.user)

    # Filter CBA records #
    cbas = filter_cbas(
        query=query,
        client_name_cba=client_name_cba,
        wo_no_cba=wo_no_cba,
        bill_no_cba=bill_no_cba,
        user=request.user,
        is_admin=is_admin
    )

    # Paginate CBA records #
    cbas_page = get_paginated_queryset(request, cbas)

    # Save new CBA record (team only) #
    if not is_admin and request.method == "POST" and form.is_valid():
        cba = form.save(commit=False)
        cba.created_by = request.user
        cba.team = getattr(
            getattr(request.user, "cba_profile", None),
            "role",
            "manager_sales"   # default role for team members
        )
        cba.save()
        messages.success(request, "✅ CBA detailed record created successfully.")
        return redirect(
            f"{reverse('cba_dashboard')}?q={query}&client_name_cba={client_name_cba}&wo_no_cba={wo_no_cba}&bill_no_cba={bill_no_cba}"
        )

    # Total-Bill Amount & VAT & AIT Amount and Actual Bill Amount #
    total_bill_amount_cba = cbas.aggregate(Sum("bill_amount_cba"))["bill_amount_cba__sum"] or 0
    total_vat_ait_amount_cba = cbas.aggregate(Sum("vat_ait_amount_cba"))["vat_ait_amount_cba__sum"] or 0
    total_actual_bill_amount_cba = cbas.aggregate(Sum("actual_bill_amount_cba"))["actual_bill_amount_cba__sum"] or 0

    context = {
        "cbas": cbas_page,
        "query": query,
        "client_name_cba": client_name_cba,
        "wo_no_cba": wo_no_cba,
        "bill_no_cba": bill_no_cba,
        "form": form,
        "mode": "list",
        "readonly": is_admin,
        "is_admin": is_admin,
        "total_bill_amount_cba": total_bill_amount_cba,
        "total_vat_ait_amount_cba": total_vat_ait_amount_cba,
        "total_actual_bill_amount_cba": total_actual_bill_amount_cba,
    }
    return render(request, "cba/cba_dashboard.html", context)

# F - Edit View (Team edit only their own CBA records. Admin cannot edit) #
@login_required
def edit_cba(request, pk):
    cba = get_object_or_404(Cba, pk=pk)
    is_admin = is_django_admin(request.user)

    # Restrict editing to creator only #
    if not is_admin and cba.created_by != request.user:
        raise PermissionDenied

    query = (request.GET.get("q") or "").strip()
    client_name_cba = (request.GET.get("client_name_cba") or "").strip()
    wo_no_cba = (request.GET.get("wo_no_cba") or "").strip()
    bill_no_cba = (request.GET.get("bill_no_cba") or "").strip()

    form = None if is_admin else CbaForm(request.POST or None, user=request.user, instance=cba)

    # Save updates #
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "✏️ CBA detailed record updated successfully.")
        params = urlencode({
            "q": query,
            "client_name_cba": client_name_cba,
            "wo_no_cba": wo_no_cba,
            "bill_no_cba": bill_no_cba,
        })
        return redirect(f"{reverse('cba_dashboard')}?{params}")

    # Refresh CBA list #
    cbas = filter_cbas(
        query=query,
        client_name_cba=client_name_cba,
        wo_no_cba=wo_no_cba,
        bill_no_cba=bill_no_cba,
        user=request.user,
        is_admin=is_admin
    )
    cbas_page = get_paginated_queryset(request, cbas)

    context = {
        "form": form,
        "mode": "edit",
        "cba": cba,
        "query": query,
        "client_name_cba": client_name_cba,
        "wo_no_cba": wo_no_cba,
        "bill_no_cba": bill_no_cba,
        "readonly": False,
        "is_admin": is_admin,
        "cbas": cbas_page,
    }
    return render(request, "cba/cba_dashboard.html", context)

# G - Delete View (Team delete only their own CBA records. Admin cannot delete) #
@login_required
def delete_cba(request, pk):
    cba = get_object_or_404(Cba, pk=pk)
    is_admin = is_django_admin(request.user)

    # Restrict deletion to creator only #
    if not is_admin and cba.created_by != request.user:
        raise PermissionDenied

    query = (request.GET.get("q") or "").strip()
    client_name_cba = (request.GET.get("client_name_cba") or "").strip()
    wo_no_cba = (request.GET.get("wo_no_cba") or "").strip()
    bill_no_cba = (request.GET.get("bill_no_cba") or "").strip()

    # Confirm deletion #
    if request.method == "POST":
        name = cba.client_name_cba.client_name_ctv if cba.client_name_cba else "Unknown Client"
        cba.delete()
        messages.success(request, f"🗑️ CBA record for client '{name}' deleted successfully.")
        params = urlencode({
            "q": query,
            "client_name_cba": client_name_cba,
            "wo_no_cba": wo_no_cba,
            "bill_no_cba": bill_no_cba,
        })
        return redirect(f"{reverse('cba_dashboard')}?{params}")

    context = {
        "cba": cba,
        "query": query,
        "client_name_cba": client_name_cba,
        "wo_no_cba": wo_no_cba,
        "bill_no_cba": bill_no_cba,
        "is_admin": is_admin,
        "readonly": True,
    }
    return render(request, "cba/confirm_delete.html", context)

