from django.contrib.auth import get_user_model
from django.test import TestCase
from mixer.backend.django import mixer

from posts.models import Group, Post
from yatube import settings

User = get_user_model()


class PostModelTest(TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        super().setUpClass()
        cls.post = mixer.blend(Post)

    def test_posts_have_correct_str(self) -> None:
        """Проверяем, что у модели Post корректно работает __str__."""
        self.assertEqual(
            self.post.text[: settings.TEXT_LENGTH],  # fmt: skip
            str(self.post),
        )


class GroupModelTest(TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        super().setUpClass()
        cls.group = mixer.blend(Group)

    def test_groups_have_correct_str(self) -> None:
        """Проверяем, что у модели Group корректно работает __str__."""
        self.assertEqual(self.group.title, str(self.group))
