from django.shortcuts import render
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from customerdetailed.models import CustomerDetailed

# 🔁 Reusable Pagination Function
def get_paginated_queryset(request, queryset, per_page=10):
    paginator = Paginator(queryset, per_page)
    page_number = request.GET.get("page")
    try:
        return paginator.page(page_number)
    except PageNotAnInteger:
        return paginator.page(1)
    except EmptyPage:
        return paginator.page(paginator.num_pages)

# 🏗️ Sales & Marketing Customer Detailed List View
def salesmarketing_doc_list(request):
    query = request.GET.get('q', '').strip()
    customerdetaileds = CustomerDetailed.objects.filter(department='salesmarketing')
    if query:
        customerdetaileds = customerdetaileds.filter(name__icontains=query)

    customerdetaileds_page = get_paginated_queryset(request, customerdetaileds, per_page=10)

    return render(request, 'salesmarketing/salesmarketing_doc_list.html', {
        'customerdetaileds': customerdetaileds_page,
        'query': query
    })

