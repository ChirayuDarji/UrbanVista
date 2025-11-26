from django.http import JsonResponse
from django.urls import path
from news.models import News
from reports.models import Report


def healthcheck(_request):
    return JsonResponse({"status": "ok"})


urlpatterns = [
    path("health", healthcheck, name="api-health"),
    path("news", lambda r: JsonResponse({
        "items": [
            {
                "title": n.title,
                "slug": n.slug,
                "category": getattr(n.category, "slug", None),
                "published_at": n.published_at.isoformat() if n.published_at else None,
            }
            for n in News.objects.filter(status='published').order_by('-published_at')[:50]
        ]
    }), name="api-news-list"),
    path("reports", lambda r: JsonResponse({
        "items": [
            {
                "id": rep.id,
                "issue_type": rep.issue_type,
                "status": rep.status,
                "location": rep.location,
                "created_at": rep.created_at.isoformat() if hasattr(rep, 'created_at') else None,
            }
            for rep in Report.objects.all().order_by('-created_at')[:50]
        ]
    }), name="api-reports-list"),
]


