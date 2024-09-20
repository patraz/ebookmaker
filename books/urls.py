from django.urls import path
from .views import (
    BooksListView, BookDetailView, CreateEbookContent,
    DashboardView, CreateEbookView, BookDeleteView,
    download_pdf, EditBookContentView
)

urlpatterns = [
    path("", BooksListView.as_view(), name='book-list'),
    path('dashboard/', DashboardView.as_view(), name='dashboard'),
    path("<int:pk>/", BookDetailView.as_view(), name='book-detail'),
    path("update/<int:pk>/", EditBookContentView.as_view(),
         name='update-subchapter'),
    path("delete/<int:pk>/", BookDeleteView.as_view(), name='book-delete'),
    path("create/", CreateEbookContent.as_view(), name='book-create'),
    path("generate/<int:pk>", CreateEbookView.as_view(), name='generate-ebook'),
    path('download-pdf/<int:pk>/', download_pdf, name='download-pdf'),
]
