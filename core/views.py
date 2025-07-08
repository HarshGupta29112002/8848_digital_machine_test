from django.shortcuts import render
from rest_framework import generics, status
from rest_framework.views import APIView
from rest_framework.response import Response
from django.db.models import Q #To use logical operators
from .models import Book, Member, Transaction
from .serializers import BookSerializer, MemberSerializer, TransactionSerializer
from datetime import date

import requests

# Create your views here.


# use case 1 : CRUD operations on Books and Members ------------>>>>>>>>>>

class BookListCreateView(generics.ListCreateAPIView):
    queryset = Book.objects.all()
    serializer_class = BookSerializer

class BookDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Book.objects.all()
    serializer_class = BookSerializer

class MemberListCreateView(generics.ListCreateAPIView):
    queryset = Member.objects.all()
    serializer_class = MemberSerializer

class MemberDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Member.objects.all()
    serializer_class = MemberSerializer


# use case 2 : Issue book ----------------->>>>>>>>>>>>>>>>

class IssueBookView(APIView):
    def post(self, request):
        member_id = request.data.get('member_id')
        book_id = request.data.get('book_id')

        try:
            member = Member.objects.get(id=member_id)
            book = Book.objects.get(id=book_id)
        except(Member.DoesNotExist, Book.DoesNotExist):
            return Response({'error': 'Member or Book not found'}, status=404)
        
        if member.total_debt > 500:
            return Response({'error' : 'Outstanding debt > ₹500'}, status=400)
        
        if book.stock < 1:
            return Response({'error' : 'Book out of stock'},status=400)
        
        Transaction.objects.create(member=member, book=book)
        book.stock -= 1
        book.save()

        return Response({'message':'Book issued successfully'}, status=201)
    

# Issue book return ------------->>>>>>>>>>>>

class ReturnBookView(APIView):
    def post(self, request):
        member_id = request.data.get('member_id')
        book_id = request.data.get('book_id')

        try:
            transaction = Transaction.objects.get(member_id=member_id, book_id=book_id, status='issued')
        except Transaction.DoesNotExist:
            return Response({'error':'No active issue recorded'}, status=404)
        
        today = date.today()
        days_passed = (today - transaction.issue_date).days
        rent = days_passed * 10

        member = transaction.member
        if member.total_debt + rent > 500:
            return Response({'error':'Debt will exceed ₹500'},status=400)
        
        transaction.return_date = today
        transaction.rent_fee = rent
        transaction.status = 'returned'
        transaction.save()

        book = transaction.book
        book.stock += 1
        book.save()

        return Response({'message':f'Book returned. Rent charged ₹{rent}'}, status=200)
    
class BookSearchView(APIView):
    def get(self, request):
        q = request.GET.get('q','')
        results = Book.objects.filter(Q(title__icontains=q) | Q(authors__icontains=q))
        serializer = BookSerializer(results, many=True)
        return Response(serializer.data)
    

# API -------->>>>>>>>

class ImportBooksFromFrappe(APIView):
    def post(self, request):
        title = request.data.get('title','')
        count = int(request.data.get('count',20))
        page = 1
        imported = 0

        while imported < count:
            response = requests.get(
                'https://frappe.io/api/method/frappe-library',
                params={
                    'page': page,
                    'title' : title
                }
            )

            books = response.json().get('message', [])
            if not books:
                break

            for b in books:
                if imported >= count:
                    break
                try:
                    Book.objects.get(isbn = b['isbn'])
                    continue
                except Book.DoesNotExist:
                    Book.objects.create(
                        title=b['title'],
                        authors=b['authors'],
                        isbn=b['isbn'],
                        publisher=b['publisher'],
                        num_pages=b.get('num_pages') or 0,
                        stock=5 
                    )
                    imported += 1
            page += 1
        return Response({'message':f'{imported} books imported.'})