import json
from django.conf import settings
from django.contrib.auth import login, logout
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.models import User
from django.contrib.auth.views import LoginView
from django.core.mail import send_mail
from django.core.paginator import Paginator
from django.db import transaction
from django.http import HttpResponseNotFound, HttpResponse, Http404
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse_lazy
from django.utils.safestring import mark_safe
from django.views import View
from django.views.generic import CreateView, TemplateView, ListView, DetailView, DeleteView, UpdateView
# from rest_framework.viewsets import ModelViewSet
from rest_framework.response import Response
from rest_framework.views import APIView

from .forms import *
from .models import Category, PostImage, Profile, Messages, Chat
from .models import product
# from .serializers import ProductSe
from .serializers import AllProductSerializer, DetailProductSerializer, PostImageSerializer

paginate = 4

# def home(request):
#     contact_list = product.objects.all()
#     paginator = Paginator(contact_list, 2)
#     page_number = request.GET.get('page')
#     page_obj = paginator.get_page(page_number)
#     context = {
#         "Category": Category.objects.all(),
#         "Category_id": 1,
#         'page_obj': page_obj,
#     }
#     return render(request, 'svoy01/main.html', context)


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
    paginate_by = paginate
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


def room(request, room_name):
    if room_name == str(request.user):
        return HttpResponse('Sam S Soboy')
    if not User.objects.filter(username=room_name):
        return HttpResponse('Net Usera')
    if not Chat.objects.filter(name=room_name, owner=request.user):
        Chat.objects.create(name=room_name, owner=request.user)
    context = {
        'room_name': room_name,
        'room_name_json': mark_safe(json.dumps(room_name)),
        'history': Messages.objects.filter(room_name=room_name,
                                           author=request.user,
                                           chat_id=Chat.objects.filter(name=room_name, owner=request.user).get().pk,)
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


# class ProductView(ModelViewSet):
#     queryset = product.objects.all()
#     serializer_class = ProductSerializer


# def post(request, Category_id):
#     context = {
#         "Category": Category.objects.all(),
#         'CAtegory': Category.objects.get(id=Category_id),
#         'product': product.objects.filter(cat_id=Category_id),
#     }
#     return render(request, 'svoy01/category.html', context)


# def Product(request, product_slug, ):
#     context = {
#         "Category": Category.objects.all(),
#         'Product': product.objects.get(slug=product_slug)
#     }
#     return render(request, 'svoy01/product.html', context)

class ShowProduct(DetailView):
    model = product
    template_name = "svoy01/product.html"
    slug_url_kwarg = 'product_slug'
    context_object_name = "Product"

    # def get_queryset(self):
    #     return photos.objects.filter(cat_id=self.kwargs['Category_id'])

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = context['Product']
        context['Category'] = Category.objects.all()
        context['photos'] = PostImage.objects.filter(post_id=self.object.id)
        return context


class ShowCategory(ListView):
    paginate_by = paginate
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
        object = product.objects.filter(author=self.request.user.id)
        return object


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
    template_name = 'svoy01/update.html'
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
        context['count'] = product.objects.filter(author=self.request.user.id).count()
        return context

    def get_queryset(self):
            query = product.objects.filter(author=self.request.user.id)
            return query


def logout_user(request):
    logout(request)
    return redirect('home')

# def blog_view(request):
#     posts = product.objects.all()
#     return render(request, 'svoy01/blog.html', {"posts": posts})
#
# def detail_view(request, id):
#     post = get_object_or_404(product, id=id)
#     photos = PostImage.objects.filter(post=post)
#     return render(request, 'svoy01/detail.html', {
#         "post": post, "photos": photos,
#     })


def pageNotFound(request, exception):
    return HttpResponseNotFound('<h1>niet!!<h1>')




#password qwedsacxz1
