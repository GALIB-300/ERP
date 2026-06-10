# A - Import Required Modules
from django.shortcuts import render, get_object_or_404, redirect
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.urls import reverse
from django.db.models import Q
from django.contrib import messages
from .models import CustomerDetailed
from .forms import CustomerDetailedForm

# B - Filtering Function
def filter_customerdetaileds(query=None):
    queryset = CustomerDetailed.objects.all()
    if query:
        queryset = queryset.filter(
            Q(name__icontains=query) |
            Q(email__icontains=query) |
            Q(company__icontains=query)
        )
    return queryset

# C - Reusable Pagination Function
def get_paginated_queryset(request, queryset, per_page=10):
    paginator = Paginator(queryset, per_page)
    page_number = request.GET.get("page")

    try:
        return paginator.page(page_number)
    except PageNotAnInteger:
        return paginator.page(1)
    except EmptyPage:
        return paginator.page(paginator.num_pages)

# D - Unified View (List View + Form Submission)
def customerdetailed_dashboard(request):
    query = request.GET.get("q", "").strip()
    customerdetaileds = filter_customerdetaileds(query)
    customerdetaileds_page = get_paginated_queryset(request, customerdetaileds, per_page=10)

    form = CustomerDetailedForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        customer = form.save(commit=False)
        customer.save()
        messages.success(request, "✅ Customer detailed record created successfully.")
        return redirect(f"{reverse('customerdetailed_dashboard')}?q={query}")

    return render(request, "customerdetailed/customerdetailed_dashboard.html", {
        "customerdetaileds": customerdetaileds_page,
        "query": query,
        "form": form,
        "mode": "list"
    })

# E - Edit View (Inline Form + List Table)
def edit_customerdetailed(request, pk):
    customer = get_object_or_404(CustomerDetailed, pk=pk)
    query = request.GET.get("q", "").strip()

    form = CustomerDetailedForm(request.POST or None, instance=customer)
    if form.is_valid():
        form.save()
        messages.success(request, "✏️ Customer detailed record updated successfully.")
        return redirect(f"{reverse('customerdetailed_dashboard')}?q={query}")

    customerdetaileds = filter_customerdetaileds(query)
    customerdetaileds_page = get_paginated_queryset(request, customerdetaileds, per_page=10)

    return render(request, "customerdetailed/customerdetailed_dashboard.html", {
        "form": form,
        "mode": "edit",
        "customer": customer,
        "query": query,
        "customerdetaileds": customerdetaileds_page
    })

# F - Delete View (Renamed to match urls.py)
def Customerdetailed_delete(request, pk):
    customer = get_object_or_404(CustomerDetailed, pk=pk)
    query = request.GET.get("q", "").strip()

    if request.method == 'POST':
        name = customer.name
        customer.delete()
        messages.success(request, f"🗑️ Customer '{name}' deleted successfully.")
        return redirect(f"{reverse('customerdetailed_dashboard')}?q={query}")
