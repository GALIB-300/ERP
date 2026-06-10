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

from .forms import SbForm
from .models import Sb
from po.models import Po   

# B - Django Admin Check #
def is_django_admin(user):
    return user.is_superuser

# C - Filtering Function (Project, Supplier & PO Number Based) #
def filter_sbs(query=None, project_name_sb=None, supplier_name_sb=None, po_number_sb=None,
               user=None, is_admin=False, exclude_user=None):
    queryset = Sb.objects.all() if is_admin else Sb.objects.filter(created_by=user)

    if exclude_user:
        queryset = queryset.exclude(created_by=exclude_user)

    # Free text search across project, supplier & PO fields
    if query:
        queryset = queryset.filter(
            Q(project_name_sb__project_name_po__name_of_project__icontains=query) |
            Q(supplier_name_sb__supplier_name_po__name_of_supplier__icontains=query) |
            Q(po_number_sb__po_no__icontains=query)   # <-- corrected lookup
        )

    # Filter by project name #
    if project_name_sb:
        queryset = queryset.filter(
            project_name_sb__project_name_po__name_of_project__icontains=project_name_sb
        )

    # Filter by supplier name #
    if supplier_name_sb:
        queryset = queryset.filter(
            supplier_name_sb__supplier_name_po__name_of_supplier__icontains=supplier_name_sb
        )

    # Filter by PO number #
    if po_number_sb:
        queryset = queryset.filter(
            po_number_sb__po_no__icontains=po_number_sb   # <-- corrected lookup
        )

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

# E-Dashboard View-(Admin view all SBs. Team view/add their own SBs) #
@login_required
def sb_dashboard(request):
    # Step-(A1)-Collect query parameters from URL #
    query = request.GET.get("q", "").strip()
    project_name_sb = request.GET.get("project_name_sb", "").strip()
    po_number_sb = request.GET.get("po_number_sb", "").strip()
    supplier_name_sb = request.GET.get("supplier_name_sb", "").strip()

    # Step-(A2)-Check if user is admin #
    is_admin = is_django_admin(request.user)

    # Step-(A3)-Initialize form only for non-admin users #
    form = None if is_admin else SbForm(request.POST or None, user=request.user)

    # Step-(A4)-Centralized data filter #
    sbs = filter_sbs(
        query=query,
        project_name_sb=project_name_sb,
        po_number_sb=po_number_sb,
        supplier_name_sb=supplier_name_sb,
        user=request.user,
        is_admin=is_admin
    )

    # Step-(A5)-Apply pagination #
    sbs_page = get_paginated_queryset(request, sbs)

    # Step-(A6)-Add new SB only if user is NOT admin #
    if not is_admin and request.method == "POST" and form.is_valid():
        sb = form.save(commit=False)
        sb.created_by = request.user
        sb.team = getattr(
            getattr(request.user, "sb_profile", None),
            "role",
            "manager_construction"   # default role for team users
        )
        sb.save()
        messages.success(request, "✅ SB record created successfully.")
        return redirect(
            f"{reverse('sb_dashboard')}?q={query}&project_name_sb={project_name_sb}&po_number_sb={po_number_sb}&supplier_name_sb={supplier_name_sb}"
        )

    # Step-(A7)-Total Bill Amount-(Show below-List Table) #
    total_bill_amount_sb = sbs.aggregate(Sum("bill_amount_sb"))["bill_amount_sb__sum"] or 0

    # Step-(A8)-Prepare context for template #
    context = {
        "sbs": sbs_page,
        "query": query,
        "project_name_sb": project_name_sb,
        "po_number_sb": po_number_sb,
        "supplier_name_sb": supplier_name_sb,
        "form": form,
        "mode": "list",
        "readonly": is_admin,   # Admins are readonly
        "is_admin": is_admin,
        "total_bill_amount_sb": total_bill_amount_sb,
    }

    # Step-(A9)-Render template #
    return render(request, "sb/sb_dashboard.html", context)

