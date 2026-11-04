from django.urls import path
from . import workspace_views

app_name = 'workspace'

urlpatterns = [
    path('', workspace_views.workspace_dashboard, name='dashboard'),
    path('queue/ads/', workspace_views.ad_review_queue, name='ad_queue'),
    path('action/ad/<int:listing_id>/', workspace_views.ad_action, name='ad_action'),
]