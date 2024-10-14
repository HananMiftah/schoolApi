# requests/admin.py
from django.contrib import admin
from .models import Request

# @admin.register(Request)
# class RequestAdmin(admin.ModelAdmin):
#     list_display = ('id', 'school', 'status')  # Fields to display in the admin list view
#     search_fields = ('school__name',)  # Allow searching by school name
#     list_filter = ('status',)  # Add filters for the status
admin.site.register(Request)