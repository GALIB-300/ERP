# A - Import Required Modules #
from django.shortcuts import render, get_object_or_404, redirect
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.http import JsonResponse
from django.contrib import messages
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from urllib.parse import urlencode
from django.db.models import Q, Sum

from .forms import PtForm
from .models import Pt

# B - Django Admin Check #
def is_django_admin(user):
    return user.is_superuser

# C - Filtering Function (Client Name + Submit Year) #
def filter_pts(query=None, client_name_pt=None, submit_year_pt=None,
               user=None, is_admin=False, exclude_user=None):
    if is_admin:
        queryset = Pt.objects.all()
    else:
        queryset = Pt.objects.filter(created_by=user)

    if exclude_user:
        queryset = queryset.exclude(created_by=exclude_user)

    if query:
        queryset = queryset.filter(
            Q(client_name_pt__name_of_client__icontains=query) |
            Q(submit_year_pt__icontains=query)
        )

    if client_name_pt:
        queryset = queryset.filter(client_name_pt__name_of_client__icontains=client_name_pt)

    if submit_year_pt:
        queryset = queryset.filter(submit_year_pt=submit_year_pt)

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

# E - Dashboard View #
@login_required
def pt_dashboard(request):
    query = request.GET.get("q", "").strip()
    client_name_pt = request.GET.get("client_name_pt", "").strip()
    submit_year_pt = request.GET.get("submit_year_pt", "").strip()
    is_admin = is_django_admin(request.user)

    form = None if is_admin else PtForm(request.POST or None, user=request.user)

    pts = filter_pts(query=query, client_name_pt=client_name_pt,
                     submit_year_pt=submit_year_pt, user=request.user,
                     is_admin=is_admin)

    pts_page = get_paginated_queryset(request, pts)

    if not is_admin and request.method == "POST" and form.is_valid():
        pt = form.save(commit=False)
        pt.created_by = request.user
        pt.team = getattr(getattr(request.user, "pt_profile", None),
                          "role", "manager_sales")
        pt.save()
        messages.success(request, "✅ Proposal detailed record created successfully.")
        return redirect(
            f"{reverse('pt_dashboard')}?q={query}&client_name_pt={client_name_pt}&submit_year_pt={submit_year_pt}"
        )

    total_proposal_pt = pts.aggregate(Sum("total_proposal_pt"))["total_proposal_pt__sum"] or 0
    total_award_pt = pts.aggregate(Sum("proposal_award_pt"))["proposal_award_pt__sum"] or 0

    client_summary = []
    for pt in pts:
        client_name = pt.client_name_pt.name_of_client if pt.client_name_pt else "Unknown Client"
        client_summary.append({
            "client_name": client_name,
            "proposal_pt": pt.total_proposal_pt or 0,
            "award_pt": pt.proposal_award_pt or 0,
        })
    client_summary.append({
        "client_name": "Total",
        "proposal_pt": total_proposal_pt,
        "award_pt": total_award_pt,
    })

    context = {
        "pts": pts_page,
        "query": query,
        "client_name_pt": client_name_pt,
        "submit_year_pt": submit_year_pt,
        "form": form,
        "mode": "list",
        "readonly": is_admin,
        "is_admin": is_admin,
        "total_proposal_pt": total_proposal_pt,
        "total_award_pt": total_award_pt,
        "client_summary": client_summary,
    }
    return render(request, "pt/pt_dashboard.html", context)

# F - Edit View #
@login_required
def edit_pt(request, pk):
    pt = get_object_or_404(Pt, pk=pk)
    is_admin = is_django_admin(request.user)

    if not is_admin and pt.created_by != request.user:
        raise PermissionDenied

    query = (request.GET.get("q") or "").strip()
    client_name_pt = (request.GET.get("client_name_pt") or "").strip()
    submit_year_pt = (request.GET.get("submit_year_pt") or "").strip()

    form = PtForm(request.POST or None, instance=pt, user=request.user)

    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "✏️ Proposal detailed record updated successfully.")
        params = urlencode({
            "q": query,
            "client_name_pt": client_name_pt,
            "submit_year_pt": submit_year_pt,
        })
        return redirect(f"{reverse('pt_dashboard')}?{params}")

    pts = filter_pts(query=query, client_name_pt=client_name_pt,
                     submit_year_pt=submit_year_pt, user=request.user,
                     is_admin=is_admin)
    pts_page = get_paginated_queryset(request, pts)

    context = {
        "form": form,
        "mode": "edit",
        "pt": pt,
        "query": query,
        "client_name_pt": client_name_pt,
        "submit_year_pt": submit_year_pt,
        "readonly": False,
        "is_admin": is_admin,
        "pts": pts_page,
    }
    return render(request, "pt/pt_dashboard.html", context)

# G - Delete View #
@login_required
def delete_pt(request, pk):
    pt = get_object_or_404(Pt, pk=pk)
    is_admin = is_django_admin(request.user)

    if not is_admin and pt.created_by != request.user:
        raise PermissionDenied

    query = (request.GET.get("q") or "").strip()
    client_name_pt = (request.GET.get("client_name_pt") or "").strip()
    submit_year_pt = (request.GET.get("submit_year_pt") or "").strip()

    if request.method == "POST":
        name = pt.client_name_pt.name_of_client if pt.client_name_pt else "Unknown Client"
        pt.delete()
        messages.success(request, f"🗑️ Proposal for client '{name}' deleted successfully.")
        params = urlencode({
            "q": query,
            "client_name_pt": client_name_pt,
            "submit_year_pt": submit_year_pt,
        })
        return redirect(f"{reverse('pt_dashboard')}?{params}")

    context = {
        "pt": pt,
        "query": query,
        "client_name_pt": client_name_pt,
        "submit_year_pt": submit_year_pt,
        "is_admin": is_admin,
        "readonly": True,
    }
    return render(request, "pt/confirm_delete.html", context)