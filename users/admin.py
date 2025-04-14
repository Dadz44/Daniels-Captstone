from django.contrib import admin
from .models import SocioUser,Profile,Post,Comment

@admin.register(SocioUser)
class SocioUserAdmin(admin.ModelAdmin):
    model = SocioUser
    list_display = ("id","email","first_name","last_name","date_of_birth","is_staff","is_active",)
    list_filter = ("email", "first_name", "last_name", "date_of_birth", "is_staff","is_active", )
    fieldsets = ((None, {"fields": ("first_name","last_name", "email", "password", "date_of_birth")}),
        ("Permissions", {"fields": ("is_staff",  "is_active",  "groups",  "user_permissions")}),)
    add_fieldsets = (( None, {"fields": ( "first_name","last_name", "email", "password1", "password2", "date_of_birth", "is_staff", "is_active", "groups", "user_permissions")}),)
    search_fields = ("email",)
    ordering = ("email",)


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display =['user','name','date_of_birth','bio','photo','location']
    list_filter =['user',]
    search_fields=['email']

@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display=['id','body','author','created']
    list_filter =['body','author','created']
    search_fields=['body']
    ordering =('created',)

@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display=['id','comment','author','created_on']
    list_filter =['comment','author','created_on']
    search_fields=['author','comment']
    ordering =('created_on',)
