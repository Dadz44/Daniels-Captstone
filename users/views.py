from django.shortcuts import render, get_object_or_404,redirect
from django.http import JsonResponse
from django.contrib.auth.mixins import UserPassesTestMixin,LoginRequiredMixin
from .forms import SociosCreationForm,LoginForm,PostForm,CommentForm,ProfileEditForm,UserEditForm
import json
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth import authenticate,login as auth_login,logout
from .models import Profile,SocioUser,Post,Comment


@csrf_exempt
def signup(request):
    if request.method == "POST":
        
        
        user_form = SociosCreationForm(request.POST)

        if user_form.is_valid():
            new_user = user_form.save(commit=False)
            new_user.set_password(user_form.cleaned_data['password'])
            new_user.save()

            #creates user
            reg_data ={
                'first_name':new_user.first_name,
                'last_name':new_user.last_name,
                'email':new_user.email,
                'date_of_birth':new_user.date_of_birth
            }

            profile_data ={
                
                'user': new_user,   
                'bio': request.POST.get('bio'),
                'date_of_birth':new_user.date_of_birth,
                'location':request.POST.get('location'),
                'photo':request.FILES.get('photo')
            }

            profiles = Profile.objects.create(**profile_data)

            user_profile_data ={
              'date_of_birth': new_user.date_of_birth,
              'bio': profiles.bio,
              'photo': str(profiles.photo.url) if profiles.photo else None,
              'location':profiles.location
            }


            return JsonResponse({'signup_message':f'user {new_user.first_name} {new_user.last_name} signed up successfully', 'Profile message':f'{user_profile_data} created'}, status =200)
        else:
            return JsonResponse({"error":user_form.errors})
    else:
        return JsonResponse({'message':'Only Post Method Accepted'})
    

@csrf_exempt
def user_login(request):
    if request.method == 'POST':
    
        
        form = LoginForm(request.POST)
        if form.is_valid():
            cd = form.cleaned_data
            user =authenticate(request, email =cd['email'], password =cd['password'])
            if user is not None:
                if user.is_active:
                    auth_login(request, user)
                    return JsonResponse({'message':'Authenticated Successfully'},status =200)
                
                else: 
                    return JsonResponse({'message':'Disabled Account'},status =403)
            else:   
                return JsonResponse({'message':'Invalid Login'},status =401)
        else:
            return JsonResponse({'error':form.errors})
        
    return JsonResponse({'message':'Log-in successfull'})

def login_required_json(view_func):
    def wrapper(request, *args, **kwargs):
        if request.user.is_authenticated:
            return view_func(request, *args, **kwargs)
        else:
            return JsonResponse({'error': 'Authentication required'}, status=401)
    return wrapper

@csrf_exempt
@login_required_json
def user_logout(request):
    if request.method =='POST':
        if request.user.is_authenticated:
            logout(request)
            return JsonResponse({'message':'Logged Out Successfully'})
        else:
            return JsonResponse({'message':'User Not Authenticated'})
    else:
        return JsonResponse({'message':'Only Post Request Allowed'})
    
@csrf_exempt
@login_required_json
def create_post(request):
    if request.method == "POST":
        
        form=PostForm(request.POST,request.FILES)
        if form.is_valid():
            post = form.save(commit =False)
            post.author =request.user
            post.save()
            post_data ={
                'id':post.id,
                'body':post.body,
                'image':request.build_absolute_uri(post.image.url) if post.image else None,
                'author':request.user.email,
                'created':post.created.strftime('%Y-%m-%d %H:%M:%S')
            }
        
            return JsonResponse ({'message': 'Post created sucessfully','Post':post_data}, status =200)
        else:
            return JsonResponse({'error':form.errors})
    return JsonResponse({'error': 'Invalid Request Method'}, status =400)

@csrf_exempt
@login_required_json
def update_post(request,post_id):
    if request.method == "POST":
        try:
            post = Post.objects.get(id=post_id,author=request.user)
        except Post.DoesNotExist:
            return JsonResponse({'message':'Post does not exist'})

        form = PostForm(request.POST,request.FILES, instance=post)
        
        if form.is_valid():
            post_update =form.save()

            post_data ={
                    'id':post_update.id,
                    'body':post_update.body,
                    'image':request.build_absolute_uri(post.image.url) if post.image else None,
                    'author':request.user.email,
                    'created':post_update.created.strftime('%Y-%m-%d %H:%M:%S')
                }

            return JsonResponse({'message':'update successful',
                             'post':post_data})
        else:
            return JsonResponse({'errors':form.errors},status =400)
    else:
        return JsonResponse({'message':'Only POST method allowed'},status =405)
        


