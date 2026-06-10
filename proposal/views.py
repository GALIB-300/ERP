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
from django.db.models import Sum


from .forms import ProposalForm
from .models import Proposal

# B - Django Admin Check #
def is_django_admin(user):
    return user.is_superuser

# C - Filtering Function (Submit Year-Based) #
def filter_proposals(query=None, submit_year=None, user=None, is_admin=False, exclude_user=None):
    # Base queryset #
    if is_admin:
        # Admins see all proposals #
        queryset = Proposal.objects.all()
    else:
        # Team members see only their own proposals #
        queryset = Proposal.objects.filter(created_by=user)

    # Exclude specific user if provided #
    if exclude_user:
        queryset = queryset.exclude(created_by=exclude_user)

    # Free text search across submit_year #
    if query:
        queryset = queryset.filter(
            Q(submit_year__icontains=query)
        )

    # Filter by submit year (exact match) #
    if submit_year:
        queryset = queryset.filter(submit_year=submit_year)

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

# E - Dashboard View (Admin view all proposals. Team view/add their own proposals) #
@login_required
def proposal_dashboard(request):
    query = request.GET.get("q", "").strip()
    submit_year = request.GET.get("submit_year", "").strip()
    is_admin = is_django_admin(request.user)

    form = None if is_admin else ProposalForm(request.POST or None)

    proposals = filter_proposals(
        query=query,
        submit_year=submit_year,
        user=request.user,
        is_admin=is_admin
    )

    proposals_page = get_paginated_queryset(request, proposals)

    if not is_admin and request.method == "POST":
        if form.is_valid():
            proposal_no = form.cleaned_data.get("proposal_no")

            # ✅ Duplicate check without unique=True
            if Proposal.objects.filter(proposal_no=proposal_no).exists():
                # Attach error to field and show flash message
                form.add_error("proposal_no", "❌ Duplicate proposal no. Please change this.")
                messages.error(request, "❌ Duplicate proposal no. Please change this.")
            else:
                proposal = form.save(commit=False)
                proposal.created_by = request.user
                proposal.team = getattr(
                    getattr(request.user, "proposal_profile", None),
                    "role",
                    "manager_sales"
                )
                proposal.save()
                messages.success(request, "✅ Proposal detailed record created successfully.")
                return redirect(
                    f"{reverse('proposal_dashboard')}?q={query}&submit_year={submit_year}"
                )

    # 🔑 Calculate total proposal amount #
    total_proposed_amount = proposals.aggregate(
        Sum("proposal_amount")
    )["proposal_amount__sum"] or 0

    context = {
        "proposals": proposals_page,
        "query": query,
        "submit_year": submit_year,
        "form": form,
        "mode": "list",
        "readonly": is_admin,
        "is_admin": is_admin,
        "total_proposed_amount": total_proposed_amount,
    }
    return render(request, "proposal/proposal_dashboard.html", context)

# F - Edit View (Team edit only their own proposals. Admin cannot edit) #
@login_required
def edit_proposal(request, pk):
    proposal = get_object_or_404(Proposal, pk=pk)
    is_admin = is_django_admin(request.user)

    if not is_admin and proposal.created_by != request.user:
        raise PermissionDenied

    query = (request.GET.get("q") or "").strip()
    submit_year = (request.GET.get("submit_year") or "").strip()

    form = ProposalForm(request.POST or None, instance=proposal)

    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "✏️ Proposal detailed record updated successfully.")
        params = urlencode({
            "q": query,
            "submit_year": submit_year,
        })
        return redirect(f"{reverse('proposal_dashboard')}?{params}")

    proposals = filter_proposals(
        query=query,
        submit_year=submit_year,
        user=request.user,
        is_admin=is_admin
    )
    proposals_page = get_paginated_queryset(request, proposals)

    context = {
        "form": form,
        "mode": "edit",
        "proposal": proposal,
        "query": query,
        "submit_year": submit_year,
        "readonly": False,
        "is_admin": is_admin,
        "proposals": proposals_page,
    }
    return render(request, "proposal/proposal_dashboard.html", context)

# G - Delete View (Team delete only their own proposals. Admin cannot delete) #
@login_required
def delete_proposal(request, pk):
    proposal = get_object_or_404(Proposal, pk=pk)
    is_admin = is_django_admin(request.user)

    if not is_admin and proposal.created_by != request.user:
        raise PermissionDenied

    query = (request.GET.get("q") or "").strip()
    submit_year = (request.GET.get("submit_year") or "").strip()

    if request.method == "POST":
        number = proposal.proposal_no
        proposal.delete()
        messages.success(request, f"🗑️ Proposal '{number}' deleted successfully.")
        params = urlencode({
            "q": query,
            "submit_year": submit_year,
        })
        return redirect(f"{reverse('proposal_dashboard')}?{params}")

    context = {
        "proposal": proposal,
        "query": query,
        "submit_year": submit_year,
        "is_admin": is_admin,
        "readonly": True
    }
    return render(request, "proposal/confirm_delete.html", context)
