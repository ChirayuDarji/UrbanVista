# mysite/views.py
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from allauth.socialaccount.models import SocialAccount

# Optional if you have the incidents app
try:
    from incidents.models import Incident
except Exception:
    Incident = None

def home(request):
    context = {}
    if request.user.is_authenticated:
        # Connected social accounts (Google will be one of them)
        context["social_accounts"] = SocialAccount.objects.filter(user=request.user)

        if Incident is not None:
            context["incidents_created_recent"] = (
                Incident.objects.filter(created_by=request.user)
                .order_by("-created_at")[:5]
            )
            context["incidents_assigned_recent"] = (
                Incident.objects.filter(assignees=request.user)
                .order_by("-created_at")[:5]
            )
            context["incidents_created_count"] = (
                Incident.objects.filter(created_by=request.user).count()
            )
            context["incidents_assigned_count"] = (
                Incident.objects.filter(assignees=request.user).count()
            )
    return render(request, "home.html", context)


def about(request):
    """About Us page view."""
    context = {
        'title': 'About Us',
    }
    return render(request, "about.html", context)

def help_center(request):
    """Help Center & FAQ page."""
    return render(request, "help_center.html")