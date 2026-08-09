import uuid
from django.db import models
from django.conf import settings
from apps.membership.models import MemberProfile

class PaymentCategory(models.Model):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    default_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
    is_mandatory = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Payment Category'
        verbose_name_plural = 'Payment Categories'

    def __str__(self):
        return self.name

class PaymentSubmission(models.Model):
    class Status(models.TextChoices):
        PENDING = 'PENDING', 'Pending Verification'
        VERIFIED = 'VERIFIED', 'Verified / Approved'
        REJECTED = 'REJECTED', 'Rejected'

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    member = models.ForeignKey(MemberProfile, on_delete=models.PROTECT, related_name='payments')
    category = models.ForeignKey(PaymentCategory, on_delete=models.PROTECT)
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    payment_reference = models.CharField(max_length=100, unique=True)
    proof_of_payment = models.FileField(upload_to='proofs/%Y/%m/')
    
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.PENDING)
    rejection_reason = models.TextField(null=True, blank=True)
    submitted_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Payment Submission'
        verbose_name_plural = 'Payment Submissions'
        ordering = ['-submitted_at']

    def __str__(self):
        return f"{self.payment_reference} - {self.member} ({self.amount})"

class FinancialLedger(models.Model):
    class TransactionType(models.TextChoices):
        CREDIT = 'CREDIT', 'Credit (Income)'
        DEBIT = 'DEBIT', 'Debit (Expense)'

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    submission = models.OneToOneField(
        PaymentSubmission, 
        on_delete=models.PROTECT, 
        null=True, 
        blank=True, 
        related_name='ledger_entry'
    )
    transaction_type = models.CharField(max_length=10, choices=TransactionType.choices)
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    description = models.TextField()
    posted_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Financial Ledger Entry'
        verbose_name_plural = 'Financial Ledger Entries'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.transaction_type}: {self.amount} - {self.description[:30]}"
