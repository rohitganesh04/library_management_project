from django.contrib import admin
from .models import Member,Books,Issue,Cart,Publisher,Author

admin.site.register(Member)
admin.site.register(Books)
admin.site.register(Issue)
admin.site.register(Cart)
admin.site.register(Publisher)
admin.site.register(Author)