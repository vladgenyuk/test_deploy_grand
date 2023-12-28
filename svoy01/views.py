import json

from django.contrib.auth import login, logout
from django.contrib.auth.views import LoginView, PasswordResetView
from django.db import transaction
from django.http import HttpResponseNotFound
from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from django.utils.safestring import mark_safe
from django.views.generic import CreateView, ListView, DetailView, DeleteView, UpdateView

from .forms import *
from .models import Category, PostImage, Profile, Messages, Chat
from .models import Product

PAGINATE = 4


def all_users(request):
    context = {
        'allusers': Profile.objects.all(),
        'Category': Category.objects.all()
    }
    return render(request, 'svoy01/allusers.html', context)


def admin(request):
    return render(request)


def room(request, receiver_id: int):
    user = User.objects.get(pk=receiver_id)
    chat = Chat.objects.filter(members__in=[request.user]).intersection(
        Chat.objects.filter(members__in=[user]))
    if not chat:
        chat = Chat.objects.create()
        chat.members.set([request.user, user])
    else:
        chat = chat[0]
    receiver_name = user.username
    context = {
        'Category': Category.objects.all(),
        'receiver_name': receiver_name,
        'chat_id': chat.id,
        'receiver_name_json': mark_safe(json.dumps(receiver_name)),
        'history': Messages.objects.filter(chat_id=chat.id),
    }
    return render(request, 'svoy01/room.html', context)


def logout_user(request):
    logout(request)
    return redirect('home')


def pageNotFound(request, exception):
    return HttpResponseNotFound('<h1>niet!!<h1>')


def create_10(request):
    for i in range(10):
        Product.objects.create(
        author_id=1,
        title=str(i),
        text=str(i),
        cat_id=6,
        cost=100
        )
    return redirect('home')


class Home(ListView):
    template_name = 'svoy01/main.html'
    paginate_by = PAGINATE
    allow_empty = True
    model = Product
    context_object_name = "Product"

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        context['Category'] = Category.objects.all()
        context['Category_id'] = 1
        context['count'] = Product.objects.count()
        return context

    def get_queryset(self):
        return Product.objects.all()


class Chats(ListView):
    template_name = 'svoy01/chatsroom.html'

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        context['Category'] = Category.objects.all()
        context['Chats'] = Chat.objects.prefetch_related('members').all()
        return context

    def get_queryset(self):
        pass


class ShowProduct(DetailView):
    model = Product
    template_name = "svoy01/Product.html"
    slug_url_kwarg = 'product_slug'
    context_object_name = "Product"

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = context['Product']
        context['Category'] = Category.objects.all()
        context['photos'] = PostImage.objects.filter(post_id=self.object.id)
        return context


class ShowCategory(ListView):
    paginate_by = PAGINATE
    model = Product
    template_name = "svoy01/category.html"
    context_object_name = "Product"
    allow_empty = True

    def get_queryset(self):
        global query
        query = self.request.GET.get('q')
        if not query:
            query = ""
        if self.kwargs['Category_id'] == 1:
            object_list = Product.objects.filter(title__icontains=query)
        else:
            object_list = Product.objects.filter(title__icontains=query, cat_id=self.kwargs['Category_id'])
        return object_list

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = context['Product']
        context["Category_id"] = self.kwargs['Category_id']
        context['Category'] = Category.objects.all()
        context['count'] = Product.objects.filter(cat_id=self.kwargs['Category_id'], title__icontains=query).count()
        return context


class create(CreateView):
    model = Product
    form_class = AddPostForm
    context_object_name = "Product"
    template_name = 'svoy01/create.html'
    success_url = reverse_lazy('Home')

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super(create, self).get_context_data(**kwargs)
        context['Category'] = Category.objects.all()
        if self.request.POST:
            context['form_images'] = ItemImageFormSet(self.request.POST, self.request.FILES)
        else:
            context['form_images'] = ItemImageFormSet()
        return context

    def form_valid(self, form):
        context = self.get_context_data()
        form_img = context['form_images']
        with transaction.atomic():
            form.instance.author = self.request.user
            self.object = form.save()
            if form_img.is_valid():
                form_img.instance = self.object
                form_img.save()
        return super(create, self).form_valid(form)


class ArticleDeleteView(DeleteView):
    success_url = reverse_lazy('Home')
    template_name = 'svoy01/delete.html'
    context_object_name = "Product"
    model = Product

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        context['Category'] = Category.objects.all()
        return context

    def get_queryset(self):
        return Product.objects.filter(author=self.request.user.id)


class RegisterUser(CreateView):
    form_class = RegisterUserForm
    template_name = 'svoy01/register.html'
    success_url = reverse_lazy('login')

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        context['Category'] = Category.objects.all()
        return context

    def form_valid(self, form):
        user = form.save()
        login(self.request, user)
        return redirect('home')


class LoginUser(LoginView):
    form_class = LoginUserForm
    template_name = 'svoy01/login.html'
    success_url = reverse_lazy('home')

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        context['Category'] = Category.objects.all()
        return context


class UpdateProduct(UpdateView):
    template_name = 'svoy01/UpdateProduct.html'
    context_object_name = 'Product'
    model = Product
    form_class = AddPostForm

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        context['Category'] = Category.objects.all()
        context['photos'] = PostImage.objects.filter(post_id=self.object.id)
        context['form_images'] = ItemImageFormSet()
        if self.request.POST:
            context['form_images'] = ItemImageFormSet(self.request.POST, self.request.FILES, instance=self.object)
        else:
            context['form_images'] = ItemImageFormSet(instance=self.object)
        return context

    def form_valid(self, form):
        context = self.get_context_data()
        form_img = context['form_images']
        with transaction.atomic():
            form.instance.user = self.request.user
            krakazyabra = form.save()
            if form_img.is_valid():
                form_img.instance = krakazyabra
                form_img.save()
        return super(UpdateProduct, self).form_valid(form)


class PersonalArea(ListView):
    template_name = 'svoy01/area.html'
    model = Product
    context_object_name = "Product"

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super(PersonalArea, self).get_context_data()
        context['Category'] = Category.objects.all()
        context['profile_id'] = self.request.user.id
        context['count'] = Product.objects.filter(author=self.request.user.id).count()
        return context

    def get_queryset(self):
        query = Product.objects.filter(author=self.request.user.id)
        return query


class UpdateProfile(UpdateView):
    template_name = 'svoy01/UpdateProfile.html'
    context_object_name = 'Profile'
    model = Profile
    form_class = ProfileForm
    success_url = reverse_lazy('home')

    def get_context_data(self, **kwargs):
        context = super(UpdateProfile, self).get_context_data()
        context['Category'] = Category.objects.all()
        context['Profile'] = self.request.user.id
        return context


class ResetPass(PasswordResetView, ListView):
    template_name = 'svoy01/area.html'
    model = Product
    context_object_name = "Product"

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super(ResetPass, self).get_context_data()
        context['Category'] = Category.objects.all()
        return context