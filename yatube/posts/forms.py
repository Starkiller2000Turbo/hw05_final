from django import forms

from posts.models import Comment, Post


class PostForm(forms.ModelForm):
    """Форма на основе модели поста."""

    class Meta:
        model = Post
        fields = ('text', 'group', 'image')


class CommentForm(forms.ModelForm):
    """Форма на основе модели комментария."""

    class Meta:
        model = Comment
        fields = ('text',)
