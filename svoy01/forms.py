from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.forms import inlineformset_factory

from .models import Product, Profile, PostImage, Category


class AddPostForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):                 # конструктор для поля cat вместо ---- (категория не выбрана)
        super().__init__(*args, **kwargs)
        self.fields['cat'] = forms.ModelChoiceField(queryset=Category.objects.filter(level=1), label="Категория")
        self.fields['cat'].empty_label = "категория не выбрана"

    class Meta:
        model = Product
        fields = ['title', 'text', 'cost', 'cat', 'photo']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'Название'}),
            'text': forms.Textarea(attrs={'cols': 60, 'rows': 10, 'placeholder': 'Описание'}),
        }

    def clean_title(self):
        title = self.cleaned_data['title']
        if len(title) > 50:
            raise ValidationError("длина превышает 50 символов")

        return title


class RegisterUserForm(UserCreationForm):
    class Meta:
        model = User
        fields = ['email', 'username', 'password1', 'password2',]

    field_order = ['username', 'email', 'password1', 'password2']
    username = forms.CharField(label='Логин', widget=forms.TextInput(attrs={'class': 'test-input',
                                                                            'placeholder': 'Логин'}))
    email = forms.EmailField(label="email", widget=forms.EmailInput(attrs={'class': 'email-input',
                                                                           'placeholder': 'Email'}))
    password1 = forms.CharField(label='Пароль', widget=forms.PasswordInput(attrs={'class': 'form-input',
                                                                                 'placeholder': 'Пароль'}))
    password2 = forms.CharField(label='Пароль', widget=forms.PasswordInput(attrs={'class': 'form-input',
                                                                                 'placeholder': 'Повторите Пароль'}))
    # photo = forms.ImageField(label='Установить Фото')


class ProfileForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ('photo',)


class LoginUserForm(AuthenticationForm):
    email = forms.EmailField(label="email", widget=forms.EmailInput(attrs={'class': 'email-input',
                                                                           'placeholder': 'Email'}))
    password = forms.CharField(label='Пароль', widget=forms.PasswordInput(attrs={'class': 'form-input',
                                                                                 'placeholder': 'Пароль'}))

    def __init__(self, *args, **kwargs):
        super(LoginUserForm, self).__init__(*args, **kwargs)
        self.fields['email'].required = True
        self.fields.pop('username')

    def clean(self):
        user = User.objects.get(email=self.cleaned_data.get('email'))
        self.cleaned_data['username'] = user.username
        return super(LoginUserForm, self).clean()


class ItemImageForm(forms.ModelForm):
    class Meta:
        model = PostImage
        exclude = ()


ItemImageFormSet = inlineformset_factory(
    Product, PostImage, form=ItemImageForm,
    fields=["image"], extra=6, can_delete=False,
    max_num=5, # <- place where you can enter the nr of img
)


