from django.shortcuts import render,HttpResponse,redirect
from .models import *
from .models import Member,Books,Issue
from .forms import MemberLoginForm
from django.contrib import messages
from django.contrib.auth import logout,authenticate,login
import re
from django.core.validators import validate_email
from django.core.exceptions import ValidationError


# Create your views here.
def index(request):
    # Check if member is logged in using session
    if 'member_id' not in request.session:
        return redirect('/login')  # Redirect to login if not authenticated

    try:
        member = Member.objects.get(id=request.session['member_id'])
    except Member.DoesNotExist:
        # If the member_id is invalid (e.g., deleted), clear session and redirect to login
        del request.session['member_id']
        return redirect('/login')

    # Set or reset cart click count
    request.session['cart_click_count'] = 0

    # Render the index page with member details (optional)
    return render(request, 'index.html', {'member': member})
def home(request):
   request.session['cart_click_count'] = 0
   return render(request,'index.html',context={"current_tab":"home"})


def members(request):
   request.session['cart_click_count'] = 0
   return render(request, 'members.html', context={"current_tab": "members"})

def contact(request):
   request.session['cart_click_count'] = 0
   return render(request,'contact.html',context={"current_tab": "contact"})



def members_tab(request):
    request.session['cart_click_count'] = 0
    if request.method == "GET":
        members_list = Member.objects.all()
        return render(request, 'members.html', context={
            "current_tab": "members",
            "members": members_list
        })
    else:
        query = request.POST.get('query', '')
        filtered_members = Member.objects.filter(name__icontains=query)
        return render(request, 'members.html', context={
            "current_tab": "members",
            "members": filtered_members,
            "query": query
        })

def save_member(request):
   if request.method == "POST":
        name = request.POST.get("name")
        address = request.POST.get("address")
        phone = request.POST.get("phoneno")
        reference_id = request.POST.get("referenceid")
        email = request.POST.get("email")
        password1 = request.POST.get("password1")
        password2 = request.POST.get("password2")

        try:
          validate_email(email)
        except ValidationError:
           messages.error(request, "Invalid email address.")
           return redirect("/members/")
        
        if Member.objects.filter(email=email).exists():
            messages.error(request, "Email already registered.")
            return redirect("/members/")

        if password1 != password2:
            messages.error(request, "Passwords do not match.")
            return redirect("/members/")

        Member.objects.create(
            name=name,
            address=address,
            phone_number=phone,
            reference_id=reference_id,
            email=email,
            password=password1 
        )

        messages.success(request, "Member registered successfully.")
        return redirect("/members/")
   
   return redirect("/members")

def book_list(request):
    request.session['cart_click_count'] = 0
    books = Books.objects.all()
    return render(request, 'books.html', {'books': books})

def issue_view(request):
    request.session['cart_click_count'] = 0
    if request.method == "GET":
        issue_list = Issue.objects.all()
        return render(request,'issue.html',context={
        "current_tab": "issue",
        "issued": issue_list
        })
    else:
        return render(request,'issue.html',context={"current_tab": "issue"})

from django.shortcuts import render, redirect, get_object_or_404
from .models import Cart, Books, Member

def in_cart(request):
    # Ensure user is logged in via session
    member_id = request.session.get('member_id')
    if not member_id:
        return redirect('/login')

    # Reset or update cart click counter
    if request.GET.get('from') == 'manual':
        click_count = request.session.get('cart_click_count', 0)
        if click_count >= 1:
            request.session['cart_click_count'] = 0
            return redirect('/books')
        request.session['cart_click_count'] = click_count + 1

    # Fetch current member object
    member = get_object_or_404(Member, id=member_id)

    # Only fetch cart items for this logged-in member
    cart_items = Cart.objects.filter(c_member=member)
    cart_books = request.session.get('cart_books', [])
    books = Books.objects.all()

    return render(request, 'cart.html', context={
        'cart_books': cart_books,
        'cartcart': cart_items,
        'books': books
    })

def member_login(request):
    if request.method == "POST":
        form = MemberLoginForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data["email"]
            password = form.cleaned_data["password"]

            try:
                member = Member.objects.get(email=email, password=password)
                request.session['member_id'] = member.id  # Store in session
                #messages.success(request, f"Welcome, {member.name}!")
                return redirect('home')  # or any other page
            except Member.DoesNotExist:
                messages.error(request, "Invalid email or password")
    else:
        form = MemberLoginForm()

    return render(request, "member_login.html", {"form": form})

def add_to_cart(request):
    if request.method == "POST":
        member_id = request.session.get('member_id')
        if not member_id:
            messages.error(request, "You must be logged in to add to cart.")
            return redirect('/login')

        book_id = request.POST.get('book_id')
        if book_id:
            try:
                book = Books.objects.get(id=book_id)
                member = Member.objects.get(id=member_id)

                if not Cart.objects.filter(c_book=book, c_member=member).exists():
                    Cart.objects.create(c_book=book, c_member=member)
                    messages.success(request, "Book added to cart!")
                else:
                    messages.info(request, "Book already in cart.")
            except Books.DoesNotExist:
                messages.error(request, "Book not found.")
            except Member.DoesNotExist:
                messages.error(request, "Member not found.")

        return redirect('/cart')

    return redirect('/')


def checkout(request):
    member_id = request.session.get('member_id')
    if not member_id:
        return redirect('/login')
    member = get_object_or_404(Member, id=member_id)
    cart_items = Cart.objects.filter(c_member=member)
    if not cart_items.exists():
        messages.info(request, "Your cart is empty.")
        return redirect('/cart')
    
    for item in cart_items:
        # Create a checkout record for each cart item
        Issue.objects.create(
            member=member,
            book=item.c_book,
        )
        item.delete()  # Remove the item from the cart after checkout
    return redirect('/books')

def remove_cart(request, id):
    member_id = request.session.get('member_id')
    if not member_id:
        return redirect('/login')

    cart_item = get_object_or_404(Cart, id=id, c_member_id=member_id)
    cart_item.delete()
    return redirect('/cart')




def member_logout(request):
    # Clear only member-specific session data
    if 'member_id' in request.session:
        del request.session['member_id']

    # Optional: clear entire session
    # request.session.flush()

    return redirect('/login')  # Redirect to login page after logout


