
from django.db import models
import uuid


class Complaint(models.Model):

    CATEGORY_CHOICES = [
        ('Road Damage', 'Road Damage'),
        ('Waterlogging', 'Waterlogging'),
        ('Garbage', 'Garbage'),
        ('Streetlight', 'Streetlight'),
        ('Drainage', 'Drainage'),
        ('Other', 'Other'),
    ]

    PRIORITY_CHOICES = [
        ('Critical', 'Critical'),
        ('High', 'High'),
        ('Medium', 'Medium'),
        ('Low', 'Low'),
    ]

    STATUS_CHOICES = [
        ('Submitted', 'Submitted'),
        ('Assigned', 'Assigned'),
        ('In Progress', 'In Progress'),
        ('Resolved', 'Resolved'),
    ]

    tracking_id = models.UUIDField(
        default=uuid.uuid4,
        unique=True,
        editable=False
    )

    title = models.CharField(max_length=200)

    description = models.TextField()

    image = models.ImageField(
        upload_to='complaint_images/',
        null=True,
        blank=True
    )

    category = models.CharField(
        max_length=50,
        choices=CATEGORY_CHOICES,
        default='Other'
    )

    location = models.CharField(max_length=255)

    latitude = models.FloatField(null=True, blank=True)

    longitude = models.FloatField(null=True, blank=True)

    priority = models.CharField(
        max_length=20,
        choices=PRIORITY_CHOICES,
        default='Medium'
    )

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='Submitted'
    )

    ai_summary = models.TextField(blank=True)

    priority_reason = models.TextField(blank=True)

    assigned_department = models.CharField(
        max_length=100,
        blank=True
    )

    duplicate_of = models.ForeignKey(
        'self',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='duplicate_reports'
    )

    created_at = models.DateTimeField(auto_now_add=True)

    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title
