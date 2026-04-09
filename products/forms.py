from django import forms
from .models import Review

class ReviewForm(forms.ModelForm):
    rating = forms.ChoiceField(
        choices=[(i, i) for i in range(1, 6)],
        widget=forms.RadioSelect(attrs={'class': 'hidden peer'}),
    )

    class Meta:
        model = Review
        fields = ('rating', 'review')
        widgets = {
            'review': forms.Textarea(attrs={
                'rows': 3,
                'placeholder': 'Share your experience with this product...',
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-purple-500',
            }),
        }
