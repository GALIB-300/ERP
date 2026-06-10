# A - Import Required Modules #
from django.shortcuts import render, get_object_or_404, redirect
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.contrib import messages
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from urllib.parse import urlencode
from django.db.models import Q, Sum
from django.http import JsonResponse

from .forms import CtvForm
from .models import Ctv

# B - Django Admin Check #
def is_django_admin(user):
    return user.is_superuser

# C - Filtering Function (Client Name) #
def filter_ctvs(query=None, client_name_ctv=None, user=None, is_admin=False, exclude_user=None):
    if is_admin:
        queryset = Ctv.objects.all()
    else:
        queryset = Ctv.objects.filter(created_by=user)

    if exclude_user:
        queryset = queryset.exclude(created_by=exclude_user)

    if query:
        queryset = queryset.filter(Q(client_name_ctv__client_name_pt__icontains=query))

    if client_name_ctv:
        queryset = queryset.filter(client_name_ctv__client_name_pt__icontains=client_name_ctv)

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

# E - Dashboard View (Admin view all CTV records. Team view/add their own CTV records) #
@login_required
def ctv_dashboard(request):
    query = request.GET.get("q", "").strip()
    client_name_ctv = request.GET.get("client_name_ctv", "").strip()
    is_admin = is_django_admin(request.user)

    form = None if is_admin else CtvForm(request.POST or None, user=request.user)

    ctvs = filter_ctvs(query=query, client_name_ctv=client_name_ctv,
                       user=request.user, is_admin=is_admin)

    ctvs_page = get_paginated_queryset(request, ctvs)

    if not is_admin and request.method == "POST" and form.is_valid():
        ctv = form.save(commit=False)
        ctv.created_by = request.user
        ctv.team = getattr(getattr(request.user, "ctv_profile", None),
                           "role", "manager_sales")
        ctv.save()
        messages.success(request, "✅ CTV detailed record created successfully.")
        return redirect(f"{reverse('ctv_dashboard')}?q={query}&client_name_ctv={client_name_ctv}")

    # Total-Contract Value & VAT & AIT Amount and Actual Contract Value #
    total_contract_value_ctv = ctvs.aggregate(Sum("contract_value_ctv"))["contract_value_ctv__sum"] or 0
    total_vat_ait_amount_ctv = ctvs.aggregate(Sum("vat_ait_amount_ctv"))["vat_ait_amount_ctv__sum"] or 0
    total_actual_contract_value_ctv = ctvs.aggregate(Sum("actual_contract_value_ctv"))["actual_contract_value_ctv__sum"] or 0

    context = {
        "ctvs": ctvs_page,
        "query": query,
        "client_name_ctv": client_name_ctv,
        "form": form,
        "mode": "list",
        "readonly": is_admin,
        "is_admin": is_admin,
        "total_contract_value_ctv": total_contract_value_ctv,
        "total_vat_ait_amount_ctv": total_vat_ait_amount_ctv,
        "total_actual_contract_value_ctv": total_actual_contract_value_ctv,
    }
    return render(request, "ctv/ctv_dashboard.html", context)

# F - Edit View (Team edit only their own CTV records. Admin cannot edit) #
@login_required
def edit_ctv(request, pk):
    ctv = get_object_or_404(Ctv, pk=pk)
    is_admin = is_django_admin(request.user)

    if not is_admin and ctv.created_by != request.user:
        raise PermissionDenied

    query = (request.GET.get("q") or "").strip()
    client_name_ctv = (request.GET.get("client_name_ctv") or "").strip()

    form = None if is_admin else CtvForm(request.POST or None, instance=ctv, user=request.user)

    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "✏️ CTV detailed record updated successfully.")
        params = urlencode({"q": query, "client_name_ctv": client_name_ctv})
        return redirect(f"{reverse('ctv_dashboard')}?{params}")

    ctvs = filter_ctvs(query=query, client_name_ctv=client_name_ctv,
                       user=request.user, is_admin=is_admin)
    ctvs_page = get_paginated_queryset(request, ctvs)

    context = {
        "form": form,
        "mode": "edit",
        "ctv": ctv,
        "query": query,
        "client_name_ctv": client_name_ctv,
        "readonly": False,
        "is_admin": is_admin,
        "ctvs": ctvs_page,
    }
    return render(request, "ctv/ctv_dashboard.html", context)

# G - Delete View (Team delete only their own CTV records. Admin cannot delete) #
@login_required
def delete_ctv(request, pk):
    ctv = get_object_or_404(Ctv, pk=pk)
    is_admin = is_django_admin(request.user)

    if not is_admin and ctv.created_by != request.user:
        raise PermissionDenied

    query = (request.GET.get("q") or "").strip()
    client_name_ctv = (request.GET.get("client_name_ctv") or "").strip()

    if request.method == "POST":
        name = ctv.client_name_ctv.client_name_pt if ctv.client_name_ctv else "Unknown Client"
        ctv.delete()
        messages.success(request, f"🗑️ CTV record for client '{name}' deleted successfully.")
        params = urlencode({"q": query, "client_name_ctv": client_name_ctv})
        return redirect(f"{reverse('ctv_dashboard')}?{params}")

    context = {
        "ctv": ctv,
        "query": query,
        "client_name_ctv": client_name_ctv,
        "is_admin": is_admin,
        "readonly": True,
    }
    return render(request, "ctv/confirm_delete.html", context)