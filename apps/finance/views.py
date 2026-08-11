from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db import connection
from apps.users.decorators import role_required
from apps.users.models import CustomUser
from .models import PaymentSubmission, FinancialLedger

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

        # Update PaymentSubmission status via direct SQL execution to bypass ORM UUID numeric casting bug
        with connection.cursor() as cursor:
            cursor.execute(
                "UPDATE finance_paymentsubmission SET status = %s WHERE id::text = %s",
                ['APPROVED', payment_id_str]
            )

        # Retrieve payment for amount check
        payment = PaymentSubmission.objects.filter(pk=payment_id).first()
        amount = payment.amount if payment else 0.00

        # Insert into FinancialLedger via direct SQL execution
        with connection.cursor() as cursor:
            cursor.execute("""
                INSERT INTO finance_financialledger (id, payment_id, amount, transaction_type, description, created_at)
                SELECT gen_random_uuid(), id, amount, 'Credit', 'Verified Payment Submission', NOW()
                FROM finance_paymentsubmission
                WHERE id::text = %s
                ON CONFLICT DO NOTHING
            """, [payment_id_str])

        messages.success(request, f"Payment verified and posted to ledger successfully!")
        return redirect('financial_dashboard')

    return redirect('financial_dashboard')
