# users/admin.py
from django.contrib import admin
from .models import User  # Import the User model

# Register the User model with the admin site
@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ('id', 'username', 'email', 'role')  # Fields to display in the admin list view
    search_fields = ('username', 'email')  # Fields to search
    list_filter = ('role',)  # Add filters for the role

# Alternatively, you can use the following line to register without a custom admin class
# admin.site.register(User)
