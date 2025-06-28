from django.urls import path
from home import views

urlpatterns = [
    path('', views.index, name='home'),              
    path('contact/', views.contact, name='contact'),
    path('members/', views.members_tab, name='members'),
    path('home/', views.home, name='home'),
    path('members/add',views.save_member,name = 'members'),
    path('books/',views.book_list,name = 'books'),
    path('issue/',views.issue_view,name = 'issue'),
    path('cart/',views.in_cart,name = 'cart'),
    path("login/", views.member_login, name="member_login"),
    path("cart/add",views.add_to_cart, name="add_cart"),
    path('logout/', views.member_logout, name='member_logout'),
    path('remove_cart/<int:id>/', views.remove_cart, name='remove_cart'),
    path('checkout/', views.checkout,name = 'checkout')
]