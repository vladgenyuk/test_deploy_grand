from django.contrib.auth.decorators import login_required
from django.urls import path
from . import views
from django.contrib.auth import views as auth_views
from django.views.decorators.cache import cache_page


urlpatterns = [
    path('', views.Home.as_view(), name='home'),
    path('admin/', views.admin, name='admin'),
    path('category/<int:Category_id>/', views.ShowCategory.as_view(), name='category'),
    path('product/<int:pk>/', cache_page(60)(views.ShowProduct.as_view()), name='product'),
    path('create/', login_required(views.create.as_view()), name='create'),
    path('delete/<int:pk>', login_required(views.ArticleDeleteView.as_view()), name='delete'),
    path('register/', views.RegisterUser.as_view(), name='register'),
    path('logout/', views.logout_user, name='logout'),
    path('login/', views.LoginUser.as_view(), name='login'),
    path('area/', views.PersonalArea.as_view(), name='area'),
    path('updateProduct/<int:pk>/', views.UpdateProduct.as_view(), name='update'),
    path('updateProfile/<int:pk>/', views.UpdateProfile.as_view(), name='update_profile'),

    path('reset_password',
         views.ResetPass.as_view(template_name='svoy01/reset_password.html'),
         name='reset_password'),
    path('reset_password_sent',
         auth_views.PasswordResetDoneView.as_view(template_name='svoy01/reset_password_sent.html'),
         name='password_reset_done'),
    path('reset/<uidb64>/<token>',
         auth_views.PasswordResetConfirmView.as_view(template_name='svoy01/reset.html'),
         name='password_reset_confirm'),
    path('reset_password_complete',
         auth_views.PasswordResetCompleteView.as_view(template_name='svoy01/reset_password_complete.html'),
         name='password_reset_complete'),

    path('chats/', views.Chats.as_view(), name='chats'),
    path('chats/<int:receiver_id>', views.room, name='room'),
    path('all_users', views.all_users, name='all_users'),
    path('create_100', views.create_10, name='create_100'),
]

