# Generated by Django 5.0.6 on 2024-06-22 14:58

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("books", "0005_alter_book_content"),
    ]

    operations = [
        migrations.AddField(
            model_name="book",
            name="status",
            field=models.CharField(
                choices=[("ebook", "E-book"), ("project", "Project")],
                default="project",
                max_length=10,
            ),
        ),
    ]