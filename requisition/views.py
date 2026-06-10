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

from .models import Requisition
from .forms import RequisitionForm
from project.models import Project
from resource.models import Resource

# B-Django Admin Check #
def is_django_admin(user):
    return user.is_superuser

# C-Filtering Function-(Project Name and Requisition No-Based) #
def filter_requisitions(query=None, project_name=None, requisition_no=None,
                        user=None, is_admin=False, exclude_user=None):
    # Base queryset #
    if is_admin:
        queryset = Requisition.objects.all()
    else:
        queryset = Requisition.objects.filter(created_by=user)

    # Exclude specific user if provided #
    if exclude_user:
        queryset = queryset.exclude(created_by=exclude_user)

    # Free text search across project name & requisition no #
    if query:
        queryset = queryset.filter(
            Q(project__name_of_project__icontains=query) |
            Q(requisition_no__icontains=query)
        )

    # Filter by Project name #
    if project_name:
        queryset = queryset.filter(
            project__name_of_project__icontains=project_name
        )

    # Filter by Requisition No #
    if requisition_no:
        queryset = queryset.filter(
            requisition_no__icontains=requisition_no
        )

    return queryset

# D - Pagination Helper #
def get_paginated_queryset(request, queryset, per_page=10):
    paginator = Paginator(queryset, per_page)
    page_number = request.GET.get("page")

    try:
        return paginator.page(page_number)
    except PageNotAnInteger:
        return paginator.page(1)
    except EmptyPage:
        return paginator.page(paginator.num_pages)

# E - Team Dashboard-(Team will view/add their own Requisitions. Admin will view only submitted requisitions) #
@login_required
def requisition_dashboard(request):
    # Step-(A1)-Search Query parameter-(q)-from the URL #
    query = request.GET.get("q", "").strip()

    # Step-(A2)-Project Name-based query parameter-from the URL #
    project_name = request.GET.get("project", "").strip()

    # Step-(A3)-Requisition No-based query parameter-from the URL #
    requisition_no = request.GET.get("requisition_no", "").strip()

    # Step-(A4)-Check if user is admin (custom helper) #
    is_admin = is_django_admin(request.user)

    # Step-(A5)-Initialize form only for non-admin users #
    form = None if is_admin else RequisitionForm(request.POST or None, user=request.user)

    # Step-(A6)-Centralized data filter #
    if is_admin:
        # Admins only see requisitions submitted for approval
        requisitions_qs = filter_requisitions(
            query=query,
            project_name=project_name,
            requisition_no=requisition_no,
            user=request.user,
            is_admin=is_admin,
            exclude_user=request.user,
        ).filter(submitted_for_approval=True)
    else:
        # Team members see their own requisitions
        requisitions_qs = filter_requisitions(
            query=query,
            project_name=project_name,
            requisition_no=requisition_no,
            user=request.user,
            is_admin=is_admin,
        )

    # Step-(A6a)-Apply pagination #
    requisitions_page = get_paginated_queryset(request, requisitions_qs)

    # Step-(A7)-Add new requisition data by the team user #
    if not is_admin and request.method == "POST" and form.is_valid():
        requisition = form.save(commit=False)
        requisition.created_by = request.user
        requisition.team = getattr(
            getattr(request.user, "requisition_profile", None),
            "role",
            "manager_construction"   # default role for customers/team members
        )
        requisition.save()
        messages.success(request, "✅ Requisition record created successfully.")

        # Step-(A7a)-Redirect to dashboard so list refreshes immediately #
        return redirect("requisition_dashboard")

    # Step-(A8)-Prepare context for template #
    context = {
        "requisitions": requisitions_page,
        "query": query,
        "project": project_name,
        "requisition_no": requisition_no,
        "form": form,
        "mode": "list",
        "readonly": is_admin,  # Admins are readonly
        "is_admin": is_admin,
    }

    # Step-(A9)-Render template #
    return render(request, "requisition/requisition_dashboard.html", context)

