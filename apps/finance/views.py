from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db import transaction
from django.db.models import Sum
from apps.users.decorators import role_required
from apps.users.models import CustomUser
from .models import PaymentSubmission, FinancialLedger, PaymentCategory
from .forms import PaymentSubmissionForm

@login_required
@role_required(CustomUser.Role.FINANCIAL_SECRETARY, CustomUser.Role.CHAIRMAN)
def financial_dashboard_view(request):
    pending_payments = PaymentSubmission.objects.filter(status=PaymentSubmission.Status.PENDING)
    verified_payments = PaymentSubmission.objects.filter(status='approved')
    ledger_entries = FinancialLedger.objects.all()

    total_revenue = FinancialLedger.objects.filter(
        transaction_type='credit'
    ).aggregate(Sum('amount'))['amount__sum'] or 0.00

    context = {
        'pending_payments': pending_payments,
        'verified_payments': verified_payments,
        'ledger_entries': ledger_entries,
        'total_revenue': total_revenue,
        'pending_count': pending_payments.count(),
    }
    return render(request, 'dashboards/financial.html', context)

@login_required
def submit_payment_view(request):
    if request.method == 'POST':
        form = PaymentSubmissionForm(request.POST, request.FILES)
        if form.is_valid():
            try:
                payment = form.save(commit=False)
                payment.member = request.user.profile
                payment.status = PaymentSubmission.Status.PENDING
                payment.save()

                messages.success(request, 'Payment proof submitted successfully! Awaiting verification.')
                return redirect('member_dashboard')
            except Exception as e:
                messages.error(request, f'Submission error: {str(e)}')
    else:
        form = PaymentSubmissionForm()

    return render(request, 'finance/submit_payment.html', {'form': form})

@login_required
@role_required(CustomUser.Role.FINANCIAL_SECRETARY, CustomUser.Role.CHAIRMAN)
def verify_payment_view(request, payment_id):
    if request.method == 'POST':
        payment = get_object_or_404(PaymentSubmission, id=payment_id)
        
        with transaction.atomic():
            payment.status = 'approved'
            payment.save()

            # Post double-entry transaction into immutable Ledger
            FinancialLedger.objects.create(
                submission=payment,
                transaction_type='credit',
                amount=payment.amount,
                description=f"Payment for {payment.category.name} by {payment.member.first_name} {payment.member.last_name} ({payment.member.member_number})",
                posted_by=request.user
            )

        messages.success(request, f"Payment Ref: {payment.payment_reference} verified and posted to Ledger.")
    return redirect('financial_dashboard')

@login_required
@role_required(CustomUser.Role.FINANCIAL_SECRETARY, CustomUser.Role.CHAIRMAN)
def reject_payment_view(request, payment_id):
    if request.method == 'POST':
        payment = get_object_or_404(PaymentSubmission, id=payment_id)
        reason = request.POST.get('rejection_reason', 'Payment could not be verified.')

        payment.status = PaymentSubmission.Status.REJECTED
        payment.rejection_reason = reason
        payment.save()

        messages.warning(request, f"Payment Ref: {payment.payment_reference} rejected.")
    return redirect('financial_dashboard')
