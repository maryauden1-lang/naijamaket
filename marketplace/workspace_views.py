from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.contrib.auth import logout
from django.utils import timezone
from django.db.models import Q
from .models import Listing, SellerProfile, ReportedListing, StaffActivityLog
from .workspace_guards import staff_workspace_required, log_staff_action


@staff_workspace_required()
def workspace_dashboard(request):
    """Central operations dashboard for staff members and CEO"""
    user = request.user
    role = 'ceo' if user.is_superuser else getattr(user, 'staff_profile', None).role if hasattr(user, 'staff_profile') else 'staff'

    context = {
        'role': role,
        'is_ceo': user.is_superuser,
        'pending_listings_count': Listing.objects.filter(status='pending').count(),
        'pending_kyc_count': SellerProfile.objects.filter(
            Q(verification_status='pending') | 
            (Q(is_nin_verified=False) & (Q(id_document__isnull=False) & ~Q(id_document='') | Q(selfie_image__isnull=False) & ~Q(selfie_image='')))
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
    
    ad = Listing.objects.filter(
        status='pending',
        locked_by=request.user,
        locked_at__gte=now - timezone.timedelta(minutes=10)
    ).first()

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


# ==========================================
# CEO KYC VERIFICATION DESK (SUPERUSER ONLY)
# ==========================================
@staff_workspace_required()
def kyc_review_list(request):
    """Only the CEO/Superuser can review personal NIN documents and selfies"""
    if not request.user.is_superuser:
        messages.error(request, "Access Denied: Only the CEO/Superuser is authorized to inspect sensitive identity documents.")
        return redirect('workspace:dashboard')

    # Fetch all sellers pending verification review
    pending_profiles = SellerProfile.objects.filter(
        Q(verification_status='pending') | 
        (Q(is_nin_verified=False) & (Q(id_document__isnull=False) & ~Q(id_document='') | Q(selfie_image__isnull=False) & ~Q(selfie_image='')))
    ).select_related('user', 'state', 'area').order_by('-verification_submitted_at', '-id')

    context = {
        'pending_profiles': pending_profiles,
        'total_pending': pending_profiles.count(),
    }
    return render(request, 'workspace/kyc_review.html', context)


@staff_workspace_required()
def kyc_decision_action(request, profile_id):
    """CEO decision processor: approve blue badge or reject with custom feedback"""
    if not request.user.is_superuser:
        messages.error(request, "Access Denied: Superuser credentials required.")
        return redirect('workspace:dashboard')

    if request.method != 'POST':
        return redirect('workspace:kyc_list')

    profile = get_object_or_404(SellerProfile, id=profile_id)
    decision = request.POST.get('decision')
    feedback = request.POST.get('feedback', '').strip()

    if decision == 'approve':
        profile.is_nin_verified = True
        profile.verification_status = 'verified'
        profile.verification_feedback = None
        profile.save()

        log_staff_action(
            staff_user=request.user,
            action='verify_nin',
            target_id=f"User #{profile.user.id} ({profile.user.username})",
            details="CEO verified NIN and face biometric. Blue verification badge awarded.",
            request=request
        )
        messages.success(request, f"Merchant '{profile.user.username}' is now verified with the official Blue Badge!")

    elif decision == 'reject':
        if not feedback:
            messages.error(request, "Please type a reason explaining why the submission was disapproved.")
            return redirect('workspace:kyc_list')

        profile.is_nin_verified = False
        profile.verification_status = 'rejected'
        profile.verification_feedback = feedback
        profile.save()

        log_staff_action(
            staff_user=request.user,
            action='reject_nin',
            target_id=f"User #{profile.user.id} ({profile.user.username})",
            details=f"CEO Disapproved KYC: {feedback}",
            request=request
        )
        messages.warning(request, f"Verification for '{profile.user.username}' was disapproved. Feedback sent to seller.")

    return redirect('workspace:kyc_list')


def staff_logout_view(request):
    """Safely logs out the staff member and sends them to the workspace login"""
    logout(request)
    messages.info(request, "You have been logged out successfully.")
    return redirect('/admin/login/?next=/workspace/')


def smart_login_redirect(request):
    """
    Intelligent router after login:
    - Non-superusers with staff profiles go straight to /workspace/
    - Superusers (CEO) can directly access /workspace/ with CEO tools
    - Normal buyers/sellers go to home
    """
    if not request.user.is_authenticated:
        return redirect('/admin/login/?next=/workspace/')

    # Operational staff and CEO both route to workspace
    if request.user.is_staff or request.user.is_superuser:
        return redirect('workspace:dashboard')

    return redirect('/')