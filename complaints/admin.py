from django.contrib import admin
from .models import Complaint


@admin.register(Complaint)
class ComplaintAdmin(admin.ModelAdmin):

    list_display = (
        'title',
        'category',
        'priority',
        'status',
        'location',
        'created_at'
    )

    list_filter = (
        'category',
        'priority',
        'status'
    )

    search_fields = (
        'title',
        'description',
        'location'
    )