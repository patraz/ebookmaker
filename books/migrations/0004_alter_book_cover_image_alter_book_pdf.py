# Generated by Django 5.0.6 on 2024-06-20 17:53

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("books", "0003_book_content"),
    ]

    operations = [
        migrations.AlterField(
            model_name="book",
            name="cover_image",
            field=models.ImageField(blank=True, null=True, upload_to="book_covers/"),
        ),
        migrations.AlterField(
            model_name="book",
            name="pdf",
            field=models.FileField(blank=True, null=True, upload_to="book_pdfs/"),
        ),
    ]
