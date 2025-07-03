from django import forms
from .models import PolicyNode

class PolicyNodeForm(forms.ModelForm):
    class Meta:
        model = PolicyNode
        fields = '__all__'
