from ast import For
from dataclasses import fields

from pyexpat import model
from django import forms
from .models import Account, UserProfile


class RegistrationForm(forms.ModelForm):
    password= forms.CharField(widget=forms.PasswordInput(attrs={'placeholder':'Enter Password'}))

    confirm_password= forms.CharField(widget=forms.PasswordInput(attrs={'placeholder':'Confirm Password' }))
    class Meta: 
        model = Account
        fields = ['first_name','last_name','phone','email','password' ]

        # looping class form-control to apply in all field at once
    def __init__(self, *args,**kwargs):
        super(RegistrationForm, self). __init__(*args,**kwargs)

        self.fields['first_name'].widget.attrs['placeholder']= 'Enter your First Name'
        self.fields['last_name'].widget.attrs['placeholder']= 'Enter your Last Name'
        self.fields['phone'].widget.attrs['placeholder']= 'Enter your Phone Number'
        self.fields['email'].widget.attrs['placeholder']= 'Enter your Email'
        for field in self.fields:
            self.fields[field].widget.attrs['class']= 'form-control'


            # crosscheck
    def clean(self):
        cleaned_data =  super(RegistrationForm, self).clean()
        password = cleaned_data.get('password')
        confirm_password = cleaned_data.get('confirm_password')

        if password != confirm_password:
            raise forms.ValidationError(
                "Password does not match !"
            )


class UserForm(forms.ModelForm):
    class Meta:
        model=Account
        fields = ('first_name','last_name','phone')

    def __init__(self, *args,**kwargs):
        super(UserForm, self). __init__(*args,**kwargs)

        for field in self.fields:
            self.fields[field].widget.attrs['class']= 'form-control'


class UserProfileForm(forms.ModelForm):
    profile_picture = forms.ImageField(required=False,error_messages={'invalid':{"Image Files Only"}},widget=forms.FileInput)
    class Meta:
        model = UserProfile
        fields = ('address1','address2','city','prov','profile_picture')

    def __init__(self, *args,**kwargs):
        super(UserProfileForm, self). __init__(*args,**kwargs)

        for field in self.fields:
            self.fields[field].widget.attrs['class']= 'form-control'