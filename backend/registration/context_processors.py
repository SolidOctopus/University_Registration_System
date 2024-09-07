from .models import Profile

def user_role(request):
    if request.user.is_authenticated:
        try:
            user_role = request.user.profile.role
        except Profile.DoesNotExist:
            user_role = None
    else:
        user_role = None
    return {'user_role': user_role}
