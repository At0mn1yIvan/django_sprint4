from django import forms
from django.contrib.auth import get_user_model
from .models import Post, Comment


User = get_user_model()


class PostForm(forms.ModelForm):
    """Форма для создания и редактирования поста."""

    class Meta:
        model = Post
        exclude = [
            'author',
            'is_published',
        ]


class CommentForm(forms.ModelForm):
    """Форма для добавления комментария."""

    class Meta:
        model = Comment
        fields = (
            'text',
        )


class ProfileEditForm(forms.ModelForm):
    """Форма для редактирования профиля пользователя."""

    class Meta:
        model = User
        fields = (
            'first_name',
            'last_name',
            'email',
            'username',
        )
