from django.db import models
from django.utils import timezone
from datetime import timedelta
from django.core.validators import MinLengthValidator
from django.core.exceptions import ValidationError
import re

def validate_gmail(value):
    pattern = r'^[a-zA-Z0-9._%+-]+@gmail\.com$'
    if not re.match(pattern, value):
        raise ValidationError("Enter a valid Gmail address (e.g., user@gmail.com).")

def get_due_date():
    return timezone.now().date() + timedelta(days=15)


# Create your models here.
class Member(models.Model):  
    name = models.CharField(max_length=100)
    reference_id = models.CharField(max_length=10)
    phone_number = models.CharField(max_length=10)
    address = models.TextField()
    active = models.BooleanField(default=True)

    password = models.CharField(
        max_length=128,  # Allows for hashed passwords
        validators=[MinLengthValidator(8)],
        help_text="Minimum 8 characters. For better security, store hashed passwords."
    )

    email = models.EmailField(
        unique=True,
        null=True ,
        validators=[MinLengthValidator(10), validate_gmail]
     )

    def __str__(self):
        return self.name

class Author(models.Model):
    name = models.CharField(max_length=100)
    bio = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.name
    
    
class Publisher(models.Model):
    name = models.CharField(max_length=100)
    address = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.name

class Books(models.Model):
    book_name = models.CharField(max_length=100)
    isbn = models.CharField(max_length=13, null=True, blank=True)
    available_copies = models.PositiveIntegerField(default=1)
    author_name = models.ManyToManyField(Author) 
    publisher = models.ForeignKey(Publisher, on_delete=models.SET_NULL, null=True, blank=True)

    def __str__(self):
        return self.book_name




class Issue(models.Model):
    book = models.ForeignKey(Books, on_delete=models.CASCADE)
    member = models.ForeignKey(Member, on_delete=models.CASCADE)
    issue_date = models.DateField(default=timezone.now)
    return_date = models.DateField(null=True, blank=True)
    due_date = models.DateField(default=get_due_date)


    def __str__(self):
        return f"{self.book.book_name} issued to {self.member.name}"
    

class Cart(models.Model):
    c_member = models.ForeignKey(Member, on_delete=models.CASCADE)
    c_book = models.ForeignKey(Books, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.c_member.name} - {self.c_book.book_name} by {self.c_book.author_name}"

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["c_member", "c_book"], name="unique_person_book")
        ]





