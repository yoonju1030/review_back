# Generated manually for MariaDB migration

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Anime',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=200)),
                ('image', models.URLField(blank=True, max_length=500, null=True)),
                ('air_year_quarter', models.CharField(blank=True, max_length=20, null=True)),
                ('content', models.TextField(blank=True, null=True)),
                ('content_rating', models.CharField(blank=True, max_length=50, null=True)),
                ('ended', models.BooleanField(default=False)),
                ('genres', models.JSONField(blank=True, default=list)),
                ('tags', models.JSONField(blank=True, default=list)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
            ],
            options={
                'db_table': 'anime',
            },
        ),
    ]

