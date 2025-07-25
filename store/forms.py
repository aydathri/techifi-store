from .models import User, Customer, Manager, Category, Product, Review
from django import forms
from django.contrib.auth.forms import UserCreationForm

class CustomerSignUpForm(UserCreationForm):
    email = forms.EmailField(required=True)
    phone = forms.CharField(max_length=11, required=True)

    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name', 'email', 'phone', 'password1', 'password2')


class CustomerLoginForm(forms.Form):
    identifier = forms.CharField(label = 'Username or Email',
                                 widget=forms.TextInput      #تعیین می‌کنه از چه نوع input استفاده کنه.
                                 (attrs={'placeholder': 'Username or Email',       # متن کم‌رنگی که داخل فیلد
                                         'class': 'form-control'}))       # کلاس CSS برای طراحی فرم

    password = forms.CharField(label = 'Password',
                               widget=forms.PasswordInput
                               (attrs={'placeholder': 'Password',
                                       'class': 'form-control'}))


class CustomerForgotPasswordForm(forms.Form):
    identifier = forms.CharField(label = 'Username or Email',
                                 widget=forms.TextInput
                                 (attrs={'placeholder': 'Username or Email',
                                         'class': 'form-control'}))


class CustomerResetPasswordForm(forms.Form):
    new_password = forms.CharField(label = 'New Password',
                                   widget=forms.PasswordInput
                                   (attrs={'placeholder': 'New password',
                                           'class:': 'form-control'}))

    confirm_password = forms.CharField(label = 'Confirm Password',
                                       widget=forms.PasswordInput
                                       (attrs={'placeholder': 'Confirm new password',
                                               'class:': 'form-control'}))


class CustomerProfileForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name', 'email', 'phone', 'address', 'avatar')


class CustomerReviewForm(forms.ModelForm):
    class Meta:
        model = Review
        fields = ('score', 'description')





class ManagerRegisterForm(UserCreationForm):
    email = forms.EmailField(required=True)
    phone = forms.CharField(max_length=11, required=True)

    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name', 'email', 'phone', 'password1', 'password2')


class ManagerLoginForm(forms.Form):
    identifier = forms.CharField(label = 'Username or Email',
                                 widget=forms.TextInput
                                 (attrs={'placeholder': 'Username or Email',
                                         'class': 'form-control'}))

    password = forms.CharField(label = 'Password',
                               widget=forms.PasswordInput
                               (attrs={'placeholder': 'Password',
                                       'class:': 'form-control'}))


class ManagerForgotPasswordForm(forms.Form):
    identifier = forms.CharField(label = 'Username or Email',
                                 widget = forms.TextInput
                                 (attrs = {'placeholder': 'Username or Email',
                                         'class': 'form-control'}))


class ManagerResetPasswordForm(forms.Form):
    new_password = forms.CharField(label = 'New Password',
                                   widget=forms.PasswordInput
                                   (attrs={'placeholder': 'New password',
                                           'class:': 'form-control'}))

    confirm_password = forms.CharField(label = 'Confirm Password',
                                       widget=forms.PasswordInput
                                       (attrs={'placeholder': 'Confirm new password',
                                               'class:': 'form-control'}))


class ManagerEditProfileForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name', 'email', 'phone','avatar')


class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ('title',)
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter the category name...'})
        }


class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = ('title', 'description', 'price', 'is_active', 'category', 'image')
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'product title'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'description'}),
            'price': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'price'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-control', 'placeholder': 'status'}),
            'category': forms.Select(attrs={'class': 'form-control', 'placeholder': 'category'}),
            'image': forms.FileInput(attrs={'class': 'form-control', 'accept': 'image/*'}),
        }
