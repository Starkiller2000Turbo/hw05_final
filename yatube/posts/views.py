from django.contrib.auth.decorators import login_required
from django.http import HttpRequest, HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.cache import cache_page

from core.utils import paginate
from posts.forms import CommentForm, PostForm
from posts.models import Follow, Group, Post, User


@cache_page(20)
def index(request: HttpRequest) -> HttpResponse:
    """Обработка перехода на главную страницу.

    Args:
        request: Передаваемый запрос.

    Returns:
        Рендер главной страницы.
    """
    return render(
        request,
        'posts/index.html',
        {
            'page_obj': paginate(
                request,
                Post.objects.select_related(
                    'author',
                    'group',
                ),
            ),
        },
    )


def group_posts(request: HttpRequest, slug: str) -> HttpResponse:
    """Обработка перехода на страницу определённой группы.

    Args:
        request: Передаваемый запрос.
        slug: Запрос определённой группы, используемый в URL.

    Returns:
        Рендер страницы выбранной группы.
    """
    group = get_object_or_404(Group, slug=slug)
    return render(
        request,
        'posts/group_list.html',
        {
            'page_obj': paginate(
                request,
                group.posts.select_related('author'),
            ),
            'group': group,
        },
    )


def profile(request: HttpRequest, username: str) -> HttpResponse:
    """Обработка перехода на страницу пользователя.

    Args:
        request: Передаваемый запрос.
        username: url/имя автора

    Returns:
        Рендер страницы пользователя.
    """
    author = get_object_or_404(User, username=username)
    following = request.user.is_authenticated and request.user.follower.filter(
        author=author,
    )
    return render(
        request,
        'posts/profile.html',
        {
            'page_obj': paginate(
                request,
                author.posts.select_related('group'),
            ),
            'author': author,
            'following': following,
        },
    )


def post_detail(request: HttpRequest, pk: int) -> HttpResponse:
    """Обработка перехода на страницу определённого поста.

    Args:
        request: Передаваемый запрос.
        pk: id определённого поста

    Returns:
        Рендер страницы выбранного поста.
    """
    post = get_object_or_404(Post, id=pk)
    form = CommentForm(
        request.POST or None,
    )
    return render(
        request,
        'posts/post_detail.html',
        {
            'post': post,
            'form': form,
        },
    )


@login_required
def post_create(request: HttpRequest) -> HttpResponse:
    """Обработка перехода на страницу создания поста.

    Args:
        request: Передаваемый запрос.

    Returns:
        Рендер страницы создания поста.
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
    return redirect('posts:profile', request.user.get_username())


@login_required
def post_edit(request: HttpRequest, pk: str) -> HttpResponse:
    """Обработка перехода на страницу редактирования поста.

    Args:
        request: Передаваемый запрос.
        pk: id поста, подвергаемого редактированию

    Returns:
        Рендер страницы редактирования поста.
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
        Рендер страницы выбранного поста.
    """
    post = get_object_or_404(Post, id=pk)
    form = CommentForm(request.POST or None)
    if form.is_valid():
        form.instance.author = request.user
        form.instance.post = post
        form.save()
    return redirect('posts:post_detail', pk=pk)


@login_required
def follow_index(request: HttpRequest) -> HttpResponse:
    """Обработка перехода на страницу постов из подписок.

    Args:
        request: Передаваемый запрос.

    Returns:
        Возвращает рендер страницы редактирования поста.
    """
    return render(
        request,
        'posts/follow.html',
        {
            'page_obj': paginate(
                request,
                Post.objects.filter(
                    author__following__user=request.user,
                ).select_related(
                    'author',
                    'group',
                ),
            ),
        },
    )


@login_required
def profile_follow(request: HttpRequest, username: str) -> HttpResponse:
    """Обработка запроса на подписку на определённого пользователя.

    Args:
        request: Передаваемый запрос.
        username: логин автора, на которого подписываются

    Returns:
        Рендер страницы редактирования поста.
    """
    author = get_object_or_404(User, username=username)
    if (
        author != request.user
        and not author.following.filter(
            user=request.user,
        ).exists()
    ):
        Follow.objects.create(author=author, user=request.user)
    return redirect('posts:profile', username=username)


@login_required
def profile_unfollow(request: HttpRequest, username: str) -> HttpResponse:
    """Обработка запроса на отписку от определённого пользователя.

    Args:
        request: Передаваемый запрос.
        username: логин автора, от которого отписываются

    Returns:
        Рендер страницы редактирования поста.
    """
    get_object_or_404(
        Follow,
        author=get_object_or_404(User, username=username),
        user=request.user,
    ).delete()
    return redirect('posts:profile', username)