@csrf_exempt
@login_required_json
def delete_post(request,post_id):
    if request.method == "DELETE":
        try:
            post =Post.objects.get(id = post_id, author =request.user)
            post_data ={
                'id':post.id,
                'body':post.body,
                'image':request.build_absolute_uri(post.image.url) if post.image else None,
                'author':request.user.email,
                'created':post.created
            }
            post.delete()
            return JsonResponse({'message':'Post Deleted Successfully', 'Deleted Message':post_data},status=200)
        except Post.DoesNotExist:
            return JsonResponse({'message':'Post Does not exist'},status =400)
    
    else:
        return JsonResponse({'message': "Only Delete Method accepted"}, status =405)
    
@csrf_exempt
@login_required_json
def create_comment(request,post_id):
    if request.method == "POST":
        post = get_object_or_404(Post,id =post_id)
        
        
        form=CommentForm(request.POST,request.FILES)
        if form.is_valid():
            comment = form.save(commit =False)
            comment.author =request.user
            comment.post = post
            comment.save()
            comment_data ={
                'id':comment.id,
                'comment':comment.comment,
                'image':request.build_absolute_uri(comment.image.url) if comment.image else None,
                'author':comment.author.email,
                'created_on':comment.created_on.strftime('%Y-%m-%d %H:%M:%S')
            }
        
            return JsonResponse ({'message': 'Comment created sucessfully','Comment':comment_data}, status =200)
        else:
            return JsonResponse({'error':form.errors})
    return JsonResponse({'error': 'Invalid Request Method'}, status =400)

@csrf_exempt
@login_required_json
def delete_comment(request,comment_id):
    if request.method != "DELETE":
        return JsonResponse({'message':'Only Delete Method Allowed'},status =405)
    else:

        comments = get_object_or_404(Comment, author =request.user, id =comment_id)
        
        
        comment_data={
            'id':comments.id,
            'comment':comments.comment,
            'image':request.build_absolute_uri(comments.image.url) if comments.image else None,
            'author':comments.author.email
        }
        
        comments.delete()

        return JsonResponse({'message':'Comment Deleted', 'Deleted Comment':comment_data},status =200)
    

    
@login_required_json
def post_view(request):
    
    user =request.user

    followed_users =user.profile.following.all()
    print(followed_users)
    relevant_users = [user]+list(followed_users)
    
    print('users',relevant_users)
    try:
        posts = Post.objects.filter(author__in=relevant_users).order_by('-created')
    except Post.DoesNotExist:
        return JsonResponse({'message':'No Post exists'},status =404)
    
    post_data=[]
    for post in posts:
        comments =post.comment_set.all()
        comment_form =CommentForm()

        post_data.append({
            'id': post.id,
            'body': post.body,
            'image':request.build_absolute_uri(post.image.url) if post.image else None,
            'author': post.author.email,
            'total_likes':post.likes.count(),
            'total_dislikes':post.dislikes.count(),
            'created': post.created.strftime('%Y-%m-%d %H:%M'),
            'comments': [{
                'id': comment.id,
                'comment': comment.comment,
                'image':request.build_absolute_uri(comment.image.url) if comment.image else None,
                'author': comment.author.email,
                'created_on': comment.created_on.strftime('%Y-%m-%d %H:%M')
            } for comment in comments],
            'comment_form_fields':{field.name: field.label for field in comment_form.visible_fields()}})
        
        
    liked_posts = Post.objects.filter(likes=user).order_by('-created')
    liked_post_data = [{
        'id': post.id,
        'body': post.body,
        'author': post.author.email,
        'created': post.created.strftime('%Y-%m-%d %H:%M')
    } for post in liked_posts]
    
    
    disliked_posts = Post.objects.filter(dislikes=user).order_by('-created')
    disliked_post_data = [{
        'id': post.id,
        'body': post.body,
        'author': post.author.email,
        'created': post.created.strftime('%Y-%m-%d %H:%M')
    } for post in disliked_posts]
        

    return JsonResponse({'posts': post_data, 
                         'likes':liked_post_data,
                        'dislikes':disliked_post_data}, status=200)