# F - Edit View (Team will edit their own data. Admin will not edit data) #
# Step-(A)-Edit view #
@login_required
def edit_requisition(request, pk):
    # Step-(A1)-Get requisition by ID #
    requisition = get_object_or_404(Requisition, pk=pk)

    # Step-(A2)-Check if user is admin (custom helper) #
    is_admin = is_django_admin(request.user)

    # Step-(A3)-Permission check based on Admin & Team #
    if is_admin or requisition.created_by != request.user:
        raise PermissionDenied

    # Step-(A4)-Search Query parameter-(q)-from the URL #
    query = (request.GET.get("q") or "").strip()

    # Step-(A5)-Project Name-based query parameter-from the URL #
    project_name = (request.GET.get("project") or "").strip()

    # Step-(A6)-Requisition No-based query parameter-from the URL #
    requisition_no = (request.GET.get("requisition_no") or "").strip()

    # Step-(A7)-Initialize form with requisition instance #
    form = RequisitionForm(request.POST or None, instance=requisition, user=request.user)

    # Step-(A8)-Edit requisition based on team users #
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "✏️ Requisition record updated successfully.")
        params = urlencode({
            "q": query,
            "project": project_name,
            "requisition_no": requisition_no,
        })
        return redirect(f"{reverse('requisition_dashboard')}?{params}")

    # Step-(A9)-Centralized data filter #
    requisitions_qs = filter_requisitions(
        query=query,
        project_name=project_name,
        requisition_no=requisition_no,
        user=request.user,
        is_admin=is_admin
    )

    # Step-(A9a)-Apply pagination #
    requisitions_page = get_paginated_queryset(request, requisitions_qs)

    # Step-(A10)-Prepare context for edit template #
    context = {
        "form": form,
        "mode": "edit",
        "requisition": requisition,
        "query": query,
        "project": project_name,
        "requisition_no": requisition_no,
        "readonly": False,
        "is_admin": is_admin,
        "requisitions": requisitions_page,
    }

    # Step-(A11)-Render template #
    return render(request, "requisition/requisition_dashboard.html", context)

# G - Delete View (Team will delete their own requisitions. Admin cannot delete) #
# Step-(A)-Delete view #
@login_required
def delete_requisition(request, pk):
    # Step-(A1)-Get Requisition by ID #
    requisition = get_object_or_404(Requisition, pk=pk)

    # Step-(A2)-Check if user is admin (custom helper) #
    is_admin = is_django_admin(request.user)

    # Step-(A3)-Permission check based on Admin & Team #
    if is_admin or requisition.created_by != request.user:
        raise PermissionDenied

    # Step-(A4)-Search Query parameter-(q)-from the URL #
    query = (request.GET.get("q") or "").strip()

    # Step-(A5)-Project Name-based query parameter-from the URL #
    project_name_requisition = (request.GET.get("project") or "").strip()

    # Step-(A6)-Requisition No-based query parameter-from the URL #
    requisition_no = (request.GET.get("requisition_no") or "").strip()

    # Step-(A7)-Delete Requisition (only team users can delete) #
    if request.method == "POST":
        name = requisition.project_name_requisition.name_of_project if requisition.project_name_requisition else "Unknown Project"
        requisition.delete()
        messages.success(request, f"🗑️ Requisition record for project '{name}' deleted successfully.")
        params = urlencode({
            "q": query,
            "project": project_name_requisition,
            "requisition_no": requisition_no,
        })
        return redirect(f"{reverse('requisition_dashboard')}?{params}")

    # Step-(A8)-Prepare context for delete confirmation template #
    context = {
        "requisition": requisition,
        "query": query,
        "project": project_name_requisition,
        "requisition_no": requisition_no,
        "is_admin": is_admin,
        "readonly": True    # Admins are readonly, team confirm delete
    }

    # Step-(A9)-Render delete confirmation template #
    return render(request, "requisition/confirm_delete.html", context)

# H - Submit Requisition for Approval (Team only can submit requisition) #
@login_required
def submit_requisition_for_approval(request, pk):
    # Step-(H1)-Get requisition by ID #
    requisition = get_object_or_404(Requisition, pk=pk)

    # Step-(H2)-Check if user is admin (custom helper) #
    is_admin = is_django_admin(request.user)

    # Step-(H3)-Permission check: only creator (not admin) can submit #
    if is_admin or requisition.created_by != request.user:
        raise PermissionDenied

    # Step-(H4)-Mark requisition as submitted for approval #
    requisition.submitted_for_approval = True
    requisition.save()

    # Step-(H5)-Success message #
    messages.success(request, "📤 Requisition submitted to admin for approval.")

    # Step-(H6)-Redirect back to team dashboard #
    return redirect(reverse('requisition_dashboard'))

# I - Update Requisition Status (Admin only)
@login_required
def update_requisition_status(request, pk):
    requisition = get_object_or_404(Requisition, pk=pk)

    if not is_django_admin(request.user):
        raise PermissionDenied

    # Accept both GET and POST
    action = request.POST.get("action") if request.method == "POST" else request.GET.get("action")

    if action == "approve":
        requisition.status = "Approved"
        messages.success(request, "✅ Requisition approved successfully.")
    elif action == "reject":
        requisition.status = "Rejected"
        messages.warning(request, "❌ Requisition rejected.")
    elif action == "pending":
        requisition.status = "Pending"
        messages.info(request, "⏳ Requisition marked as pending.")
    else:
        messages.error(request, "⚠️ Invalid action.")

    requisition.save()
    return redirect(reverse("requisition_dashboard"))

# J - Auto-Fill API (Used by JavaScript) #
def get_requisition_details(request, pk):
    resource = get_object_or_404(Resource, pk=pk)
    return JsonResponse({
        "unit": resource.unit or "",   # <-- match your model field name
    })

