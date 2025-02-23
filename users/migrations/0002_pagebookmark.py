# Generated by Django 5.1.6 on 2025-02-23 17:30

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='PageBookmark',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('url', models.URLField()),
                ('title', models.CharField(max_length=255)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('order', models.PositiveIntegerField(default=0)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='page_bookmarks', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'ordering': ['order', '-created_at'],
                'constraints': [models.UniqueConstraint(fields=('user', 'url'), name='unique_user_page_bookmark')],
            },
        ),
    ]
