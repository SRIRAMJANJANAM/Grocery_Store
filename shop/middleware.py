from .models import NavigationLog
from datetime import datetime

class NavigationLogMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):

        response = self.get_response(request)

        try:
            if hasattr(request, "user") and request.user.is_authenticated:
                NavigationLog.objects.create(
                    user=request.user,
                    date=datetime.now().date(),
                    time=datetime.now().time(),
                    method=request.method,
                    url=request.path,
                    action=f"{request.method} {request.path}",
                    status_code=response.status_code,
                )
        except Exception as e:
            print("Logging error:", e)

        return response