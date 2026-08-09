from django.db import models

class PaymentCategory(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)

    class Meta:
        verbose_name_plural = "Payment Categories"

    def __str__(self):
        return self.name

class PaymentReceipt(models.Model):
    category = models.ForeignKey(PaymentCategory, on_delete=models.SET_NULL, null=True)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    transaction_reference = models.CharField(max_length=100)
    proof_of_payment = models.FileField(upload_to='receipts/')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.category} - {self.amount}"
