from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.utils import timezone
from django.db.models import Q
from .models import Listing, SellerProfile, ReportedListing, StaffActivityLog
from .workspace_guards import staff_workspace_required, log_staff_action


@staff_workspace_required()
def workspace_dashboard(request):
    """Central operations dashboard for staff members"""
    user = request.user
    role = getattr(user, 'staff_profile', None).role if hasattr(user, 'staff_profile') else 'ceo'

    context = {
        'role': role,
        'pending_listings_count': Listing.objects.filter(status='pending').count(),
        'pending_kyc_count': SellerProfile.objects.filter(
            Q(is_nin_verified=False) & (Q(id_document__isnull=False) & ~Q(id_document=''))
        ).count(),
        'open_reports_count': ReportedListing.objects.filter(is_resolved=False).count(),
        'recent_my_actions': StaffActivityLog.objects.filter(staff=user)[:10],
    }
    return render(request, 'workspace/dashboard.html', context)


@staff_workspace_required(allowed_roles=['moderator'])
def ad_review_queue(request):
    """
    Automated queue distribution:
    Fetches the oldest unmoderated ad and locks it to this moderator for 10 minutes.
    """
    now = timezone.now()
    
    # 1. Check if the moderator already has an active locked ad
    ad = Listing.objects.filter(
        status='pending',
        locked_by=request.user,
        locked_at__gte=now - timezone.timedelta(minutes=10)
    ).first()

    # 2. If no active lock, grab the oldest unallocated pending ad
    if not ad:
        ad = Listing.objects.filter(
            status='pending'
        ).filter(
            Q(locked_by__isnull=True) | Q(locked_at__lt=now - timezone.timedelta(minutes=10))
        ).order_by('created_at').first()

        if ad:
            ad.locked_by = request.user
            ad.locked_at = now
            ad.save(update_fields=['locked_by', 'locked_at'])

    context = {
        'ad': ad,
        'remaining_pending': Listing.objects.filter(status='pending').count()
    }
    return render(request, 'workspace/ad_queue.html', context)


@staff_workspace_required(allowed_roles=['moderator'])
def ad_action(request, listing_id):
    """Process approve or reject for an ad with one click"""
    if request.method != 'POST':
        return redirect('workspace:ad_queue')

    ad = get_object_or_404(Listing, id=listing_id)
    decision = request.POST.get('decision')
    reason = request.POST.get('rejection_reason', '').strip()

    if decision == 'approve':
        ad.status = 'active'
        ad.rejection_reason = None
        ad.moderated_by = request.user
        ad.moderated_at = timezone.now()
        ad.locked_by = None
        ad.locked_at = None
        ad.save()

        log_staff_action(
            staff_user=request.user,
            action='approve_ad',
            target_id=f"Ad #{ad.id} ({ad.title})",
            details="Listing verified and approved for public marketplace.",
            request=request
        )
        messages.success(request, f"Ad '{ad.title}' approved successfully.")

    elif decision == 'reject':
        if not reason:
            messages.error(request, "A reason must be selected to reject an ad.")
            return redirect('workspace:ad_queue')

        ad.status = 'rejected'
        ad.rejection_reason = reason
        ad.moderated_by = request.user
        ad.moderated_at = timezone.now()
        ad.locked_by = None
        ad.locked_at = None
        ad.save()

        log_staff_action(
            staff_user=request.user,
            action='reject_ad',
            target_id=f"Ad #{ad.id} ({ad.title})",
            details=f"Rejection Reason: {reason}",
            request=request
        )
        messages.warning(request, f"Ad '{ad.title}' rejected.")

    return redirect('workspace:ad_queue')