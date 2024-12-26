from django.contrib.auth.decorators import login_required
from django.db.models import Count
from django.http import Http404
from django.shortcuts import get_object_or_404, redirect, render
from django.contrib.auth import get_user_model
from django.urls import reverse
from django.utils import timezone
from django.views.generic import ListView

from .forms import CommentForm, PostForm, ProfileEditForm
from .models import Category, Post, Comment

User = get_user_model()

PAGE_PAGINATOR = 10


class HomePage(ListView):
    """Представление для главной страницы."""

    template_name = "blog/index.html"
    paginate_by = PAGE_PAGINATOR
    context_object_name = "posts"

    def get_queryset(self):
        return (
            Post.objects.filter(
                is_published=True,
                pub_date__lte=timezone.now(),
                category__is_published=True,
            )
            .order_by(
                "-pub_date",
            )
            .annotate(
                comment_count=Count("comment"),
            )
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["total_posts"] = Post.objects.filter(
            is_published=True,
            pub_date__lte=timezone.now(),
            category__is_published=True,
        ).count()
        return context


class CategoryListView(ListView):
    """Представление для списка категорий."""

    template_name = "blog/category.html"
    paginate_by = PAGE_PAGINATOR

    def get_queryset(self):
        category = self.get_category()
        if not category.is_published:
            slug = self.kwargs["category_slug"]
            raise Http404(
                f"Категория с slug {slug} не опубликована",
            )

        return (
            category.post.filter(
                is_published=True, pub_date__lte=timezone.now()
            )
            .order_by(
                "-pub_date",
            )
            .annotate(
                comment_count=Count("comment"),
            )
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["category"] = self.get_category()
        return context

    def get_category(self):
        slug = self.kwargs["category_slug"]
        return get_object_or_404(Category, slug=slug)


class ProfileListView(ListView):
    """Представление для профиля пользователя."""

    template_name = "blog/profile.html"
    paginate_by = PAGE_PAGINATOR

    def get_queryset(self):
        profile = self.get_profile()
        return (
            Post.objects.filter(
                author=profile,
            )
            .order_by(
                "-pub_date",
            )
            .annotate(
                comment_count=Count("comment"),
            )
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["profile"] = self.get_profile()
        return context

    def get_profile(self):
        username = self.kwargs["username"]
        return get_object_or_404(User, username=username)


@login_required(login_url="/auth/login/")
def edit_profile(request):
    """Представление для редактирования профиля."""
    profile = request.user

    if request.method == "POST":
        form = ProfileEditForm(request.POST, instance=profile)
        if form.is_valid():
            form.save()
            return redirect("blog:profile", profile.username)
    else:
        form = ProfileEditForm(instance=profile)

    context = {
        "profile": profile,
        "form": form,
    }
    return render(request, "blog/user.html", context)


def post_detail(request, post_id):
    """Представление для детального отображения поста."""
    current_post = get_object_or_404(
        Post,
        pk=post_id,
    )

    if request.user != current_post.author:
        current_post = get_object_or_404(
            Post,
            pk=post_id,
            is_published=True,
            pub_date__lte=timezone.now(),
            category__is_published=True,
        )

    comments = Comment.objects.filter(post=current_post)

    form = CommentForm()

    context = {
        "post": current_post,
        "form": form,
        "comments": comments,
    }
    return render(request, "blog/detail.html", context)


@login_required(login_url="/auth/login/")
def create_post(request, pk_post=None):
    """Представление для создания и редактирования поста."""
    user = request.user

    if pk_post:
        instance = get_object_or_404(Post, id=pk_post)
        if user != instance.author:
            return redirect("blog:post_detail", instance.pk)
    else:
        instance = None

    form = PostForm(
        request.POST or None,
        request.FILES or None,
        instance=instance,
    )

    if form.is_valid():
        new_post = form.save(commit=False)
        new_post.author = user
        new_post.save()
        return redirect("blog:profile", user.username)

    context = {"form": form}
    return render(request, "blog/create.html", context)


@login_required(login_url="/auth/login/")
def delete_post(request, pk_post):
    """Представление для удаления поста."""
    user = request.user
    instance = get_object_or_404(Post, pk=pk_post)

    if user != instance.author and not user.is_staff:
        return redirect("blog:post_detail", instance.pk)

    form = PostForm(instance=instance)
    context = {"form": form}

    if request.method == "POST":
        instance.delete()
        return redirect("blog:index")

    return render(request, "blog/create.html", context)


@login_required(login_url="/auth/login/")
def add_comment(request, post_id, comment_id=None):
    """Представление для создания и редактирования комментария."""
    user = request.user
    post = get_object_or_404(Post, pk=post_id)

    if comment_id:
        comment = get_object_or_404(Comment, pk=comment_id, post=post)
        if user != comment.author:
            return redirect("blog:post_detail", post_id=post.pk)
    else:
        comment = None

    form = CommentForm(request.POST or None, instance=comment)

    if request.method == "POST":
        if form.is_valid():
            comment = form.save(commit=False)
            comment.author = user
            comment.post = post
            comment.save()
            return redirect(reverse("blog:post_detail", args=[post.pk]))

    context = {
        "form": form,
        "comment": comment,
        "post": post,
    }

    return render(request, "blog/comment.html", context)


@login_required(login_url="/auth/login/")
def delete_comment(request, post_id, comment_id):
    """Представление для удаления комментария."""
    user = request.user
    comment = get_object_or_404(Comment, pk=comment_id)

    if user != comment.author:
        return redirect("blog:post_detail", post_id)

    if request.method == "POST":
        comment.delete()
        return redirect(reverse("blog:post_detail", args=[post_id]))

    context = {
        "comment": comment,
    }
    return render(request, "blog/comment.html", context)
