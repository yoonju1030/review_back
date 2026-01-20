from django.db import models
import json


class Anime(models.Model):
    name = models.CharField(max_length=200)
    image = models.URLField(max_length=500, blank=True, null=True)
    air_year_quarter = models.CharField(max_length=20, blank=True, null=True)
    content = models.TextField(blank=True, null=True)
    content_rating = models.CharField(max_length=50, blank=True, null=True)
    ended = models.BooleanField(default=False)
    genres = models.JSONField(default=list, blank=True)
    tags = models.JSONField(default=list, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "anime"

    def __str__(self):
        return self.name
