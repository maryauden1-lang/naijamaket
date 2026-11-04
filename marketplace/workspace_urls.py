from django.urls import path
from . import workspace_views

app_name = 'workspace'

urlpatterns = [
    path('', workspace_views.workspace_dashboard, name='dashboard'),
    path('routing/', workspace_views.smart_login_redirect, name='smart_login_redirect'),
    path('queue/ads/', workspace_views.ad_review_queue, name='ad_queue'),
    path('action/ad/<int:listing_id>/', workspace_views.ad_action, name='ad_action'),
    path('logout/', workspace_views.staff_logout_view, name='logout'),
]