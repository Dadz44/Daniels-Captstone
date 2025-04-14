from . import views
from django.urls import path

urlpatterns =[
    path('signup/',views.signup, name ='signup'),
    path('login/', views.user_login, name ='login'),
    path('logout/', views.user_logout, name ='logout'),
    path('profile/<int:pk>',views.profile_view, name ='profile'),
    path('profile_edit/',views.update_profile,name ='user_profile'),
    path('user_edit/',views.update_user, name ='user_edit'),
    path('create/',views.create_post,name='create'),
    path('update/<int:post_id>',views.update_post, name='update'),
    path('delete/<int:post_id>',views.delete_post, name ='delete'),
    path('comment/<int:post_id>',views.create_comment, name ='comment'),
    path('comment_del/<int:comment_id>', views.delete_comment, name = 'delete_comment'),
    path('posts/',views.post_view, name ='posts'),
    path('post_detail/<int:post_id>',views.post_detail, name ='post_detail'),
    path('follow/<int:pk>',views.AddFollower, name ='post_detail'),
    path('unfollow/<int:pk>',views.removefollower, name ='unfollow'),
    path('likes/<int:post_id>',views.add_likes, name ='likes'),
    path('dislikes/<int:post_id>',views.disliked, name ='dislikes'),
    path('followers/',views.follower_list,name ='followers'),
    path('search/',views.search, name ='search')
]