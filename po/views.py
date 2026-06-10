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
from django.db.models import Sum
from datetime import datetime

from .forms import PoForm
from .models import Po
from resource.models import Resource
from company.models import Company
from stc.models import Stc 

# B-Django Admin Check #
def is_django_admin(user):
    return user.is_superuser

# C-Filtering Function-(Project Name and PO No and Supplier Name-Based) #
def filter_pos(query=None, project_name_po=None, po_no=None, supplier_name_po=None, user=None, is_admin=False, exclude_user=None):
    
    # Base queryset #
    if is_admin:
        queryset = Po.objects.all()
    else:
        queryset = Po.objects.filter(created_by=user)

    # Exclude specific user if provided #
    if exclude_user:
        queryset = queryset.exclude(created_by=exclude_user)

    # Free text search across project name & PO no #
    if query:
        queryset = queryset.filter(
            Q(project_name_po__name_of_project__icontains=query) |
            Q(po_no__icontains=query) |
            Q(supplier_name_po__name_of_supplier__icontains=query)
        )

    # Filter by Project name #
    if project_name_po:
        queryset = queryset.filter(
            project_name_po__name_of_project__icontains=project_name_po
        )

    # Filter by PO No #
    if po_no:
        queryset = queryset.filter(
            po_no__icontains=po_no
        )

    # Filter by Supplier name #
    if supplier_name_po:
        queryset = queryset.filter(
            supplier_name_po__name_of_supplier__icontains=supplier_name_po
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

# E-Dashboard View-(Admin view all POs. Team view/add their own POs) #
@login_required
def po_dashboard(request):
    # Step-(A1)-Collect query parameters from URL #
    query = request.GET.get("q", "").strip()
    project_name_po = request.GET.get("project_name_po", "").strip()
    po_no = request.GET.get("po_no", "").strip()
    supplier_name_po = request.GET.get("supplier_name_po", "").strip()

    # Step-(A2)-Check if user is admin #
    is_admin = is_django_admin(request.user)

    # Step-(A3)-Initialize form only for non-admin users #
    form = None if is_admin else PoForm(request.POST or None, user=request.user)

    # Step-(A4)-Centralized data filter #
    pos = filter_pos(
        query=query,
        project_name_po=project_name_po,
        po_no=po_no,
        supplier_name_po=supplier_name_po,
        user=request.user,
        is_admin=is_admin
    )

    # Step-(A5)-Apply pagination #
    pos_page = get_paginated_queryset(request, pos)

    # Step-(A6)-Add new PO only if user is NOT admin #
    if not is_admin and request.method == "POST" and form.is_valid():
        po = form.save(commit=False)
        po.created_by = request.user
        po.team = getattr(
            getattr(request.user, "po_profile", None),
            "role",
            "manager_construction"   # default role for team users
        )
        po.save()
        messages.success(request, "✅ PO record created successfully.")
        return redirect(
            f"{reverse('po_dashboard')}?q={query}&project_name_po={project_name_po}&po_no={po_no}&supplier_name_po={supplier_name_po}"
        )

    # Step-(A7)-Total Bill Amount-(Show bellow-List Table) #
    total_bill_amount = pos.aggregate(Sum("bill_amount"))["bill_amount__sum"] or 0

    # Step-(A8)-Prepare context for template #
    context = {
        "pos": pos_page,
        "query": query,
        "project_name_po": project_name_po,
        "po_no": po_no,
        "supplier_name_po": supplier_name_po,
        "form": form,
        "mode": "list",
        "readonly": is_admin,   # Admins are readonly
        "is_admin": is_admin,
        "total_bill_amount": total_bill_amount,
    }

    # Step-(A9)-Render template #
    return render(request, "po/po_dashboard.html", context)

# F-Edit View-(Team edit only their own POs. Admin cannot edit) #
@login_required
def edit_po(request, pk):
    po = get_object_or_404(Po, pk=pk)
    is_admin = is_django_admin(request.user)

    # Admins cannot edit, and team members can only edit their own POs
    if is_admin or po.created_by != request.user:
        raise PermissionDenied

    query = (request.GET.get("q") or "").strip()
    project_name_po = (request.GET.get("project_name_po") or "").strip()
    po_no = (request.GET.get("po_no") or "").strip()
    supplier_name_po = (request.GET.get("supplier_name_po") or "").strip()

    form = PoForm(request.POST or None, instance=po, user=request.user)

    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "✏️ PO record updated successfully.")
        params = urlencode({
            "q": query,
            "project_name_po": project_name_po,
            "po_no": po_no,
            "supplier_name_po": supplier_name_po,
        })
        return redirect(f"{reverse('po_dashboard')}?{params}")

    pos = filter_pos(
        query=query,
        project_name_po=project_name_po,
        po_no=po_no,
        supplier_name_po=supplier_name_po,
        user=request.user,
        is_admin=is_admin
    )
    pos_page = get_paginated_queryset(request, pos)

    context = {
        "form": form,
        "mode": "edit",
        "po": po,
        "query": query,
        "project_name_po": project_name_po,
        "po_no": po_no,
        "supplier_name_po": supplier_name_po,
        "readonly": False,
        "is_admin": is_admin,
        "pos": pos_page,
    }
    return render(request, "po/po_dashboard.html", context)

