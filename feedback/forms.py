from django import forms
from .models import Comment, Professor

class FeedbackForm(forms.ModelForm):
    professor = forms.ModelChoiceField(
        queryset=Professor.objects.all(),
        empty_label="Select a Professor",
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    student_name = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Optional - your name'
        })
    )
    comment_text = forms.CharField(
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'placeholder': 'Enter your feedback here...',
            'rows': 4
        })
    )

    class Meta:
        model = Comment
        fields = ['professor', 'student_name', 'comment_text']