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
from django.shortcuts import render

from .forms import SupplierForm
from .models import Supplier

# B-Django Admin Check #
def is_django_admin(user):
    role = getattr(getattr(user, "supplier_profile", None), "role", None)
    # Superusers OR GM Construction are treated as admin-like
    return user.is_superuser or role == "gm_construction"

# C-Filtering Function-(Supplier Name-Based) #
def filter_suppliers(query=None, name_of_supplier=None, user=None, is_admin=False, exclude_user=None):
    if is_admin:
        # Admins & GM Construction see all suppliers
        queryset = Supplier.objects.all()
    else:
        # Manager Construction sees only their own
        queryset = Supplier.objects.filter(created_by=user)

    if exclude_user:
        queryset = queryset.exclude(created_by=exclude_user)

    if query:
        queryset = queryset.filter(Q(name_of_supplier__icontains=query))

    if name_of_supplier:
        queryset = queryset.filter(name_of_supplier__icontains=name_of_supplier)

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

# E-Dashboard View-(Admin view all suppliers. Team view/add their own suppliers) #
# Step-(A)-Dashboard view #
@login_required
def supplier_dashboard(request):
    query = request.GET.get("q", "").strip()
    name_of_supplier = request.GET.get("name_of_supplier", "").strip()

    # Step-(A3)-Check if user is admin (superuser or GM Construction)
    is_admin = is_django_admin(request.user)
    role = getattr(getattr(request.user, "supplier_profile", None), "role", None)

    # Step-(A4)-Initialize form only for Manager Construction
    readonly = is_admin
    form = None if readonly else SupplierForm(request.POST or None)

    # Step-(A5)-Centralized data filter
    suppliers = filter_suppliers(
        query=query,
        name_of_supplier=name_of_supplier,
        user=request.user,
        is_admin=is_admin
    )

    # Apply pagination
    suppliers_page = get_paginated_queryset(request, suppliers)

    # Step-(A6)-Add new supplier only if Manager Construction
    if not is_admin and request.method == "POST" and form.is_valid():
        supplier = form.save(commit=False)
        supplier.created_by = request.user
        supplier.team = getattr(
            getattr(request.user, "supplier_profile", None),
            "role",
            "manager_construction"   # default role for suppliers
        )
        supplier.save()
        messages.success(request, "✅ Supplier detailed record created successfully.")
        return redirect(
            f"{reverse('supplier_dashboard')}?q={query}&name_of_supplier={name_of_supplier}"
        )

    # Step-(A7)-Prepare context for template
    context = {
        "suppliers": suppliers_page,
        "query": query,
        "name_of_supplier": name_of_supplier,
        "form": form,
        "mode": "list",
        "readonly": readonly,   # Admin & GM are readonly
        "is_admin": is_admin,
        "role": role,
    }

    # Step-(A8)-Render template
    return render(request, "supplier/supplier_dashboard.html", context)
    
# F-Edit View-(Team edit only their own suppliers. Admin cannot edit) #
# Step-(A)-Edit view #
@login_required
def edit_supplier(request, pk):
    # Step-(A1)-Get supplier by ID #
    supplier = get_object_or_404(Supplier, pk=pk)

    # Step-(A2)-Check if user is admin (custom helper) #
    is_admin = is_django_admin(request.user)

    # Step-(A3)-Permission check based on Admin & Team #
    if is_admin or supplier.created_by != request.user:
        raise PermissionDenied

    # Step-(A4)-Search Query parameter-(q)-from the URL #
    query = (request.GET.get("q") or "").strip()

    # Step-(A5)-Name of Supplier-based-query parameter-from the URL #
    name_of_supplier = (request.GET.get("name_of_supplier") or "").strip()

    # Step-(A6)-Initialize form with supplier instance #
    form = SupplierForm(request.POST or None, instance=supplier)

    # Step-(A7)-Edit suppliers based on team users #
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "✏️ Supplier detailed record updated successfully.")
        params = urlencode({
            "q": query,
            "name_of_supplier": name_of_supplier,
        })
        return redirect(f"{reverse('supplier_dashboard')}?{params}")

    # Step-(A8)-Centralized data filter #
    suppliers = filter_suppliers(
        query=query,
        name_of_supplier=name_of_supplier,
        user=request.user,
        is_admin=is_admin
    )

    # Apply pagination #
    suppliers_page = get_paginated_queryset(request, suppliers)

    # Step-(A9)-Prepare context for edit template #
    context = {
        "form": form,
        "mode": "edit",
        "supplier": supplier,
        "query": query,
        "name_of_supplier": name_of_supplier,
        "readonly": False,
        "is_admin": is_admin,
        "suppliers": suppliers_page,  
    }

    # Step-(A10)-Render template #
    return render(request, "supplier/supplier_dashboard.html", context)

# G-Delete View-(Team delete only their own suppliers. Admin cannot delete) #
# Step-(A)-Delete view #
@login_required
def delete_supplier(request, pk):
    # Step-(A1)-Get supplier by ID #
    supplier = get_object_or_404(Supplier, pk=pk)

    # Step-(A2)-Check if user is admin (custom helper) #
    is_admin = is_django_admin(request.user)

    # Step-(A3)-Permission check based on Admin & Team #
    if is_admin or supplier.created_by != request.user:
        raise PermissionDenied

    # Step-(A4)-Search Query parameter-(q)-from the URL #
    query = (request.GET.get("q") or "").strip()

    # Step-(A5)-Name of Supplier-based-query parameter-from the URL #
    name_of_supplier = (request.GET.get("name_of_supplier") or "").strip()
    
    # Step-(A6)-Delete suppliers-(only team users can delete) #
    if request.method == "POST":
        name = supplier.name_of_supplier
        supplier.delete()
        messages.success(request, f"🗑️ Supplier '{name}' deleted successfully.")
        params = urlencode({
            "q": query,
            "name_of_supplier": name_of_supplier,
        })
        return redirect(f"{reverse('supplier_dashboard')}?{params}")

    # Step-(A7)-Prepare context for delete confirmation template #
    context = {
        "supplier": supplier,
        "query": query,
        "name_of_supplier": name_of_supplier,
        "is_admin": is_admin,
        "readonly": True    # Admins are readonly, team confirm delete
    }

    # Step-(A8)-Render delete confirmation template #
    return render(request, "supplier/supplier_dashboard.html", context)

# H - Supplier List View #
@login_required
def supplier_process(request):
    # Step-(A1)-Search Query parameter-(q)-from the URL #
    query = request.GET.get("q", "").strip()

    # Step-(A2)-Name of Supplier-based-query parameter-from the URL #
    name_of_supplier = request.GET.get("name_of_supplier", "").strip()

    # Step-(A3)-Check if user is admin (superuser or GM Construction)
    is_admin = is_django_admin(request.user)

    # Step-(A4)-Centralized data filter (search + supplier name filter)
    suppliers = filter_suppliers(
        query=query,
        name_of_supplier=name_of_supplier,
        user=request.user,
        is_admin=is_admin
    ).order_by("name_of_supplier")

    # Step-(A5)-Apply pagination
    suppliers_page = get_paginated_queryset(request, suppliers)

    # Step-(A6)-Prepare context for template
    context = {
        "suppliers": suppliers_page,
        "query": query,
        "name_of_supplier": name_of_supplier,
        "is_admin": is_admin,
        "mode": "list",        # Only list table view
        "readonly": True,      # Always readonly in list view
    }

    # Step-(A7)-Render template
    return render(request, "supplier/supplier_process.html", context)
