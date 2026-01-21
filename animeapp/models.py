from django.db import models
import json

class Genre(models.Model):
    """
    Anime 장르 마스터 테이블
    """
    name = models.CharField(max_length=50)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "genre"
        
    def __str__(self):
        return self.name

class Anime(models.Model):
    """
    애니메이션 테이블 (필요한 필드는 취향대로 추가/수정)
    """
    name = models.CharField(max_length=200)
    laftel_id = models.IntegerField(null=True, blank=True, db_index=True)
    image = models.URLField(max_length=500, blank=True, null=True)
    air_year_quarter = models.CharField(max_length=20, blank=True, null=True)
    content = models.TextField(blank=True, null=True)
    content_rating = models.CharField(max_length=50, blank=True, null=True)
    ended = models.BooleanField(default=False)
    # genres = models.JSONField(default=list, blank=True)
    genres = models.ManyToManyField(Genre, through='AnimeGenre', related_name='animes', blank=True)
    tags = models.JSONField(default=list, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "anime"
        indexes = [
            models.Index(fields=["name"]),
        ]

    def __str__(self):
        return self.name

class AnimeGenre(models.Model):
    """
    중간 테이블(through) - 인덱싱/확장(예: 우선순위, 추가 메타)을 위해 명시적으로 둠
    """
    anime = models.ForeignKey(Anime, on_delete=models.CASCADE)
    genre = models.ForeignKey(Genre, on_delete=models.CASCADE)

    # 필요하면 추가 메타 필드도 가능 (예: primary 여부, weight 등)
    # weight = models.PositiveSmallIntegerField(default=0)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "anime_genre"
        constraints = [
            models.UniqueConstraint(fields=["anime", "genre"], name="uq_anime_genre"),
        ]
        indexes = [
            models.Index(fields=["anime"]),
            models.Index(fields=["genre"]),
            models.Index(fields=["anime", "genre"]),
        ]

    def __str__(self) -> str:
        return f"{self.anime_id} - {self.genre_id}"