import time
from .models import RequestLog
from django.utils.deprecation import MiddlewareMixin
from django.http import HttpResponseServerError
from django.contrib.auth import get_user_model
from django.utils.deprecation import MiddlewareMixin
from django.contrib.auth import get_user_model



User = get_user_model()



class RequestLogMiddleware(MiddlewareMixin):
    def process_request(self, request):
        request.start_time = time.time()
        request._request_body = None
        if request.method in ["POST", "PUT", "PATCH", "DELETE"]:
            content_type = request.META.get("CONTENT_TYPE", "").lower()
            if "multipart/form-data" in content_type:
                # Initialize request body as a dictionary
                request_body = {}
                # Add form fields from request.POST
                if request.POST:
                    request_body.update(dict(request.POST))
                # Add file metadata from request.FILES
                if request.FILES:
                    file_info = {name: f"File: {file.name}, Size: {file.size} bytes" for name, file in request.FILES.items()}
                    request_body.update(file_info)
                # Convert to string for logging
                request._request_body = str(request_body) if request_body else "<empty-multipart>"
            elif "application/json" in content_type or "text/" in content_type:
                # Handle JSON or text-based bodies
                try:
                    request._request_body = request.body.decode("utf-8")
                except UnicodeDecodeError:
                    request._request_body = "<decoding-error>"
            else:
                # Other content types
                request._request_body = "<non-text-body>"
        return None

    def process_response(self, request, response):
        if response is None:
            return HttpResponseServerError("Internal Server Error")

        exclude_paths = [
            '/admin/',
            '/static/',
            '/media/',
            '/center/',
            '/dashboard/logs/',
            '/dashboard/logs/delete/',
        ]
        if any(request.path.startswith(path) for path in exclude_paths):
            return response

        if not request.user.is_authenticated or not request.user.is_staff:
            return response

        if request.method == "GET":
            return response

        response_time_ms = (time.time() - getattr(request, 'start_time', time.time())) * 1000
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        ip_address = x_forwarded_for.split(',')[0] if x_forwarded_for else request.META.get('REMOTE_ADDR')
        query_params = dict(request.GET)

        view_name = None
        if hasattr(response, 'renderer_context') and response.renderer_context:
            view = response.renderer_context.get('view')
            if view:
                view_name = f"{view.__class__.__module__}.{view.__class__.__name__}"

        try:
            RequestLog.objects.create(
                user=request.user,
                ip_address=ip_address,
                path=request.path,
                method=request.method,
                view_name=view_name,
                query_params=query_params,
                status_code=response.status_code,
                response_time=response_time_ms,
                request_body=getattr(request, '_request_body', None)
            )
        except Exception as e:
            print(f"Error logging request: {e}")

        return response