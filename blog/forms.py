from django import forms
from .models import Comment

class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ['body']
        widgets = {
            'body': forms.Textarea(attrs={
                'class': 'form-control',
                'placeholder': 'نظر خود را بنویسید...',
                'rows': 4,
                'maxlength': 1000
            })
        }

    def clean_body(self):
        body = self.cleaned_data['body']
        body = body.strip()
        if len(body) < 5:
            raise forms.ValidationError('متن کامنت باید حداقل ۵ کاراکتر باشد.')
        return body