import csv
from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.db import connection
from apps.users.decorators import role_required
from apps.users.models import CustomUser
from .models import PaymentSubmission, FinancialLedger, PaymentCategory

def align_finance_schema():
    """Ensure database column types for finance_paymentsubmission match UUID user keys."""
    try:
        with connection.cursor() as cursor:
            cursor.execute("""
                ALTER TABLE finance_paymentsubmission 
                ALTER COLUMN user_id TYPE uuid USING user_id::text::uuid;
            """)
    except Exception:
        pass

@login_required
def submit_payment_view(request):
    align_finance_schema()

    if request.method == 'POST':
        amount = request.POST.get('amount')
        category_id = request.POST.get('category')
        ref = request.POST.get('transaction_reference', '')
        proof = request.FILES.get('proof_of_payment')

        if amount and proof:
            cat_obj = None
            if category_id:
                try:
                    cat_obj = PaymentCategory.objects.get(id=category_id)
                except (PaymentCategory.DoesNotExist, ValueError):
                    cat_obj = None

            PaymentSubmission.objects.create(
                user=request.user,
                category=cat_obj,
                amount=amount,
                transaction_reference=ref,
                proof_of_payment=proof,
                status='PENDING'
            )

            messages.success(request, "Payment submission received and pending verification!")
            
            if request.user.role in [CustomUser.Role.FINANCIAL_SECRETARY, CustomUser.Role.CHAIRMAN]:
                return redirect('financial_dashboard')
            return redirect('member_dashboard')
        else:
            messages.error(request, "Please fill in all required fields and attach proof of payment.")

    categories = PaymentCategory.objects.all()
    return render(request, 'finance/submit_payment.html', {'categories': categories})


@login_required
@role_required(CustomUser.Role.FINANCIAL_SECRETARY, CustomUser.Role.CHAIRMAN)
def financial_dashboard_view(request):
    pending_payments = PaymentSubmission.objects.filter(status__iexact='PENDING').select_related('user', 'category').order_by('-created_at')
    verified_payments = PaymentSubmission.objects.filter(status__iexact='APPROVED').select_related('user', 'category').order_by('-created_at')
    ledger_entries = FinancialLedger.objects.all().select_related('posted_by').order_by('-created_at')
    
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
        user_id = request.user.id

        with connection.cursor() as cursor:
            # 1. Update status
            cursor.execute(
                "UPDATE finance_paymentsubmission SET status = %s WHERE id::text = %s",
                ['APPROVED', payment_id_str]
            )

            # 2. Insert into Financial Ledger with Detailed Description (Payer Name + Category)
            cursor.execute("""
                INSERT INTO finance_financialledger (id, payment_id, amount, transaction_type, description, posted_by_id, created_at)
                SELECT 
                    gen_random_uuid(), 
                    p.id, 
                    p.amount, 
                    'Credit', 
                    CONCAT(
                        'Payment from ', COALESCE(u.first_name || ' ' || u.last_name, u.email, 'Member'),
                        ' for ', COALESCE(c.name, 'General Contribution')
                    ), 
                    %s::uuid, 
                    NOW()
                FROM finance_paymentsubmission p
                LEFT JOIN users_customuser u ON p.user_id = u.id
                LEFT JOIN finance_paymentcategory c ON p.category_id = c.id
                WHERE p.id::text = %s
                ON CONFLICT DO NOTHING
            """, [str(user_id), payment_id_str])

        messages.success(request, "Payment verified and posted to ledger with detailed payer info!")
        return redirect('financial_dashboard')

    return redirect('financial_dashboard')


@login_required
@role_required(CustomUser.Role.FINANCIAL_SECRETARY, CustomUser.Role.CHAIRMAN)
def reject_payment_view(request, payment_id):
    if request.method == 'POST':
        payment_id_str = str(payment_id).strip()

        with connection.cursor() as cursor:
            cursor.execute(
                "UPDATE finance_paymentsubmission SET status = %s WHERE id::text = %s",
                ['REJECTED', payment_id_str]
            )

        messages.info(request, "Payment request rejected.")
        return redirect('financial_dashboard')

    return redirect('financial_dashboard')


@login_required
@role_required(CustomUser.Role.FINANCIAL_SECRETARY, CustomUser.Role.CHAIRMAN)
def export_ledger_csv_view(request):
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="financial_ledger.csv"'

    writer = csv.writer(response)
    writer.writerow(['ID', 'Payment ID', 'Amount', 'Type', 'Description', 'Created At'])

    for entry in FinancialLedger.objects.all().order_by('-created_at'):
        writer.writerow([entry.id, entry.payment_id, entry.amount, entry.transaction_type, entry.description, entry.created_at])

    return response


@login_required
@role_required(CustomUser.Role.FINANCIAL_SECRETARY, CustomUser.Role.CHAIRMAN)
def export_payments_csv_view(request):
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="payment_submissions.csv"'

    writer = csv.writer(response)
    writer.writerow(['ID', 'User', 'Amount', 'Status', 'Reference', 'Created At'])

    for sub in PaymentSubmission.objects.all().order_by('-created_at'):
        writer.writerow([sub.id, sub.user, sub.amount, sub.status, sub.transaction_reference, sub.created_at])

    return response

export_submissions_csv_view = export_payments_csv_view
