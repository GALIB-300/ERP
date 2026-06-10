# A - Import Required Modules #
from django.shortcuts import render, get_object_or_404, redirect
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.http import JsonResponse
from django.contrib import messages
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from urllib.parse import urlencode

from .forms import LetterForm
from .models import Letter

# B-Django Admin Check #
def is_django_admin(user):
    # Adjust this to match your custom user model #
    return getattr(user, "role", None) == "admin"

# C - Filtering Function (Client Name + WO No + Bill No) #
def filter_letters(query=None, client_name_letter=None, wo_no_letter=None, bill_no_letter=None,
                   user=None, is_admin=False, exclude_user=None):
    # Base queryset
    if is_admin:
        queryset = Letter.objects.all()
    else:
        queryset = Letter.objects.filter(created_by=user)

    # Exclude specific user if provided
    if exclude_user:
        queryset = queryset.exclude(created_by=exclude_user)

    # Free text search across client, WO No, and Bill No
    if query:
        queryset = queryset.filter(
            Q(client_name_letter__client_name_cba__client_name_ctv__client_name_pt__name_of_client__icontains=query) |
            Q(wo_no_letter__wo_no_cba__wo_no_ctv__icontains=query) |
            Q(bill_no_letter__bill_no_cba__icontains=query)
        )

    # Filter by client name (deep chain)
    if client_name_letter:
        queryset = queryset.filter(
            client_name_letter__client_name_cba__client_name_ctv__client_name_pt__name_of_client__icontains=client_name_letter
        )

    # Filter by WO No (CBA field)
    if wo_no_letter:
        queryset = queryset.filter(wo_no_letter__wo_no_cba__wo_no_ctv__icontains=wo_no_letter)

    # Filter by Bill No (CBA field)
    if bill_no_letter:
        queryset = queryset.filter(bill_no_letter__bill_no_cba__icontains=bill_no_letter)

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

# E-Team will view their own letters #
@login_required
def letter_list(request):
    # Search filters
    query = request.GET.get("q", "").strip()
    client_name_letter = request.GET.get("client_name_letter", "").strip()
    wo_no_letter = request.GET.get("wo_no_letter", "").strip()
    bill_no_letter = request.GET.get("bill_no_letter", "").strip()

    # Check if user is admin
    is_admin = is_django_admin(request.user)

    # Filter letters: admin sees all, team sees only their own
    letters_queryset = filter_letters(
        query=query,
        client_name_letter=client_name_letter,
        wo_no_letter=wo_no_letter,
        bill_no_letter=bill_no_letter,
        user=request.user,
        is_admin=is_admin
    )

    # ✅ Apply pagination
    letters = get_paginated_queryset(request, letters_queryset, per_page=10)

    context = {
        "letters": letters,
        "query": query,
        "client_name_letter": client_name_letter,
        "wo_no_letter": wo_no_letter,
        "bill_no_letter": bill_no_letter,
        "readonly": is_admin,   # admins are readonly
        "is_admin": is_admin,
    }
    return render(request, "letter/letter_list.html", context)

# F-Team will add letters #
@login_required
def letter_add(request):
    form = LetterForm(request.POST or None, user=request.user)  # ✅ pass user for dropdowns

    if request.method == "POST" and form.is_valid():
        letter = form.save(commit=False)
        letter.created_by = request.user
        letter.team = getattr(
            getattr(request.user, "letter_profile", None),
            "role",
            "manager_sales"   # default role
        )
        letter.save()
        messages.success(request, "✅ Letter record created successfully.")
        return redirect(
            f"{reverse('letter_list')}?q=&client_name_letter=&wo_no_letter=&bill_no_letter="
        )

    context = {
        "form": form,
        "readonly": False,
        "is_admin": False,
    }
    return render(request, "letter/letter_form.html", context)

# G-Admin will view all letters #
@login_required
def letter_list(request):
    # Search filters
    query = request.GET.get("q", "").strip()
    client_name_letter = request.GET.get("client_name_letter", "").strip()
    wo_no_letter = request.GET.get("wo_no_letter", "").strip()
    bill_no_letter = request.GET.get("bill_no_letter", "").strip()

    # Check if user is admin
    is_admin = is_django_admin(request.user)

    # Filter letters: admin sees all, team sees only their own
    letters_queryset = filter_letters(
        query=query,
        client_name_letter=client_name_letter,
        wo_no_letter=wo_no_letter,
        bill_no_letter=bill_no_letter,
        user=request.user,
        is_admin=is_admin
    )

    # ✅ Apply pagination
    letters = get_paginated_queryset(request, letters_queryset, per_page=10)

    context = {
        "letters": letters,
        "query": query,
        "client_name_letter": client_name_letter,
        "wo_no_letter": wo_no_letter,
        "bill_no_letter": bill_no_letter,
        "readonly": is_admin,   # admins are readonly
        "is_admin": is_admin,
    }
    return render(request, "letter/letter_list.html", context)

