# A - Import Required Modules #
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied

from .forms import CompanyForm
from .models import Company

# B - Django Admin Check #
def is_django_admin(user):
    return user.is_superuser

# C - Dashboard View (Admin view all companies. Team view/add their own companies) #
@login_required
def company_dashboard(request):
    # Step-(A1) - Check if user is admin #
    is_admin = is_django_admin(request.user)

    # Step-(A2) - Initialize form only for non-admin users #
    form = None if is_admin else CompanyForm(request.POST or None)

    # Step-(A3) - Queryset (Admin sees all, team sees own) #
    companies = Company.objects.all() if is_admin else Company.objects.filter(created_by=request.user)

    # Step-(A4) - Add new company only if user is NOT admin #
    if not is_admin and request.method == "POST" and form.is_valid():
        company = form.save(commit=False)
        company.created_by = request.user
        company.team = getattr(
            getattr(request.user, "company_profile", None),
            "role",
            "manager_construction"
        )
        company.save()
        messages.success(request, "✅ Company record created successfully.")
        return redirect(reverse("company_dashboard"))

    # Step-(A5) - Prepare context #
    context = {
        "companies": companies,
        "form": form,
        "mode": "list",
        "readonly": is_admin,
        "is_admin": is_admin,
    }

    # Step-(A6) - Render template #
    return render(request, "company/company_dashboard.html", context)

# D - Edit View (Team edit only their own companies. Admin cannot edit) #
@login_required
def edit_company(request, pk):
    company = get_object_or_404(Company, pk=pk)
    is_admin = is_django_admin(request.user)

    if is_admin or company.created_by != request.user:
        raise PermissionDenied

    form = CompanyForm(request.POST or None, instance=company)

    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "✏️ Company record updated successfully.")
        return redirect(reverse("company_dashboard"))

    context = {
        "form": form,
        "mode": "edit",
        "company": company,
        "readonly": False,
        "is_admin": is_admin,
        "companies": Company.objects.filter(created_by=request.user),
    }
    return render(request, "company/company_dashboard.html", context)

# E - Delete View (Team delete only their own companies. Admin cannot delete) #
@login_required
def delete_company(request, pk):
    company = get_object_or_404(Company, pk=pk)
    is_admin = is_django_admin(request.user)

    if is_admin or company.created_by != request.user:
        raise PermissionDenied

    if request.method == "POST":
        name = company.company_name
        company.delete()
        messages.success(request, f"🗑️ Company '{name}' deleted successfully.")
        return redirect(reverse("company_dashboard"))

    context = {
        "company": company,
        "is_admin": is_admin,
        "readonly": True,
    }
    return render(request, "company/confirm_delete.html", context)