# F-Edit View-(Team edit only their own SBs. Admin cannot edit) #
@login_required
def edit_sb(request, pk):
    sb = get_object_or_404(Sb, pk=pk)
    is_admin = is_django_admin(request.user)

    # Admins cannot edit, and team members can only edit their own SBs
    if is_admin or sb.created_by != request.user:
        raise PermissionDenied

    query = (request.GET.get("q") or "").strip()
    project_name_sb = (request.GET.get("project_name_sb") or "").strip()
    po_number_sb = (request.GET.get("po_number_sb") or "").strip()
    supplier_name_sb = (request.GET.get("supplier_name_sb") or "").strip()

    form = SbForm(request.POST or None, instance=sb, user=request.user)

    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "✏️ SB record updated successfully.")
        params = urlencode({
            "q": query,
            "project_name_sb": project_name_sb,
            "po_number_sb": po_number_sb,
            "supplier_name_sb": supplier_name_sb,
        })
        return redirect(f"{reverse('sb_dashboard')}?{params}")

    sbs = filter_sbs(
        query=query,
        project_name_sb=project_name_sb,
        po_number_sb=po_number_sb,
        supplier_name_sb=supplier_name_sb,
        user=request.user,
        is_admin=is_admin
    )
    sbs_page = get_paginated_queryset(request, sbs)

    context = {
        "form": form,
        "mode": "edit",
        "sb": sb,
        "query": query,
        "project_name_sb": project_name_sb,
        "po_number_sb": po_number_sb,
        "supplier_name_sb": supplier_name_sb,
        "readonly": False,
        "is_admin": is_admin,
        "sbs": sbs_page,
    }
    return render(request, "sb/sb_dashboard.html", context)

# G-Delete View-(Team delete only their own SBs. Admin cannot delete) #
@login_required
def delete_sb(request, pk):
    sb = get_object_or_404(Sb, pk=pk)
    is_admin = is_django_admin(request.user)

    # Admins cannot delete, and team members can only delete their own SBs
    if is_admin or sb.created_by != request.user:
        raise PermissionDenied

    query = (request.GET.get("q") or "").strip()
    project_name_sb = (request.GET.get("project_name_sb") or "").strip()
    po_number_sb = (request.GET.get("po_number_sb") or "").strip()
    supplier_name_sb = (request.GET.get("supplier_name_sb") or "").strip()

    if request.method == "POST":
        name = f"{sb.project_name_sb} - {sb.supplier_name_sb}"
        sb.delete()
        messages.success(request, f"🗑️ SB record '{name}' deleted successfully.")
        params = urlencode({
            "q": query,
            "project_name_sb": project_name_sb,
            "po_number_sb": po_number_sb,
            "supplier_name_sb": supplier_name_sb,
        })
        return redirect(f"{reverse('sb_dashboard')}?{params}")

    context = {
        "sb": sb,
        "query": query,
        "project_name_sb": project_name_sb,
        "po_number_sb": po_number_sb,
        "supplier_name_sb": supplier_name_sb,
        "is_admin": is_admin,
        "readonly": True,
    }
    return render(request, "sb/confirm_delete.html", context)

# H -Auto-fill-Unit-(Pull from-po-app) #
def get_sb_unit(request, pk):
    po = get_object_or_404(Po, pk=pk)   
    return JsonResponse({
        "resource_unit_po": po.resource_unit_po or "",   
    })

# 📦 Auto-fill Quantity (Pull from Po app with 4 filters)
def get_sb_quantity(request):
    project_id   = request.GET.get("project_id")
    po_id        = request.GET.get("po_id")
    resource_id  = request.GET.get("resource_id")
    supplier_id  = request.GET.get("supplier_id")

    po = Po.objects.filter(
        pk=po_id,
        project_name_po_id=project_id,
        resource_name_po_id=resource_id,
        supplier_name_po_id=supplier_id
    ).first()

    return JsonResponse({
        "quantity": float(po.quantity) if po else None
    })

# 💰 Auto-fill Price (Pull from Po app with 4 filters)
def get_sb_price(request):
    project_id   = request.GET.get("project_id")
    po_id        = request.GET.get("po_id")
    resource_id  = request.GET.get("resource_id")
    supplier_id  = request.GET.get("supplier_id")

    po = Po.objects.filter(
        pk=po_id,
        project_name_po_id=project_id,
        resource_name_po_id=resource_id,
        supplier_name_po_id=supplier_id
    ).first()

    return JsonResponse({
        "unit_price": float(po.unit_price) if po else None
    })