@login_required_json
def post_detail(request,post_id):
    post = get_object_or_404(Post, id=post_id)
    post_data = {
        'id':post_id,
        'body': post.body,
        'author':post.author.email,
        'total_likes':post.likes.count(),
        'total_dislikes':post.dislikes.count(),
        'created':post.created.strftime('%Y-%m-%d %H:%M')
    }
    comments = post.comment_set.all()

    comments_count = comments.count()

    comment_list =[]
    for comment in comments:
        comment_list.append({
            'id':comment.id,
            'comment':comment.comment,
            'author':comment.author.email,
            'image':request.build_absolute_uri(comments.image.url) if comments.image else None,
            'created_on':comment.created_on.strftime('%Y-%m-%d %H:%M'),
        })

    response_data ={
        'post':post_data,
        'comments':comment_list,
        'comments_count':comments_count,
    }
    return JsonResponse({'post':response_data},status =200)

@login_required_json
def profile_view(request,pk):
    profile = get_object_or_404(Profile,pk =pk)
    user = profile.user

    posts= Post.objects.filter(author = user).order_by('-created')
    comments = Comment.objects.filter(author = user).order_by('-created_on')

    followers =Profile.objects.filter(following=user)
    following =profile.following.all()

    is_following =request.user in followers if request.user.is_authenticated else False
    num_of_followers = len(followers)
    num_following = len(following)

    liked_posts = Post.objects.filter(likes =user).order_by('-created')

    follower_profiles = Profile.objects.filter(following = user)

    following_profiles =Profile.objects.filter(user__in=following)
    
    follower_list =[{
        'id':follow.user.id,
        'name':follow.name,
        'email':follow.user.email,
        'photo':request.build_absolute_uri(follow.photo.url) if follow.photo else None
    } for follow in follower_profiles]

    following_list =[{
        'id':follow.user.id,
        'name':follow.name,
        'email':follow.user.email,
        'photo':request.build_absolute_uri(follow.photo.url) if follow.photo else None
    }for follow in following_profiles]

    post_data =[{
            'id':post.id,
            'body':post.body,
            'author':post.author.email,
            'total_likes':post.likes.count(),
            'total_dislikes':post.dislikes.count(),
            'created':post.created.strftime('%Y-%m-%d %H:%M')
        }for post in posts]

    liked_post_data =[{
        'id':post.id,
        'body':post.body,
        'author':post.author.email,
        'created': post.created.strftime('%Y-%m-%d %H:%M')
    } for post in liked_posts]

    comment_list=[{
        'id':comment.id,
        'comment':comment.comment,
        'author':comment.author.email,
        'created_on':comment.created_on.strftime('%Y-%m-%d %H:%M'),
        'post':{
            'id':comment.post.id,
            'body':comment.post.body,
            'author':comment.post.author.email,
            'created':comment.post.created.strftime('%Y-%m-%d %H:%M')
        } }for comment in comments]
    

    return JsonResponse ({'Profile':{'name':profile.name,
                                     'is_following':is_following,
                                     'number_of_followers':num_of_followers,
                                     'number_following':num_following,
                                     'date_of_birth':profile.date_of_birth.strftime('%d %B %Y'),
                                     'bio':profile.bio, 
                                     'location':profile.location,
                                     'user':profile.user.email},
                                'posts':post_data,
                                'comments':comment_list,
                                'liked_post':liked_post_data,
                                'following':following_list,
                                'followers':follower_list})

@csrf_exempt
@login_required_json
def AddFollower(request,pk):
    if request.method != "POST":
        return JsonResponse({'messages':'Invalid Method'},status =405)

    else:
        user_to_follow = get_object_or_404(Profile,pk=pk)
        current_profile = request.user.profile

        if user_to_follow == current_profile:
            return JsonResponse({'message':f'You Cannot Follow Youself'},status =400)

        elif user_to_follow in current_profile.following.all():
            return JsonResponse({'message':'You are already following this user'},status =400)
        
        else:
            current_profile.following.add(user_to_follow.user)

            return JsonResponse({'message':f'You are now following {user_to_follow.user.email}'},status =200)
        
        
@csrf_exempt
@login_required_json   
def removefollower(request,pk):
    if request.method != "POST":
        return JsonResponse({'messages':'Only Post Method Allowed'},status =405)
    
    else:
        user_to_unfollow = get_object_or_404(Profile,pk = pk)
        current_profile = request.user.profile

        if user_to_unfollow == current_profile:
            return JsonResponse({'message':'You cannot unfollow yourself'}, status=400 )
        
        elif user_to_unfollow.user not in current_profile.following.all():
            return JsonResponse({'message': 'You are not following the account'},status =405)

        else:
            current_profile.following.remove(user_to_unfollow.user)
            return JsonResponse({'message':f'You have unfollowed {user_to_unfollow.user.email}'}, status =200)

