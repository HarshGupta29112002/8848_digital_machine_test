from django.urls import path
from . import views

urlpatterns = [
    path('books/', views.BookListCreateView.as_view()),
    path('books/<int:pk>/', views.BookDetailView.as_view()),
    path('members/', views.MemberListCreateView.as_view()),
    path('members/<int:pk>/', views.MemberDetailView.as_view()),
    path('issue/', views.IssueBookView.as_view()),
    path('return/', views.ReturnBookView.as_view()),
    path('search/', views.BookSearchView.as_view()),
    path('import-books/', views.ImportBooksFromFrappe.as_view()),
]
