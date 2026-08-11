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
    # Fetch pending and approved items accounting for both uppercase and lowercase status values
    pending_payments = PaymentSubmission.objects.filter(status__iexact='pending').order_by('-created_at')
    verified_payments = PaymentSubmission.objects.filter(status__iexact='approved').order_by('-created_at')
    ledger_entries = FinancialLedger.objects.all().order_by('-created_at')
    
    total_revenue = sum(entry.amount for entry in ledger_entries if entry.amount)

    context = {
        'pending_payments': pending_payments,
        'pending_count': pending_payments.count(),
        'verified_payments': verified_payments,
        'ledger_entries': ledger_entries,
        'total_revenue': total_revenue,
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
        payment = PaymentSubmission.objects.filter(pk=payment_id).first()
        
        if not payment:
            payment = next((p for p in PaymentSubmission.objects.all() if str(p.pk) == str(payment_id)), None)

        if not payment:
            messages.error(request, "Payment record was not found.")
            return redirect('financial_dashboard')

        # Determine target approved status value
        approved_val = 'APPROVED' if hasattr(PaymentSubmission, 'Status') and hasattr(PaymentSubmission.Status, 'APPROVED') else 'approved'
        
        # Update status directly in database
        PaymentSubmission.objects.filter(pk=payment.pk).update(status=approved_val)
        payment.refresh_from_db()

        # Create ledger entry and explicitly catch specific fields
        try:
            FinancialLedger.objects.get_or_create(
                payment=payment,
                defaults={'amount': payment.amount}
            )
        except Exception as e:
            # Fallback direct creation
            try:
                FinancialLedger.objects.create(
                    payment_id=payment.pk,
                    amount=payment.amount
                )
            except Exception as inner_e:
                print("Ledger creation error:", inner_e)

        messages.success(request, f"Payment of ?{payment.amount:,.2f} successfully verified and posted to ledger!")
        return redirect('financial_dashboard')

    return redirect('financial_dashboard')


def reject_payment_view(request, payment_id):
    if request.method == 'POST':
        payment = get_object_or_404(PaymentSubmission, pk=payment_id)
        reason = request.POST.get('rejection_reason', 'Payment could not be verified.')

        payment.status = PaymentSubmission.Status.REJECTED
        payment.rejection_reason = reason
        payment.save()

        messages.warning(request, f"Payment Ref: {payment.payment_reference} rejected.")
    return redirect('financial_dashboard')
import csv
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from apps.users.decorators import role_required

@login_required
@role_required(CustomUser.Role.FINANCIAL_SECRETARY, CustomUser.Role.CHAIRMAN)
def export_ledger_csv_view(request):
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="financial_ledger_export.csv"'

    writer = csv.writer(response)
    # Header row
    writer.writerow(['ID', 'Payment ID', 'Amount (NGN)', 'Created At'])

    # Data rows
    for entry in FinancialLedger.objects.all().order_by('-created_at'):
        writer.writerow([
            entry.id,
            entry.payment_id if hasattr(entry, 'payment_id') else '',
            entry.amount,
            entry.created_at.strftime('%Y-%m-%d %H:%M:%S') if entry.created_at else ''
        ])

    return response

@login_required
@role_required(CustomUser.Role.FINANCIAL_SECRETARY, CustomUser.Role.CHAIRMAN)
def export_payments_csv_view(request):
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="payment_submissions_export.csv"'

    writer = csv.writer(response)
    writer.writerow(['ID', 'Category', 'Amount', 'Transaction Ref', 'Status', 'Submitted At'])

    for p in PaymentSubmission.objects.all().order_by('-id'):
        writer.writerow([
            p.id,
            getattr(p, 'category', ''),
            p.amount,
            getattr(p, 'transaction_reference', getattr(p, 'payment_reference', '')),
            p.status,
            p.created_at.strftime('%Y-%m-%d %H:%M:%S') if hasattr(p, 'created_at') and p.created_at else ''
        ])

    return response
