from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import Profile

@login_required
def profile_list(request):
    profiles = Profile.objects.select_related('user').all()
    return render(request, 'accounts/profile_list.html', {'profiles': profiles})

@login_required
def profile_detail(request, user_id):
    profile = get_object_or_404(Profile, user__id=user_id)
    return render(request, 'accounts/profile_detail.html', {'profile': profile})