@csrf_exempt
@login_required_json       
def update_profile(request):
    if request.method == "POST":
        try:    
            profile = Profile.objects.get(user=request.user)
        except Profile.DoesNotExist:
            return JsonResponse({'message':'Profile Does Not Exist'},status =404)
    
        
        form = ProfileEditForm(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            updated_profile = form.save()

            profile_data ={
                'name':updated_profile.name,
                'bio':updated_profile.bio,
                'location':updated_profile.location,
                'photo':request.build_absolute_uri(updated_profile.photo.url) if updated_profile.photo else None
            }
            print(request.POST)
            print(request.FILES)
            return JsonResponse({'message':'update successful','profile':profile_data},status =200)
        else:
            return JsonResponse({'message':form.errors})
    else:
        return JsonResponse({'message':'Only Post Method Allowed'})
    

@csrf_exempt  
@login_required_json      
def update_user(request):
    if request.method == "POST":
            
        user = request.user
        
        form = UserEditForm(request.POST,request.FILES, instance=user)
        if form.is_valid():
            users = form.save(commit=False)
            users.save()

            users_data ={
                'first_name':users.first_name,
                'last_name':users.last_name,
                'date_of_birth':users.date_of_birth,
            }
            return JsonResponse({'message':'update successful','profile':users_data},status =200)
        else:
            return JsonResponse({'message':form.errors})
    else:
        return JsonResponse({'message':'Only POST method allowed'})
    
@csrf_exempt
@login_required_json
def add_likes(request,post_id):
    if request.method != "POST":
        return JsonResponse({'messages':'Invalid Method'},status =405)

    else:
        try:
            post = get_object_or_404(Post,pk=post_id)
        except Post.DoesNotExist:
            return JsonResponse({'message':'Post not found'})
        
        user=request.user
        

        if user in post.dislikes.all():
            post.dislikes.remove(user)
            liked = False

        else:
            post.likes.add(user)
            liked =True
            return JsonResponse({'message':'Liked toggled successfully',
                                 'like':liked, 
                                 'total_likes':post.likes.count(),
                                 'total_dislikes':post.dislikes.count()},status =200 )
        
        
@csrf_exempt
@login_required_json
def disliked(request,post_id):
    if request.method != "POST":
        return JsonResponse({'messages':'Invalid Method'},status =405)

    else:
        try:
            post = get_object_or_404(Post,pk=post_id)
        except Post.DoesNotExist:
            return JsonResponse({'message':'Post not found'})
        
        user=request.user
        

        if user in post.likes.all():
            post.likes.remove(user)
        
        if user in post.dislikes.all():
            post.dislikes.remove(user)
            disliked = False
    
        else:
            post.dislikes.add(user)
            disliked =True

            return JsonResponse({'message':'Liked toggled successfully',
                                 'disliked':disliked, 
                                 'total_likes':post.likes.count(),
                                 'total_dislikes':post.dislikes.count()
                                 },status =200 )

@login_required_json   
def follower_list(request):
    user =request.user
    profile = get_object_or_404(Profile,user=request.user)
    following =profile.following.all()
    
    
    following_data =[{
        'total_following':following.count(),
        'id':user.id,
        'email':user.email,    
    }for user in following]


    return JsonResponse({'following':following_data},status =200)

def search(request):
    query = request.GET.get('q','')
    post_results = Post.objects.filter(body__icontains =query)
    comment_results =Comment.objects.filter(comment__icontains= query)
    user_result = SocioUser.objects.filter(email__icontains = query)

    post_data =[{
        'id':post.id,
        'body':post.body,
        'author':post.author.email,
        'created':post.created.strftime('%Y-%m-%d %H:%M:%S')
    } for post in post_results]

    comment_data =[{
        'id':comment.id,
        'comment':comment.comment,
        'author':comment.author.email,
        'created_on':comment.created_on.strftime('%Y-%m-%d %H:%M:%S')
    } for comment in comment_results]

    user_data =[{
        'id':users.id,
        'email':users.email     
    } for users in user_result]


    return JsonResponse({'post':post_data, 'comments':comment_data, 'user':user_data})

        

        


        

