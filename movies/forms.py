from django import forms


class ReviewForm(forms.Form):
    rating = forms.IntegerField(min_value=1, max_value=10)
    text = forms.CharField(widget=forms.Textarea, max_length=2000)
