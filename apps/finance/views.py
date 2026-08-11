from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db import connection
from apps.users.decorators import role_required
from apps.users.models import CustomUser
from .models import PaymentSubmission, FinancialLedger

@login_required
def submit_payment_view(request):
    if request.method == 'POST':
        amount = request.POST.get('amount')
        category_id = request.POST.get('category')
        ref = request.POST.get('transaction_reference', '')
        proof = request.FILES.get('proof_of_payment')

        if amount and proof:
            PaymentSubmission.objects.create(
                user=request.user,
                category_id=category_id if category_id else None,
                amount=amount,
                transaction_reference=ref,
                proof_of_payment=proof,
                status='PENDING'
            )
            messages.success(request, "Payment submission received and pending verification!")
            return redirect('financial_dashboard')
        else:
            messages.error(request, "Please fill in all required fields and attach proof of payment.")

    return render(request, 'finance/submit_payment.html')


@login_required
@role_required(CustomUser.Role.FINANCIAL_SECRETARY, CustomUser.Role.CHAIRMAN)
def financial_dashboard_view(request):
    pending_payments = PaymentSubmission.objects.filter(status__iexact='PENDING').order_by('-created_at')
    verified_payments = PaymentSubmission.objects.filter(status__iexact='APPROVED').order_by('-created_at')
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
@role_required(CustomUser.Role.FINANCIAL_SECRETARY, CustomUser.Role.CHAIRMAN)
def verify_payment_view(request, payment_id):
    if request.method == 'POST':
        payment_id_str = str(payment_id).strip()

        with connection.cursor() as cursor:
            cursor.execute(
                "UPDATE finance_paymentsubmission SET status = %s WHERE id::text = %s",
                ['APPROVED', payment_id_str]
            )

            cursor.execute("""
                INSERT INTO finance_financialledger (id, payment_id, amount, transaction_type, description, created_at)
                SELECT gen_random_uuid(), id, amount, 'Credit', 'Verified Payment Submission', NOW()
                FROM finance_paymentsubmission
                WHERE id::text = %s
                ON CONFLICT DO NOTHING
            """, [payment_id_str])

        messages.success(request, "Payment verified and posted to ledger successfully!")
        return redirect('financial_dashboard')

    return redirect('financial_dashboard')


@login_required
@role_required(CustomUser.Role.FINANCIAL_SECRETARY, CustomUser.Role.CHAIRMAN)
def reject_payment_view(request, payment_id):
    if request.method == 'POST':
        payment_id_str = str(payment_id).strip()
        reason = request.POST.get('rejection_reason', 'Payment rejected by administrator.')

        with connection.cursor() as cursor:
            cursor.execute(
                "UPDATE finance_paymentsubmission SET status = %s WHERE id::text = %s",
                ['REJECTED', payment_id_str]
            )

        messages.info(request, "Payment request rejected.")
        return redirect('financial_dashboard')

    return redirect('financial_dashboard')
