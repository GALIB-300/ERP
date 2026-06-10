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

from .forms import ClientForm
from .models import Client

# B-Django Admin Check #
def is_django_admin(user):
    role = getattr(getattr(user, "resource_profile", None), "role", None)
    # Treat superuser and manager_construction as admin-like (read-only) #
    return user.is_superuser or role == "manager_construction"

# C-Filtering Function-(Client Name-Based) #
def filter_clients(query=None, name_of_client=None, user=None, is_admin=False, exclude_user=None):
    # Base queryset #
    if is_admin:
        # Admins see all clients #
        queryset = Client.objects.all()
    else:
        # Team members see only their own clients #
        queryset = Client.objects.filter(created_by=user)

    # Exclude specific user if provided-(removes clients created by a specific user from the results) #
    if exclude_user:
        queryset = queryset.exclude(created_by=exclude_user)

    # Free text search across multiple fields #
    if query:
        queryset = queryset.filter(
            Q(name_of_client__icontains=query)
        )

    # Filter by client name #
    if name_of_client:
        queryset = queryset.filter(name_of_client__icontains=name_of_client)

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

# E-Dashboard View-(Admin view all clients. Team-(manager_sales)-view/add their own clients. (manager_construction)-only view clients data) #
@login_required
def client_dashboard(request):
    query = request.GET.get("q", "").strip()
    name_of_client = request.GET.get("name_of_client", "").strip()
    is_admin = is_django_admin(request.user)
    role = getattr(getattr(request.user, "resource_profile", None), "role", None)

    form = None if is_admin else ClientForm(request.POST or None)

    clients = filter_clients(
        query=query,
        name_of_client=name_of_client,
        user=request.user,
        is_admin=is_admin
    )

    clients_page = get_paginated_queryset(request, clients)

    if role == "manager_sales" and request.method == "POST" and form.is_valid():
        resource = form.save(commit=False)
        resource.created_by = request.user
        resource.team = role or "manager_sales"
        resource.save()
        messages.success(request, "✅ Resource detailed record created successfully.")
        return redirect(
            f"{reverse('client_dashboard')}?q={query}&name_of_client={name_of_client}"
        )

    context = {
        "clients": clients_page,
        "query": query,
        "name_of_client": name_of_client,
        "form": form,
        "mode": "list",
        "readonly": is_admin,
        "is_admin": is_admin,
    }
    return render(request, "client/client_dashboard.html", context)

# F-Edit View-(Team edit only their own clients. Admin cannot edit) #
@login_required
def edit_client(request, pk):
    client = get_object_or_404(Client, pk=pk)
    is_admin = is_django_admin(request.user)

    if not is_admin and client.created_by != request.user:
        raise PermissionDenied

    query = (request.GET.get("q") or "").strip()
    name_of_client = (request.GET.get("name_of_client") or "").strip()

    form = ClientForm(request.POST or None, instance=client)

    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "✏️ Client detailed record updated successfully.")
        params = urlencode({
            "q": query,
            "name_of_client": name_of_client,
        })
        return redirect(f"{reverse('client_dashboard')}?{params}")

    clients = filter_clients(
        query=query,
        name_of_client=name_of_client,
        user=request.user,
        is_admin=is_admin
    )
    clients_page = get_paginated_queryset(request, clients)

    context = {
        "form": form,
        "mode": "edit",
        "client": client,
        "query": query,
        "name_of_client": name_of_client,
        "readonly": False,
        "is_admin": is_admin,
        "clients": clients_page,
    }
    return render(request, "client/client_dashboard.html", context)

# G-Delete View-(Team delete only their own clients. Admin cannot delete) #
@login_required
def delete_client(request, pk):
    client = get_object_or_404(Client, pk=pk)
    is_admin = is_django_admin(request.user)

    if not is_admin and client.created_by != request.user:
        raise PermissionDenied

    query = (request.GET.get("q") or "").strip()
    name_of_client = (request.GET.get("name_of_client") or "").strip()

    if request.method == "POST":
        name = client.name_of_client
        client.delete()
        messages.success(request, f"🗑️ Client '{name}' deleted successfully.")
        params = urlencode({
            "q": query,
            "name_of_client": name_of_client,
        })
        return redirect(f"{reverse('client_dashboard')}?{params}")

    context = {
        "client": client,
        "query": query,
        "name_of_client": name_of_client,
        "is_admin": is_admin,
        "readonly": True
    }
    return render(request, "client/confirm_delete.html", context)
