from django.db import models 
from django.contrib.auth.base_user import BaseUserManager, AbstractBaseUser
from django.contrib.auth.models import PermissionsMixin
from django.core.mail import send_mail
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from django.conf import settings
from django.dispatch import receiver


class  CustomUserManager(BaseUserManager):

    def create_user(self,first_name,last_name,date_of_birth, email, password, **extra_fields):
        if not email:
            raise ValueError(_("The Email Must Be Set"))
        
        email =self.normalize_email(email)
        user = self.model(
            email = email,
            first_name = first_name,
            last_name = last_name,
            date_of_birth = date_of_birth,
            **extra_fields
        )

        user.set_password(password)
        user.save()
        return user


    def create_superuser(self,first_name,last_name,date_of_birth,email,password, **extra_fields):
        extra_fields.setdefault("is_staff",True)
        extra_fields.setdefault("is_superuser",True)
        extra_fields.setdefault("is_active",True)

        if extra_fields.get("is_staff") is not True:
            raise ValueError(_("Superuser must have is_staff = True"))
        if extra_fields.get("is_superuser") is not True:
            raise ValueError(_("Superuser must have is_superuser = True"))
        
        return self.create_user(first_name,last_name,date_of_birth,email,password,**extra_fields)
    


class SocioUser(AbstractBaseUser, PermissionsMixin):
    first_name =models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    email =models.EmailField(unique =True)
    date_of_birth=models.DateField()
    picture =models.ImageField(blank =True, null =True)
    is_staff =models.BooleanField(default=False)
    is_active =models.BooleanField(default =True)
    date_joined = models.DateTimeField(default= timezone.now)
    last_login=models.DateTimeField(null =True)

    objects =CustomUserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS =['first_name','last_name','date_of_birth']

    def __str__(self):
        return f'{self.email} socioUser created'


class Profile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL,primary_key=True, related_name='profile', on_delete =models.CASCADE)
    name = models.CharField(max_length=50,blank = True, null =True)
    date_of_birth =models.DateField(blank=True,null =True)
    bio =models.TextField(max_length=255,null =True,blank =True)
    photo =models.ImageField(upload_to='users/%Y/%m/%d/', blank =True)
    location =models.CharField(max_length=100,blank =True, null =True)
    following =models.ManyToManyField(SocioUser,blank= True, related_name='followed_profiles')
    
    

    def __str__(self):
        return(f'Profile of {self.user.first_name} created')

class Post(models.Model):
    body = models.TextField()
    image =models.ImageField(upload_to='post/%Y/%m/%d/', blank =True)
    created = models.DateTimeField(default = timezone.now)
    author = models.ForeignKey(SocioUser,on_delete=models.CASCADE)
    likes = models.ManyToManyField(SocioUser,blank =True,related_name='likes')
    dislikes =models.ManyToManyField(SocioUser,blank = True, related_name='dislikes')




class Comment(models.Model):
    comment = models.TextField()
    image =models.ImageField(upload_to='comment/%Y/%m/%d/', blank =True)
    created_on =models.DateTimeField(default=timezone.now)
    post =models.ForeignKey(Post, on_delete=models.CASCADE)
    author =models.ForeignKey(SocioUser,on_delete=models.CASCADE)