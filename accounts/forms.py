from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import User

class CustomerRegistrationForm(UserCreationForm):
    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2', 'phone', 'birthday', 'gender']
        labels = {
            'username':'',
            'email':'',
            'password1': '',
            'password2': '',
            'phone': '',
            'birthday': 'تاریخ تولد',
            'gender':'جنسیت',
        }
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control', 'placeholder':'نام کاربری'}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'ایمیل', 'style': 'text-align: right; direction: rtl;'}),
            'password1': forms.PasswordInput(attrs={'class': 'form-control w-100'}),
            'password2': forms.PasswordInput(attrs={'class': 'form-control w-100'}),

            'phone': forms.TextInput(attrs={'class': 'form-control', 'placeholder':'شماره تماس'}),
            'birthday': forms.DateInput(attrs={'type': 'date', 'class': 'form-control', 'placeholder':'تاریخ تولد'}),
            'gender': forms.Select(attrs={'class': 'form-control', 'placeholder':'جنسیت'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['username'].help_text = ''
        self.fields['password1'].help_text = ''
        self.fields['password2'].help_text = ''

        self.fields['password1'].widget.attrs.update({
        'class': 'form-control',
        'placeholder': 'رمز عبور'
    })
        self.fields['password2'].widget.attrs.update({
        'class': 'form-control',
        'placeholder': 'تکرار رمز عبور'
    })


from django import forms
from django.contrib.auth.forms import PasswordChangeForm
from .models import User

class AccountUpdateForm(forms.ModelForm):
    username = forms.CharField(
        max_length=150,
        required=True,
        widget=forms.TextInput(attrs={'class': 'form-control'}),
        label='نام کاربری'
    )
    first_name = forms.CharField(
        max_length=30,
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control'}),
        label='نام'
    )
    last_name = forms.CharField(
        max_length=30,
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control'}),
        label='نام خانوادگی'
    )
    password1 = forms.CharField(
        required=False,
        widget=forms.PasswordInput(attrs={'class': 'form-control'}),
        label='رمز عبور جدید'
    )
    password2 = forms.CharField(
        required=False,
        widget=forms.PasswordInput(attrs={'class': 'form-control'}),
        label='تکرار رمز عبور جدید'
    )

    class Meta:
        model = User
        fields = ['first_name', 'last_name','username',  'email', 'phone', 'birthday', 'gender']
        labels = {
            'email': 'ایمیل',
            'phone': 'شماره تماس',
            'birthday': 'تاریخ تولد',
            'gender': 'جنسیت',
        }
        widgets = {
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'phone': forms.TextInput(attrs={'class': 'form-control'}),
            'birthday': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'gender': forms.Select(attrs={'class': 'form-control'}),
        }

    def clean(self):
        cleaned_data = super().clean()
        password1 = cleaned_data.get('password1')
        password2 = cleaned_data.get('password2')

        if password1 or password2:
            if not password1:
                self.add_error('password1', 'لطفاً رمز عبور جدید را وارد کنید.')
            elif not password2:
                self.add_error('password2', 'لطفاً تکرار رمز عبور را وارد کنید.')
            elif password1 != password2:
                self.add_error('password2', 'رمزهای عبور مطابقت ندارند.')

        return cleaned_data
