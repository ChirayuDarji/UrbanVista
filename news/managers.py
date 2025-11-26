from django.db import models


class NewsQuerySet(models.QuerySet):
    def published(self):
        return self.filter(status='published')

    def featured(self):
        return self.published().filter(is_featured=True)


class NewsManager(models.Manager):
    def get_queryset(self):
        return NewsQuerySet(self.model, using=self._db)

    def published(self):
        return self.get_queryset().published()

    def featured(self):
        return self.get_queryset().featured()


