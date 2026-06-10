from accounts.models import Profile

def user_profile(request):
    if request.user.is_authenticated:
        username = request.user.username.lower()

        # Define department access per user (hardcoded fallback)
        department_access = {
            'jakir': ['salesmarketing', 'construction'],
            'asif': ['construction'],
            'belal': ['salesmarketing'],
            'emon': ['salesmarketing'],
        }

        try:
            profile = Profile.objects.get(user=request.user)
            # Use hardcoded mapping if present, otherwise pull from ManyToMany
            departments = department_access.get(
                username,
                list(profile.departments.values_list("name", flat=True))
            )
            return {
                'user_profile': profile,
                'user_departments': departments,
            }
        except Profile.DoesNotExist:
            return {
                'user_departments': department_access.get(username, []),
            }

    return {}
