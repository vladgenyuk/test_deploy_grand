import json

from django.contrib.auth import login, logout
from django.contrib.auth.views import LoginView, PasswordResetView
from django.db import transaction
from django.http import HttpResponseNotFound, HttpResponse, Http404
from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from django.utils.safestring import mark_safe
from django.views.generic import CreateView, ListView, DetailView, DeleteView, UpdateView
from rest_framework.response import Response
from rest_framework.views import APIView

from .forms import *
from .models import Category, PostImage, Profile, Messages, Chat
from .models import product
from .serializers import AllProductSerializer, DetailProductSerializer, PostImageSerializer

PAGINATE = 4


class AllProducts(APIView):

    def get(self, request, format=None):
        products = product.objects.all()
        serializer = AllProductSerializer(products, many=True)
        return Response(serializer.data)


class DetailProduct(APIView):

    def get_object(self, pk):
        try:
            return product.objects.get(pk=pk)
        except product.DoesNotExist:
            raise Http404

    def get(self, request, pk, format=None):
        product = self.get_object(pk)
        postimages = PostImage.objects.filter(post=pk)
        serializer = DetailProductSerializer(product)
        return Response(serializer.data)


class PostImagesView(APIView):
    def get(self, request, pk, format=None):
        postimages = PostImage.objects.filter(post=pk)
        serializer = PostImageSerializer(postimages, many=True)
        return Response(serializer.data)


def allusers(request):
    context = {
        'allusers': Profile.objects.all(),
    }
    return render(request, 'svoy01/allusers.html', context)


class home(ListView):
    template_name = 'svoy01/main.html'
    paginate_by = PAGINATE
    allow_empty = True
    model = product
    context_object_name = "product"

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        context['Category'] = Category.objects.all()
        context['Category_id'] = 1
        context['count'] = product.objects.count()
        return context

    def get_queryset(self):
        return product.objects.all()


def admin(request):
    return render(request)


def get_receiver(name: str, username: str):
    name = name.split("|")
    if name[0] == username:
        return name[1]
    return name[0]


def room(request, room_name):
    room_name = get_receiver(room_name, request.user.username)
    if not Chat.objects.filter(name__icontains=room_name):
        Chat.objects.create(name=room_name + "|" + request.user.username)
    context = {
        'Category': Category.objects.all(),
        'room_name': room_name,
        'room_name_json': mark_safe(json.dumps(room_name)),
        'history': Messages.objects.filter(chat_id__icontains=room_name),
        'room_user': User.objects.get(username=room_name)
    }
    return render(request, 'svoy01/room.html', context)


class chats(ListView):
    template_name = 'svoy01/chatsroom.html'

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        context['Category'] = Category.objects.all()
        context['chats'] = Chat.objects.all()
        return context

    def get_queryset(self):
        pass


class ShowProduct(DetailView):
    model = product
    template_name = "svoy01/product.html"
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
    model = product
    template_name = "svoy01/category.html"
    context_object_name = "product"
    allow_empty = True

    def get_queryset(self):
        global query
        query = self.request.GET.get('q')
        if not query:
            query = ""
        if self.kwargs['Category_id'] == 1:
            object_list = product.objects.filter(title__icontains=query)
        else:
            object_list = product.objects.filter(title__icontains=query, cat_id=self.kwargs['Category_id'])
        return object_list

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = context['product']
        context["Category_id"] = self.kwargs['Category_id']
        context['Category'] = Category.objects.all()
        context['count'] = product.objects.filter(cat_id=self.kwargs['Category_id'], title__icontains=query).count()
        return context


class create(CreateView):
    model = product
    form_class = AddPostForm
    context_object_name = "product"
    template_name = 'svoy01/create.html'
    success_url = reverse_lazy('home')

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
    success_url = reverse_lazy('home')
    template_name = 'svoy01/delete.html'
    context_object_name = "Product"
    model = product

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        context['Category'] = Category.objects.all()
        return context

    def get_queryset(self):
        return product.objects.filter(author=self.request.user.id)


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
    model = product
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
    model = product
    context_object_name = "Product"

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super(PersonalArea, self).get_context_data()
        context['Category'] = Category.objects.all()
        context['profile_id'] = self.request.user.id
        context['count'] = product.objects.filter(author=self.request.user.id).count()
        return context

    def get_queryset(self):
        query = product.objects.filter(author=self.request.user.id)
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


def logout_user(request):
    logout(request)
    return redirect('home')


def pageNotFound(request, exception):
    return HttpResponseNotFound('<h1>niet!!<h1>')


def create_100(request):
    for i in range(100):
        product.objects.create(
        title=str(i),
        text=str(i),
        cat=Category.objects.get(id=5),
        cost=100
        )
    return render(request, 'svoy01/create_100.html')


class Reset_Pass(PasswordResetView, ListView):
    template_name = 'svoy01/area.html'
    model = product
    context_object_name = "Product"

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super(Reset_Pass, self).get_context_data()
        context['Category'] = Category.objects.all()
        return context





#password qwedsacxz1
