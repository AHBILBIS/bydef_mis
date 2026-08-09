from django import forms
from .models import PaymentSubmission, PaymentCategory

class PaymentSubmissionForm(forms.ModelForm):
    category = forms.ModelChoiceField(
        queryset=PaymentCategory.objects.all(),
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    amount = forms.DecimalField(
        widget=forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Amount (e.g. 5000.00)'})
    )
    payment_reference = forms.CharField(
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Transaction Reference / Teller No.'})
    )
    proof_of_payment = forms.FileField(
        widget=forms.FileInput(attrs={'class': 'form-control'})
    )

    class Meta:
        model = PaymentSubmission
        fields = ['category', 'amount', 'payment_reference', 'proof_of_payment']
