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
from django.db.models import Avg

from .forms import WsForm
from .models import Ws

# B-Django Admin Check #
def is_django_admin(user):
    # Adjust this to match your custom user model #
    return getattr(user, "role", None) == "admin"

# C-Filtering Function-(Admin view all data & search filtering by-Project Name and Team view their own data & search filtering by-Project Name) #
def filter_wss(query=None, project_name_ws=None, user=None, is_admin=False, exclude_user=None):
    # Base queryset #
    if is_admin:
        # Admins see all ws #
        queryset = Ws.objects.all()
    else:
        # Team members see only their own ws #
        queryset = Ws.objects.filter(created_by=user)

    # Exclude specific user if provided-(removes ws created by a specific user from the results) #
    if exclude_user:
        queryset = queryset.exclude(created_by=exclude_user)

    # Free text search across multiple fields #
    if query:
        queryset = queryset.filter(
            Q(project_name_ws__icontains=query) |
            Q(task_name_ws__icontains=query)
        )

    # Filter by project name #
    if project_name_ws:
        queryset = queryset.filter(project_name_ws__icontains=project_name_ws)

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

# E-Team will view their own ws #
@login_required
def ws_list(request):
    # Search filters
    query = request.GET.get("q", "").strip()
    project_name_ws = request.GET.get("project_name_ws", "").strip()

    # Check if user is admin
    is_admin = is_django_admin(request.user)

    # Filter ws: admin sees all, team sees only their own
    wss_queryset = filter_wss(
        query=query,
        project_name_ws=project_name_ws,
        user=request.user,
        is_admin=is_admin
    )

    # ✅ Apply pagination
    wss = get_paginated_queryset(request, wss_queryset, per_page=10)

    # ✅ Calculate averages in Python (based on full queryset)
    planned_values = [ws.planned_progress for ws in wss_queryset]
    actual_values = [ws.actual_progress for ws in wss_queryset]

    average_planned_progress = round(sum(planned_values) / len(planned_values), 2) if planned_values else 0
    average_actual_progress = round(sum(actual_values) / len(actual_values), 2) if actual_values else 0

    context = {
        "ws_projects": wss,   # paginated queryset for table display
        "query": query,
        "project_name_ws": project_name_ws,
        "readonly": is_admin,   # admins are readonly
        "is_admin": is_admin,
        "average_planned_progress": average_planned_progress,
        "average_actual_progress": average_actual_progress,
    }
    return render(request, "ws/ws_list.html", context)

# F-Team will add data #
@login_required
def ws_add(request):
    form = WsForm(request.POST or None)

    if request.method == "POST":
        if form.is_valid():
            ws = form.save(commit=False)
            ws.created_by = request.user
            ws.team = getattr(
                getattr(request.user, "ws_profile", None),
                "role",
                "manager_construction"
            )
            ws.save()
            messages.success(request, "✅ WS record created successfully.")
            return redirect(f"{reverse('ws_list')}?q=&project_name_ws=")
        else:
            messages.error(request, "❌ Please correct the errors below.")
            print(form.errors)  # Debugging in console

    context = {
        "form": form,
        "readonly": False,
        "is_admin": False,
    }
    return render(request, "ws/ws_form.html", context)

# G-Admin will view all ws #
@login_required
def ws_list(request):
    # Search filters
    query = request.GET.get("q", "").strip()
    project_name_ws = request.GET.get("project_name_ws", "").strip()

    # Check if user is admin
    is_admin = is_django_admin(request.user)

    # Filter ws: admin sees all, team sees only their own
    wss_queryset = filter_wss(
        query=query,
        project_name_ws=project_name_ws,
        user=request.user,
        is_admin=is_admin
    )

    # ✅ Apply pagination
    wss = get_paginated_queryset(request, wss_queryset, per_page=10)

    # ✅ Calculate averages in Python (based on full queryset)
    planned_values = [ws.planned_progress for ws in wss_queryset]
    actual_values = [ws.actual_progress for ws in wss_queryset]

    average_planned_progress = round(sum(planned_values) / len(planned_values), 2) if planned_values else 0
    average_actual_progress = round(sum(actual_values) / len(actual_values), 2) if actual_values else 0

    context = {
        "ws_projects": wss,   # paginated queryset
        "query": query,
        "project_name_ws": project_name_ws,
        "readonly": is_admin,   # admins are readonly
        "is_admin": is_admin,
        "average_planned_progress": average_planned_progress,
        "average_actual_progress": average_actual_progress,
    }
    return render(request, "ws/ws_list.html", context)

# H-Team will edit their own ws. Admin cannot edit #
@login_required
def edit_ws(request, pk):
    # Step-(A1)-Get ws by ID
    ws = get_object_or_404(Ws, pk=pk)

    # Step-(A2)-Check if user is admin (custom helper)
    is_admin = is_django_admin(request.user)

    # Step-(A3)-Permission check: only team member who created ws can edit
    if is_admin or ws.created_by != request.user:
        raise PermissionDenied

    # Step-(A4)-Search Query parameter-(q)-from the URL
    query = (request.GET.get("q") or "").strip()

    # Step-(A5)-Project name-based query parameter-from the URL
    project_name_ws = (request.GET.get("project_name_ws") or "").strip()

    # Step-(A6)-Initialize form with ws instance
    form = WsForm(request.POST or None, instance=ws)

    # Step-(A7)-Save edits if valid
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "✏️ WS record updated successfully.")
        params = urlencode({
            "q": query,
            "project_name_ws": project_name_ws,
        })
        return redirect(f"{reverse('ws_list')}?{params}")

    # Step-(A8)-Prepare context for edit template
    context = {
        "form": form,
        "mode": "edit",
        "ws": ws,
        "query": query,
        "project_name_ws": project_name_ws,
        "readonly": False,
        "is_admin": is_admin,
    }

    # Step-(A9)-Render dedicated form template
    return render(request, "ws/ws_form.html", context)

# I-Team delete their own ws. Admin cannot delete #
@login_required
def delete_ws(request, pk):
    ws = get_object_or_404(Ws, pk=pk)
    is_admin = is_django_admin(request.user)

    # Only team member who created ws can delete
    if is_admin or ws.created_by != request.user:
        raise PermissionDenied

    query = (request.GET.get("q") or "").strip()
    ws_name = (request.GET.get("ws_name") or "").strip()

    if request.method == "POST":
        name = ws.project_name_ws   
        ws.delete()
        messages.success(request, f"🗑️ Ws '{name}' deleted successfully.")
        params = urlencode({
            "q": query,
            "ws_name": ws_name,
        })
        return redirect(f"{reverse('ws_list')}?{params}")

    # No need to render confirm_delete.html anymore
    return redirect(f"{reverse('ws_list')}?q={query}&ws_name={ws_name}")

# I - Gantt Chart Data (one bar per task)
def gantt_chart_data(request):
    wss = Ws.objects.filter(
        start_date__isnull=False,
        finish_date__isnull=False
    ).order_by("start_date")

    data = []
    for ws in wss:
        data.append({
            "id": str(ws.id),
            "name": f"{ws.project_name_ws} | {ws.task_name_ws}",
            "start": ws.start_date.strftime('%Y-%m-%d'),
            "end": ws.finish_date.strftime('%Y-%m-%d'),
            "progress": ws.actual_progress or 0,
            "planned_progress": ws.planned_progress or 0
        })
    return JsonResponse(data, safe=False)






