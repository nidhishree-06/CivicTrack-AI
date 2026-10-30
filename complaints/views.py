
from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.http import require_http_methods
from django.contrib.auth.decorators import login_required

from .models import Complaint
from .ai_engine import analyze_complaint


def home(request):
    return render(request, 'home.html')


@require_http_methods(["GET", "POST"])
def report_complaint(request):

    if request.method == 'POST':

        title = request.POST.get('title', '').strip()
        description = request.POST.get('description', '').strip()
        category = request.POST.get('category', '')
        location = request.POST.get('location', '').strip()

        latitude = request.POST.get('latitude', '').strip()
        longitude = request.POST.get('longitude', '').strip()

        allowed_categories = {
            choice[0] for choice in Complaint.CATEGORY_CHOICES
        }

        if (
            not title or not description or not location
            or category not in allowed_categories
        ):
            return render(request, 'report.html', {
                'error': 'Please fill in all fields correctly.'
            })

        try:
            if not latitude or not longitude:
                raise ValueError

            latitude = float(latitude)
            longitude = float(longitude)

            if not (-90 <= latitude <= 90):
                raise ValueError

            if not (-180 <= longitude <= 180):
                raise ValueError

        except ValueError:
            return render(request, 'report.html', {
                'error': 'Please select a valid location on the map.'
            })

        complaint = Complaint.objects.create(
            title=title,
            description=description,
            category=category,
            location=location,
            latitude=latitude,
            longitude=longitude
        )

        analyze_complaint(complaint)

        return redirect(
            'complaint_success',
            tracking_id=complaint.tracking_id
        )

    return render(request, 'report.html')


def complaint_success(request, tracking_id):

    complaint = get_object_or_404(
        Complaint,
        tracking_id=tracking_id
    )

    return render(request, 'success.html', {
        'complaint': complaint
    })


@login_required(login_url='/admin/login/')
def authority_dashboard(request):

    if request.method == 'POST':

        complaint_id = request.POST.get('complaint_id')

        complaint = get_object_or_404(
            Complaint,
            tracking_id=complaint_id
        )

        new_status = request.POST.get('status')
        new_department = request.POST.get(
            'assigned_department', ''
        ).strip()

        valid_statuses = {
            choice[0] for choice in Complaint.STATUS_CHOICES
        }

        if new_status in valid_statuses:
            complaint.status = new_status

        complaint.assigned_department = new_department
        complaint.save()

        return redirect('authority_dashboard')

    complaints = Complaint.objects.all().order_by('-created_at')

    context = {
        'complaints': complaints,
        'total_complaints': complaints.count(),
        'pending_complaints': complaints.exclude(
            status='Resolved'
        ).count(),
        'high_priority': complaints.filter(
            priority__in=['High', 'Critical']
        ).count(),
        'resolved_complaints': complaints.filter(
            status='Resolved'
        ).count(),
    }

    return render(
        request,
        'dashboard.html',
        context
    )

from uuid import UUID


def track_complaint(request):

    complaint = None
    error = None

    if request.method == 'POST':

        tracking_id = request.POST.get(
            'tracking_id', ''
        ).strip()

        try:
            tracking_id = UUID(tracking_id)

        except (ValueError, TypeError, AttributeError):
            error = "Please enter a valid tracking ID."

        else:
            complaint = Complaint.objects.filter(
                tracking_id=tracking_id
            ).first()

            if complaint is None:
                error = "No complaint found with this tracking ID."

    return render(request, 'track.html', {
        'complaint': complaint,
        'error': error
    })

