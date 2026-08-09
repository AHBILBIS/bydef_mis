from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from apps.users.decorators import role_required
from apps.users.models import CustomUser
from .models import MemberProfile

@login_required
@role_required(CustomUser.Role.CHAIRMAN)
def chairman_dashboard_view(request):
    pending_members = MemberProfile.objects.filter(status=MemberProfile.Status.PENDING)
    approved_members = MemberProfile.objects.filter(status=MemberProfile.Status.APPROVED)
    rejected_members = MemberProfile.objects.filter(status=MemberProfile.Status.REJECTED)

    context = {
        'pending_members': pending_members,
        'approved_members': approved_members,
        'rejected_members': rejected_members,
        'total_pending': pending_members.count(),
        'total_approved': approved_members.count(),
    }
    return render(request, 'dashboards/chairman.html', context)

@login_required
@role_required(CustomUser.Role.CHAIRMAN)
def approve_member_view(request, member_id):
    if request.method == 'POST':
        member = get_object_or_404(MemberProfile, id=member_id)
        
        # Auto-generate Member ID sequence
        current_year = timezone.now().year
        approved_count = MemberProfile.objects.filter(status=MemberProfile.Status.APPROVED).count() + 1
        generated_id = f"BYDEF-{current_year}-{approved_count:04d}"

        member.status = MemberProfile.Status.APPROVED
        member.member_number = generated_id
        member.approved_by = request.user
        member.approved_at = timezone.now()
        member.save()

        messages.success(request, f"Member {member.first_name} {member.last_name} approved successfully with ID: {generated_id}")
    return redirect('chairman_dashboard')

@login_required
@role_required(CustomUser.Role.CHAIRMAN)
def reject_member_view(request, member_id):
    if request.method == 'POST':
        member = get_object_or_404(MemberProfile, id=member_id)
        reason = request.POST.get('rejection_reason', 'Requirements not met.')

        member.status = MemberProfile.Status.REJECTED
        member.rejection_reason = reason
        member.save()

        messages.warning(request, f"Registration for {member.first_name} {member.last_name} has been rejected.")
    return redirect('chairman_dashboard')
