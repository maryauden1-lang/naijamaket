from django.contrib import admin
from django.urls import path, include, re_path
from django.shortcuts import redirect
from django.conf import settings
from django.conf.urls.static import static
from django.views.static import serve


def admin_access_guard(request):
    """
    Guards /admin/:
    - If superuser -> allow into standard Django admin
    - If staff (moderator/support) -> redirect straight to /workspace/
    - Otherwise -> standard admin login
    """
    if request.user.is_authenticated:
        if request.user.is_superuser:
            return admin.site.index(request)
        elif request.user.is_staff:
            return redirect('workspace:dashboard')
    return admin.site.login(request, extra_context={'next': '/workspace/'})


urlpatterns = [
    # Guarded root admin entry
    path('admin/', admin_access_guard, name='admin_guard'),
    # Full Django admin sub-routes
    path('admin/', admin.site.urls),
    # Staff workspace portal
    path('workspace/', include('marketplace.workspace_urls')),
    # Public marketplace routes
    path('', include('marketplace.urls')),
]

# Ensure uploaded media serves properly
urlpatterns += [
    re_path(r'^media/(?P<path>.*)$', serve, {'document_root': settings.MEDIA_ROOT}),
]

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)