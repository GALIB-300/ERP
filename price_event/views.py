# A - Import Required Modules #
from django.shortcuts import render, redirect, get_object_or_404
from .models import ResourcePriceEvent
from .forms import ResourcePriceEventForm

# B - Dashboard View (List + Create) #
def price_event_dashboard(request):
    events = ResourcePriceEvent.objects.all().order_by('-effective_from')

    if request.method == 'POST':
        form = ResourcePriceEventForm(request.POST)
        if form.is_valid():
            event = form.save(commit=False)
            event.created_by = request.user
            event.updated_by = request.user
            event.save()
            return redirect('price_event_dashboard')
    else:
        form = ResourcePriceEventForm()

    return render(request, 'price_event/price_event_dashboard.html', {   # ✅ namespaced template
        'events': events,
        'form': form,
        'mode': 'create'
    })

# C - Update View #
def price_event_update(request, pk):
    event = get_object_or_404(ResourcePriceEvent, pk=pk)
    events = ResourcePriceEvent.objects.all().order_by('-effective_from')

    if request.method == 'POST':
        form = ResourcePriceEventForm(request.POST, instance=event)
        if form.is_valid():
            event = form.save(commit=False)
            event.updated_by = request.user
            event.save()
            return redirect('price_event_dashboard')
    else:
        form = ResourcePriceEventForm(instance=event)

    return render(request, 'price_event/price_event_dashboard.html', {   # ✅ namespaced template
        'events': events,
        'form': form,
        'mode': 'update',
        'edit_event': event
    })

# D - Delete View #
def price_event_delete(request, pk):
    event = get_object_or_404(ResourcePriceEvent, pk=pk)
    events = ResourcePriceEvent.objects.all().order_by('-effective_from')

    if request.method == 'POST':
        event.delete()
        return redirect('price_event_dashboard')

    return render(request, 'price_event/price_event_dashboard.html', {   # ✅ namespaced template
        'events': events,
        'form': ResourcePriceEventForm(),
        'mode': 'delete',
        'delete_event': event
    })

    # E - Processing Page View #
def price_event_process(request):
    # Example: group events by resource/supplier and show cumulative history
    events = ResourcePriceEvent.objects.all().order_by('resource_name', 'supplier_name', '-effective_from')

    return render(request, 'price_event/price_event_process.html', {
        'events': events
    })