# G-Delete View-(Team delete only their own POs. Admin cannot delete) #
@login_required
def delete_po(request, pk):
    po = get_object_or_404(Po, pk=pk)
    is_admin = is_django_admin(request.user)

    # Admins cannot delete, and team members can only delete their own POs
    if is_admin or po.created_by != request.user:
        raise PermissionDenied

    query = (request.GET.get("q") or "").strip()
    project_name_po = (request.GET.get("project_name_po") or "").strip()
    po_no = (request.GET.get("po_no") or "").strip()
    supplier_name_po = (request.GET.get("supplier_name_po") or "").strip()

    if request.method == "POST":
        name = f"{po.project_name_po} - {po.resource_name_po}"
        po.delete()
        messages.success(request, f"🗑️ PO record '{name}' deleted successfully.")
        params = urlencode({
            "q": query,
            "project_name_po": project_name_po,
            "po_no": po_no,
            "supplier_name_po": supplier_name_po,
        })
        return redirect(f"{reverse('po_dashboard')}?{params}")

    context = {
        "po": po,
        "query": query,
        "project_name_po": project_name_po,
        "po_no": po_no,
        "supplier_name_po": supplier_name_po,
        "is_admin": is_admin,
        "readonly": True,
    }
    return render(request, "po/confirm_delete.html", context)

# H - Auto-Fill API (Used by JavaScript) #
def get_po_details(request, pk):
    resource = get_object_or_404(Resource, pk=pk)
    return JsonResponse({
        "unit": resource.unit or "",   # <-- match your model field name
    })

# I - Print Dashboard View #
@login_required
def print_po_dashboard(request):
    # Query parameters
    po_no            = request.GET.get("po_no")
    project_name_po  = request.GET.get("project_name_po")
    supplier_name_po = request.GET.get("supplier_name_po")

    # Base queryset
    po_list = Po.objects.all().order_by("po_no")

    # Apply filters
    if po_no:
        po_list = po_list.filter(po_no__icontains=po_no)

    if supplier_name_po:
        po_list = po_list.filter(
            supplier_name_po__name_of_supplier__icontains=supplier_name_po
        )

    if project_name_po:
        po_list = po_list.filter(
            project_name_po__name_of_project__icontains=project_name_po
        )

    # Pick one PO as header (first match)
    po_header = po_list.first()

    # Get company for current user
    company = Company.objects.filter(created_by=request.user).first()

    # Get stc for current user
    stc = Stc.objects.filter(created_by=request.user).first()

    # ✅ Validation check
    if not company or not stc:
        from django.contrib import messages
        if not company:
            messages.error(request, "⚠️ Please enter Company information before printing.")
        if not stc:
            messages.error(request, "⚠️ Please enter Supplier Terms & Conditions before printing.")
        # Redirect back to PO dashboard instead of showing print page
        return redirect("po_dashboard")

    # If valid → render print page
    context = {
        "po"      : po_header,
        "company" : company,
        "stc"     : stc,
        "po_list" : po_list,
        "filters" : {
            "project_name_po"  : project_name_po,
            "supplier_name_po" : supplier_name_po,
            "po_no"            : po_no,
        }
    }
    return render(request, "po/print_po_dashboard.html", context)
