from django.db import models
from django.conf import settings

# Create your models here.
User = settings.AUTH_USER_MODEL


class Book(models.Model):
    CHOICES = (
        ("Polish", "Polski"),
        ("Ukrainian", "Ukraiński"),
        ("English", "Angielski")
    )

    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='books')
    title = models.CharField(max_length=255)
    content = models.JSONField(blank=True, null=True)
    cover_image = models.ImageField(
        upload_to='book_covers/', blank=True, null=True)
    pdf = models.FileField(upload_to='book_pdfs/', null=True, blank=True)
    language = models.CharField(
        max_length=50, choices=CHOICES, default="Polish")
    status = models.CharField(max_length=10, choices=[(
        'ebook', 'E-book'), ('project', 'Project')], default='project')
    modified_ebook = models.BooleanField(default=False)

    def save(self, *args, **kwargs):
        if self.pdf:
            self.status = 'ebook'
        else:
            self.status = 'project'
        super().save(*args, **kwargs)

    def __str__(self):
        return self.title
