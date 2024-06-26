from django.test import TestCase, Client
from django.urls import reverse
from django.shortcuts import resolve_url
from django.contrib.auth.models import User
from .models import Book
from django.core.files.uploadedfile import SimpleUploadedFile


class BooksListViewTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser', password='12345')
        self.book = Book.objects.create(title='Test Book', user=self.user)

    def test_view_requires_login(self):
        response = self.client.get(reverse('book-list'))
        self.assertRedirects(
            response, f"{resolve_url('login')}?next={reverse('book-list')}")

    def test_view_with_login(self):
        self.client.login(username='testuser', password='12345')
        response = self.client.get(reverse('book-list'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'book_list.html')
        self.assertContains(response, 'Test Book')


class DownloadPDFTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser', password='12345')
        self.book = Book.objects.create(title='Test Book', user=self.user)
        self.book.pdf = SimpleUploadedFile(
            "test.pdf", b"file_content", content_type="application/pdf")
        self.book.save()

    def test_download_pdf(self):
        self.client.login(username='testuser', password='12345')
        response = self.client.get(
            reverse('download-pdf', args=[self.book.pk]))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'application/pdf')
        self.assertEqual(response['Content-Disposition'],
                         f'attachment; filename="Test Book.pdf"')

    def test_download_pdf_not_found(self):
        self.client.login(username='testuser', password='12345')
        non_existent_pk = self.book.pk + 1
        response = self.client.get(
            reverse('download-pdf', args=[non_existent_pk]))
        self.assertEqual(response.status_code, 404)


class BookDetailViewTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser', password='12345')
        self.book = Book.objects.create(title='Test Book', user=self.user)

    def test_view_requires_login(self):
        response = self.client.get(reverse('book-detail', args=[self.book.pk]))
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, f'/accounts/login/?next=/1/')

    def test_view_requires_login(self):
        response = self.client.get(reverse('book-detail', args=[self.book.pk]))
        self.assertRedirects(
            response, f"{resolve_url('login')}?next={reverse('book-detail', args=[self.book.pk])}")
