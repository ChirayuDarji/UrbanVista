from django.test import TestCase
from django.contrib.auth import get_user_model
from news.models import Category, News


class NewsModelTests(TestCase):
    def test_str_and_manager(self):
        cat = Category.objects.create(name="Transport", slug="transport")
        author = get_user_model().objects.create_user(username="u1", password="pass12345")
        n = News.objects.create(title="T1", category=cat, author=author, content="c", status="published")
        self.assertEqual(str(n), "T1")
        self.assertEqual(News.objects.published().count(), 1)


