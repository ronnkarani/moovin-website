# decorators.py (create this in your app)
from django.shortcuts import redirect
from .models import UserProfile

def role_required(role):
    def decorator(view_func):
        def _wrapped_view(request, *args, **kwargs):
            if not request.user.is_authenticated:
                return redirect('login')

            user_profile = UserProfile.objects.get(user=request.user)
            if user_profile.role != role:
                return redirect('home')
            return view_func(request, *args, **kwargs)
        return _wrapped_view
    return decorator
