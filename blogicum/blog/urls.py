from blog import views
from django.urls import path

from . import views

app_name = "blog"
urlpatterns = [
    path(
        '',
        views.HomePage.as_view(),
        name='index',
    ),
    path(
        'category/<slug:category_slug>/',
        views.CategoryListView.as_view(),
        name='category_posts',
    ),
    path(
        'profile/<str:username>/',
        views.ProfileListView.as_view(),
        name='profile',
    ),
    path(
        'profile/edit',
        views.edit_profile,
        name='edit_profile',
    ),
    path(
        'posts/<int:post_id>/',
        views.post_detail,
        name='post_detail',
    ),
    path(
        'posts/create/',
        views.create_post,
        name='create_post',
    ),
    path(
        'posts/<int:pk_post>/edit/',
        views.create_post,
        name='edit_post',
    ),
    path(
        'posts/<int:pk_post>/delete/',
        views.delete_post,
        name='delete_post',
    ),
    path(
        'posts/<int:post_id>/comment/',
        views.add_comment,
        name='add_comment',
    ),
    path(
        'posts/<int:post_id>/edit_comment/<int:comment_id>/',
        views.add_comment,
        name='edit_comment',
    ),
    path(
        'posts/<int:post_id>/delete_comment/<int:comment_id>/',
        views.delete_comment,
        name='delete_comment',
    )
]
