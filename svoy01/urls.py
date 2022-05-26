from django.contrib.auth.decorators import login_required
from django.urls import path
from . import views
from django.contrib.auth import views as auth_views
from django.views.decorators.cache import cache_page


urlpatterns = [
    path('', (views.home.as_view()), name='home'),
    path('admin/', views.admin, name='admin'),
    path('Category/<int:Category_id>/', views.ShowCategory.as_view(), name='Category'),
    path('Product/<int:pk>/', cache_page(60)(views.ShowProduct.as_view()), name='product'),
    path('Create/', login_required(views.create.as_view()), name='create'),
    path('Delete/<int:pk>', login_required(views.ArticleDeleteView.as_view()), name='delete'),
    path('Register/', views.RegisterUser.as_view(), name='register'),
    path('Logout/', views.logout_user, name='logout'),
    path('Login/', views.LoginUser.as_view(), name='login'),
    path('Area/', views.PersonalArea.as_view(), name='area'),
    path('Update/<int:pk>/', views.UpdateProduct.as_view(), name='update'),

    path('reset_password',
         auth_views.PasswordResetView.as_view(template_name='svoy01/reset_password.html'),
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

    path('Chats/', views.chats.as_view(), name='chats'),
    path('Chats/<str:room_name>/', views.room, name='room'),
    path('allusers', views.allusers, name='allusers'),
    path('api/AllProducts/', views.AllProducts.as_view(), name='AllProducts'),
    path('api/AllProducts/<int:pk>/', views.DetailProduct.as_view(), name='DetailProduct'),
    path('api/postimages/<int:pk>/', views.PostImagesView.as_view(), name='PostImages')
]
