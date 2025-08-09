from django import forms
from .models import Comment, Post

class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ['body']
        labels = {
            'body': 'متن'
        }
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




class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ['title', 'content', 'published_at', 'is_published', 'image']
        widgets = {
            'published_at': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
        }
        labels = {
            'title': 'عنوان',
            'content': 'محتوا',
            'author': 'نویسنده',
            'published_at': 'تاریخ انتشار',
            'is_published': 'منتشر شود؟',
            'image': 'تصویر',
        }