# H-Team will edit their own letters. Admin cannot edit #
@login_required
def edit_letter(request, pk):
    # Step-(A1)-Get letter by ID
    letter = get_object_or_404(Letter, pk=pk)

    # Step-(A2)-Check if user is admin (custom helper)
    is_admin = is_django_admin(request.user)

    # Step-(A3)-Permission check: only team member who created letter can edit
    if is_admin or letter.created_by != request.user:
        raise PermissionDenied

    # Step-(A4)-Search Query parameter-(q)-from the URL
    query = (request.GET.get("q") or "").strip()

    # Step-(A5)-Letter filters from the URL
    client_name_letter = (request.GET.get("client_name_letter") or "").strip()
    wo_no_letter = (request.GET.get("wo_no_letter") or "").strip()
    bill_no_letter = (request.GET.get("bill_no_letter") or "").strip()

    # Step-(A6)-Initialize form with letter instance ✅
    form = LetterForm(request.POST or None, instance=letter, user=request.user)

    # Step-(A7)-Save edits if valid
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "✏️ Letter record updated successfully.")
        params = urlencode({
            "q": query,
            "client_name_letter": client_name_letter,
            "wo_no_letter": wo_no_letter,
            "bill_no_letter": bill_no_letter,
        })
        return redirect(f"{reverse('letter_list')}?{params}")

    # Step-(A8)-Prepare context for edit template
    context = {
        "form": form,
        "mode": "edit",
        "letter": letter,
        "query": query,
        "client_name_letter": client_name_letter,
        "wo_no_letter": wo_no_letter,
        "bill_no_letter": bill_no_letter,
        "readonly": False,
        "is_admin": is_admin,
    }
    return render(request, "letter/letter_form.html", context)

# I-Team delete their own letters. Admin cannot delete #
@login_required
def delete_letter(request, pk):
    # Step-(A1)-Get letter by ID
    letter = get_object_or_404(Letter, pk=pk)

    # Step-(A2)-Check if user is admin (custom helper)
    is_admin = is_django_admin(request.user)

    # Step-(A3)-Permission check: only team member who created letter can delete
    if is_admin or letter.created_by != request.user:
        raise PermissionDenied

    # Step-(A4)-Search Query parameter-(q)-from the URL
    query = (request.GET.get("q") or "").strip()

    # Step-(A5)-Letter filters from the URL
    client_name_letter = (request.GET.get("client_name_letter") or "").strip()
    wo_no_letter = (request.GET.get("wo_no_letter") or "").strip()
    bill_no_letter = (request.GET.get("bill_no_letter") or "").strip()

    # Step-(A6)-Delete letter (only team users can delete)
    if request.method == "POST":
        subject = letter.subject
        letter.delete()
        messages.success(request, f"🗑️ Letter '{subject}' deleted successfully.")
        params = urlencode({
            "q": query,
            "client_name_letter": client_name_letter,
            "wo_no_letter": wo_no_letter,
            "bill_no_letter": bill_no_letter,
        })
        return redirect(f"{reverse('letter_list')}?{params}")

    # Step-(A7)-Prepare context for delete confirmation template
    context = {
        "letter": letter,
        "query": query,
        "client_name_letter": client_name_letter,
        "wo_no_letter": wo_no_letter,
        "bill_no_letter": bill_no_letter,
        "is_admin": is_admin,
        "readonly": True    # Admins are readonly, team confirm delete
    }

    # Step-(A8)-Render delete confirmation template
    return render(request, "letter/confirm_delete.html", context)

# I - Print Dashboard View-Bason on-(letter_print.html) #
@login_required
def letter_print(request):
    client_name_letter = request.GET.get("client_name_letter")
    wo_no_letter       = request.GET.get("wo_no_letter")
    bill_no_letter     = request.GET.get("bill_no_letter")

    letter_list = Letter.objects.all().order_by("client_name_letter")

    if client_name_letter:
        letter_list = letter_list.filter(
            client_name_letter__client_name_cba__client_name_ctv__client_name_pt__name_of_client__icontains=client_name_letter
        )

    if wo_no_letter:
        # Ensure this ends on a CharField in your model
        letter_list = letter_list.filter(
            wo_no_letter__wo_no_cba__wo_no_ctv__icontains=wo_no_letter
        )

    if bill_no_letter:
        # Ensure this ends on a CharField in your model
        letter_list = letter_list.filter(
            bill_no_letter__bill_no_cba__icontains=bill_no_letter
        )

    context = {
        "letter_list": letter_list,
        "client_name_letter": client_name_letter,
        "wo_no_letter": wo_no_letter,
        "bill_no_letter": bill_no_letter,
    }
    return render(request, "letter/letter_print.html", context)