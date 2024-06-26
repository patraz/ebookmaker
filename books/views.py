from django.http import HttpResponse, FileResponse
from django.shortcuts import get_object_or_404, redirect, render
import os
from .models import Book
from .forms import EbookForm
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views import generic
from django.urls import reverse, reverse_lazy
from .models import Book
from .ebook_content_generator import EbookCreator
import json
from .pdf_creator.pdf_from_content import create_pdf_from_dict
# Create your views here.
from django.conf import settings


class DashboardView(LoginRequiredMixin, generic.ListView):
    context_object_name = "books"
    template_name = "dashboard/dashboard.html"

    def get_queryset(self):
        return Book.objects.filter(user=self.request.user)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        queryset = self.get_queryset()
        ebooks = 0
        for x in queryset:
            if x.pdf:
                ebooks += 1
        context['ebooks'] = ebooks
        context['projects'] = queryset.count() - ebooks
        return context


class CreateEbookContent(LoginRequiredMixin, generic.FormView):
    template_name = 'dashboard/create.html'
    form_class = EbookForm

    def form_valid(self, form):
        language = form.cleaned_data['language']
        chapters = form.cleaned_data['chapters']
        subchapters = form.cleaned_data['subchapters']
        title = form.cleaned_data['title']
        print(title)

        EbookCreator().create_all_ebook_content(
            title=f"{title}", language=language, chapters=chapters, subchapters=subchapters)

        cover_image_name = f"{title.replace(' ', '_')}.png"

        file_path = os.path.join('book_covers', cover_image_name)

        source_path = os.path.join(settings.MEDIA_ROOT, file_path)

        book = Book.objects.create(
            title=title,
            user=self.request.user
        )
        book.cover_image = source_path
        with open("ebook_structure.json", "r") as chapters_file:
            ebook_structure = json.load(chapters_file)
            book.content = ebook_structure
            book.save()

        os.remove("ebook_structure.json")

        return super().form_valid(form)

    def get_success_url(self):
        return reverse('book-list')


class CreateEbookView(LoginRequiredMixin, generic.View):
    def post(self, request, *args, **kwargs):
        book = Book.objects.get(pk=self.kwargs.get('pk'))
        book.pdf = create_pdf_from_dict(
            ebook_structure=book.content, title_image=book.cover_image)
        book.modified_ebook = False
        book.save()
        return redirect('book-detail', pk=book.pk)


class BooksListView(LoginRequiredMixin, generic.ListView):
    template_name = "book_list.html"
    context_object_name = 'books'
    paginate_by = 5

    def get_queryset(self):
        qs = Book.objects.filter(user=self.request.user).order_by('-pk')
        return qs


class BookDetailView(LoginRequiredMixin, generic.DetailView):
    template_name = "dashboard/book_detail.html"
    queryset = Book.objects.all()
    context_object_name = "book"


class EditBookContentView(LoginRequiredMixin, generic.View):
    def post(self, request, pk):
        print(request.POST)
        subheading = self.request.POST.get('subchapter_title')
        chapter_title = self.request.POST.get('chapter_title')
        ebook_title = self.request.POST.get('book_title')
        book = get_object_or_404(Book, pk=pk)
        new_content = EbookCreator().create_subchapter_content(
            ebook_title=ebook_title, chapter=chapter_title, subheading=subheading, language=book.language)
        print(book.content[ebook_title]['chapters'][chapter_title][subheading])
        book.content[ebook_title]['chapters'][chapter_title][subheading] = new_content
        book.modified_ebook = True
        book.save()
        return redirect(reverse('book-detail', kwargs={'pk': pk}))


class BookDeleteView(LoginRequiredMixin, generic.DeleteView):
    model = Book
    success_url = reverse_lazy('book-list')
    template_name = 'book_confirm_delete.html'


def download_pdf(request, pk):
    book = get_object_or_404(Book, pk=pk)
    if book.pdf:
        response = FileResponse(book.pdf.open(
            'rb'), content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="{book.title}.pdf"'

        return response
    else:
        # gdy plik PDF nie istnieje
        return HttpResponse("PDF nie jest dostępny", status=404)
