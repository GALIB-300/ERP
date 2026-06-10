# A - Import Required Modules #
from django.shortcuts import render, get_object_or_404, redirect
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.http import JsonResponse
from django.contrib import messages
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from urllib.parse import urlencode
from django.db.models import Q

from .forms import PfpForm
from .models import Pfp

# B - Django Admin Check #
def is_django_admin(user):
    return user.is_superuser

# C - Filtering Function (Proposal/Submit-To Based) #
def filter_pfps(query=None, submit_to_pfp=None, proposal=None, user=None, is_admin=False, exclude_user=None):
    # Base queryset #
    if is_admin:
        queryset = Pfp.objects.all()
    else:
        queryset = Pfp.objects.filter(created_by=user)

    # Exclude specific user if provided #
    if exclude_user:
        queryset = queryset.exclude(created_by=exclude_user)

    # Free text search across submit_to_pfp #
    if query:
        queryset = queryset.filter(Q(submit_to_pfp__icontains=query))

    # Filter by submit_to_pfp #
    if submit_to_pfp:
        queryset = queryset.filter(submit_to_pfp__icontains=submit_to_pfp)

    # Filter by proposal (OneToOne relation) #
    if proposal:
        queryset = queryset.filter(proposal_id=proposal)

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

# E - Dashboard View (Admin view all PFPs. Team view/add their own PFPs) #
@login_required
def pfp_dashboard(request):
    query = request.GET.get("q", "").strip()
    proposal = request.GET.get("proposal", "").strip()
    submit_to_pfp = request.GET.get("submit_to_pfp", "").strip()
    is_admin = is_django_admin(request.user)

    form = PfpForm(request.POST or None)

    pfps = filter_pfps(
        query=query,
        submit_to_pfp=submit_to_pfp,
        proposal=proposal,
        user=request.user,
        is_admin=is_admin
    )
    pfps_page = get_paginated_queryset(request, pfps)

    if not is_admin and request.method == "POST" and form.is_valid():
        pfp = form.save(commit=False)
        pfp.created_by = request.user
        pfp.team = getattr(
            getattr(request.user, "pfp_profile", None),
            "role",
            "manager_sales"
        )
        pfp.save()
        messages.success(request, "✅ PFP detailed record created successfully.")
        return redirect(
            f"{reverse('pfp_dashboard')}?q={query}&proposal={proposal}&submit_to_pfp={submit_to_pfp}"
        )

    context = {
        "pfps": pfps_page,
        "query": query,
        "proposal": proposal,
        "submit_to_pfp": submit_to_pfp,
        "form": form,
        "mode": "list",
        "readonly": is_admin,
        "is_admin": is_admin,
    }
    return render(request, "pfp/pfp_dashboard.html", context)

# F - Edit View (Team edit only their own PFPs. Admin cannot edit) #
@login_required
def edit_pfp(request, pk):
    pfp = get_object_or_404(Pfp, pk=pk)
    is_admin = is_django_admin(request.user)

    if not is_admin and pfp.created_by != request.user:
        raise PermissionDenied

    query = (request.GET.get("q") or "").strip()
    proposal = (request.GET.get("proposal") or "").strip()

    form = PfpForm(request.POST or None, instance=pfp)

    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "✏️ PFP detailed record updated successfully.")
        params = urlencode({
            "q": query,
            "proposal": proposal,
        })
        return redirect(f"{reverse('pfp_dashboard')}?{params}")

    pfps = filter_pfps(
        query=query,
        proposal=proposal,
        user=request.user,
        is_admin=is_admin
    )
    pfps_page = get_paginated_queryset(request, pfps)

    context = {
        "form": form,
        "mode": "edit",
        "pfp": pfp,
        "query": query,
        "proposal": proposal,
        "readonly": False,
        "is_admin": is_admin,
        "pfps": pfps_page,
    }
    return render(request, "pfp/pfp_dashboard.html", context)

# G - Delete View (Team delete only their own PFPs. Admin cannot delete) #
@login_required
def delete_pfp(request, pk):
    pfp = get_object_or_404(Pfp, pk=pk)
    is_admin = is_django_admin(request.user)

    if not is_admin and pfp.created_by != request.user:
        raise PermissionDenied

    query = (request.GET.get("q") or "").strip()
    proposal = (request.GET.get("proposal") or "").strip()

    if request.method == "POST":
        name = pfp.title_pfp
        pfp.delete()
        messages.success(request, f"🗑️ PFP '{name}' deleted successfully.")
        params = urlencode({
            "q": query,
            "proposal": proposal,
        })
        return redirect(f"{reverse('pfp_dashboard')}?{params}")

    context = {
        "pfp": pfp,
        "query": query,
        "proposal": proposal,
        "is_admin": is_admin,
        "readonly": True
    }
    return render(request, "pfp/confirm_delete.html", context)
