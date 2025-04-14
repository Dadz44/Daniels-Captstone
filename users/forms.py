from django import forms
from django.contrib.auth.models import Group
from django.contrib.auth.forms import ReadOnlyPasswordHashField
from .models import SocioUser,Post,Comment,Profile

class SociosCreationForm(forms.ModelForm):
    password = forms.CharField(label = 'password',widget = forms.PasswordInput)
    password2 = forms.CharField(label = 'password2', widget=forms.PasswordInput)

    class Meta:
        model = SocioUser
        fields =['first_name','last_name','email','date_of_birth']

    def clean_password2(self):
        password =self.cleaned_data.get('password')
        password2=self.cleaned_data.get('password2')
        if password and password2 and password != password2:
            raise forms.ValidationError("Passwords don't match")
        return password2
    
    

class UserEditForm(forms.ModelForm):
    class Meta:
        model = SocioUser
        fields =['first_name','last_name','date_of_birth']



class LoginForm(forms.Form):
    email = forms.EmailField()
    password = forms.CharField(widget=forms.PasswordInput)

class PostForm(forms.ModelForm):
    body =forms.CharField(label ='',widget=forms.Textarea(attrs={'rows':5, 'placeholder':'Write Something'}))
    image =forms.ImageField(required=False)

    class Meta:
        model =Post
        fields =['body','image']

class CommentForm(forms.ModelForm):
    comment = forms.CharField(label = '', widget = forms.Textarea(attrs ={'rows':5, 'placeholder':'Write your Comment'}))
    image =forms.ImageField(required=False)

    class Meta:
        model = Comment
        fields =['comment','image']

class ProfileEditForm(forms.ModelForm):

    class Meta:
        model = Profile
        fields =['name','bio','location','date_of_birth','photo']

