from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.http import HttpRequest, HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.cache import cache_page

from core.utils import paginate
from posts.forms import CommentForm, PostForm
from posts.models import Comment, Follow, Group, Post, User


@cache_page(20, key_prefix='index')
def index(request: HttpRequest) -> HttpResponse:
    """Обработка перехода на главную страницу.

    Args:
        request: Передаваемый запрос.

    Returns:
        Возвращает рендер главной страницы.
    """
    posts = Post.objects.select_related('author', 'group')
    obj = paginate(request, posts, settings.OBJECTS_ON_PAGE)
    return render(
        request,
        'posts/index.html',
        {
            'page_obj': obj,
        },
    )


def group_posts(request: HttpRequest, slug: str) -> HttpResponse:
    """Обработка перехода на страницу определённой группы.

    Args:
        request: Передаваемый запрос.
        slug: Запрос определённой группы, используемый в URL

    Returns:
        Возвращает рендер страницы выбранной группы.
    """
    group = get_object_or_404(Group, slug=slug)
    posts = Post.objects.filter(group=group).select_related('author')
    obj = paginate(request, posts, settings.OBJECTS_ON_PAGE)
    return render(
        request,
        'posts/group_list.html',
        {
            'page_obj': obj,
            'group': group,
        },
    )


def profile(request: HttpRequest, username: str) -> HttpResponse:
    """Обработка перехода на страницу пользователя.

    Args:
        request: Передаваемый запрос.
        username: url/имя автора

    Returns:
        Возвращает рендер страницы пользователя.
    """
    author = get_object_or_404(User, username=username)
    posts = Post.objects.filter(author=author).select_related('group')
    page_obj = paginate(request, posts, settings.OBJECTS_ON_PAGE)
    if request.user.is_authenticated:
        following = author in (
            follow.author
            for follow in Follow.objects.filter(user=request.user)
        )
    else:
        following = False
    return render(
        request,
        'posts/profile.html',
        {
            'page_obj': page_obj,
            'author': author,
            'following': following,
        },
    )


def post_detail(request: HttpRequest, pk: str) -> HttpResponse:
    """Обработка перехода на страницу определённого поста.

    Args:
        request: Передаваемый запрос.
        pk: id определённого поста

    Returns:
        Возвращает рендер страницы выбранного поста.
    """
    post = get_object_or_404(Post, id=pk)
    form = CommentForm(
        request.POST or None,
    )
    comments = Comment.objects.filter(post=post).select_related('author')
    return render(
        request,
        'posts/post_detail.html',
        {
            'post': post,
            'form': form,
            'comments': comments,
        },
    )


@login_required
def post_create(request: HttpRequest) -> HttpResponse:
    """Обработка перехода на страницу создания поста.

    Args:
        request: Передаваемый запрос.

    Returns:
        Возвращает рендер страницы создания поста.
    """
    form = PostForm(
        request.POST or None,
        files=request.FILES or None,
    )
    if not form.is_valid():
        return render(
            request,
            'posts/create_post.html',
            {'form': form, 'is_edit': False},
        )
    form.instance.author = request.user
    form.save()
    return redirect('posts:profile', request.user.username)


@login_required
def post_edit(request: HttpRequest, pk: str) -> HttpResponse:
    """Обработка перехода на страницу редактирования поста.

    Args:
        request: Передаваемый запрос.
        pk: id поста, подвергаемого редактированию

    Returns:
        Возвращает рендер страницы редактирования поста.
    """
    post = get_object_or_404(Post, id=pk)
    if request.user != post.author:
        return redirect('posts:post_detail', pk)
    form = PostForm(
        request.POST or None,
        files=request.FILES or None,
        instance=post,
    )
    if not form.is_valid():
        return render(
            request,
            'posts/create_post.html',
            {
                'form': form,
                'is_edit': True,
                'post': post,
            },
        )
    form.save()
    return redirect('posts:post_detail', pk)


@login_required
def add_comment(request: HttpRequest, pk: str) -> HttpResponse:
    """Обработка отправления комментария к выбранному посту.

    Args:
        request: Передаваемый запрос.
        pk: id поста, подвергаемого комментированию

    Returns:
        Возвращает рендер страницы выбранного поста.
    """
    post = get_object_or_404(Post, id=pk)
    form = CommentForm(request.POST or None)
    if form.is_valid():
        comment = form.save(commit=False)
        comment.author = request.user
        comment.post = post
        comment.save()
    return redirect('posts:post_detail', pk=pk)


@login_required
def follow_index(request: HttpRequest) -> HttpResponse:
    """Обработка перехода на страницу постов из подписок.

    Args:
        request: Передаваемый запрос.

    Returns:
        Возвращает рендер страницы редактирования поста.
    """
    followings = Follow.objects.filter(user=request.user)
    posts = Post.objects.filter(
        author__in=(follow.author for follow in followings),
    ).select_related('author', 'group')
    obj = paginate(request, posts, settings.OBJECTS_ON_PAGE)
    return render(
        request,
        'posts/follow.html',
        {
            'page_obj': obj,
        },
    )


@login_required
def profile_follow(request: HttpRequest, username: str) -> HttpResponse:
    """Обработка запроса на подписку на определённого пользователя.

    Args:
        request: Передаваемый запрос.
        username: логин автора, на которого подписываются

    Returns:
        Возвращает рендер страницы редактирования поста.
    """
    author = get_object_or_404(User, username=username)
    if author != request.user and not Follow.objects.filter(
        author=author, user=request.user
    ):
        Follow.objects.create(author=author, user=request.user)
    return redirect('posts:profile', username=author.username)


@login_required
def profile_unfollow(request: HttpRequest, username: str) -> HttpResponse:
    """Обработка запроса на отписку от определённого пользователя.

    Args:
        request: Передаваемый запрос.
        username: логин автора, от которого отписываются

    Returns:
        Возвращает рендер страницы редактирования поста.
    """
    author = get_object_or_404(User, username=username)
    if Follow.objects.filter(author=author, user=request.user):
        Follow.objects.get(author=author, user=request.user).delete()
    return redirect('posts:profile', author.username)
