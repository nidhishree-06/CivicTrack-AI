
import math
from collections import Counter
from uuid import UUID

from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.http import require_http_methods
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db.models import Q

from .models import Complaint
from .ai_engine import analyze_complaint


# ==========================================
# GEOGRAPHIC HOTSPOT DETECTION
# ==========================================

def detect_hotspots(complaints, radius=500, minimum_reports=3):

    valid_complaints = [
        complaint for complaint in complaints
        if complaint.latitude is not None
        and complaint.longitude is not None
    ]

    def calculate_distance(first, second):

        earth_radius = 6371000

        lat1 = math.radians(first.latitude)
        lat2 = math.radians(second.latitude)

        delta_lat = math.radians(
            second.latitude - first.latitude
        )

        delta_lon = math.radians(
            second.longitude - first.longitude
        )

        a = (
            math.sin(delta_lat / 2) ** 2
            + math.cos(lat1)
            * math.cos(lat2)
            * math.sin(delta_lon / 2) ** 2
        )

        return earth_radius * 2 * math.atan2(
            math.sqrt(a),
            math.sqrt(1 - a)
        )

    visited = set()
    hotspots = []

    for index, complaint in enumerate(valid_complaints):

        if index in visited:
            continue

        cluster = []
        stack = [index]
        visited.add(index)

        while stack:

            current_index = stack.pop()
            current = valid_complaints[current_index]
            cluster.append(current)

            for other_index, other in enumerate(valid_complaints):

                if other_index in visited:
                    continue

                if calculate_distance(current, other) <= radius:
                    visited.add(other_index)
                    stack.append(other_index)

        if len(cluster) >= minimum_reports:

            categories = Counter(
                item.category for item in cluster
            )

            hotspots.append({
                'count': len(cluster),
                'latitude': sum(
                    item.latitude for item in cluster
                ) / len(cluster),
                'longitude': sum(
                    item.longitude for item in cluster
                ) / len(cluster),
                'common_category': categories.most_common(1)[0][0],
                'complaints': cluster,
            })

    return hotspots


# ==========================================
# HOMEPAGE
# ==========================================

def home(request):
    return render(request, 'home.html')


# ==========================================
# REPORT A COMPLAINT
# ==========================================

@require_http_methods(["GET", "POST"])
def report_complaint(request):

    if request.method == 'POST':

        title = request.POST.get('title', '').strip()
        description = request.POST.get('description', '').strip()
        category = request.POST.get('category', '')
        location = request.POST.get('location', '').strip()

        latitude = request.POST.get('latitude', '').strip()
        longitude = request.POST.get('longitude', '').strip()

        image = request.FILES.get('image')

        allowed_categories = {
            choice[0] for choice in Complaint.CATEGORY_CHOICES
        }

        if (
            not title
            or not description
            or not location
            or category not in allowed_categories
        ):
            return render(request, 'report.html', {
                'error': 'Please fill in all fields correctly.'
            })

        if image:

            if image.size > 5 * 1024 * 1024:
                return render(request, 'report.html', {
                    'error': 'Image size must not exceed 5 MB.'
                })

            allowed_types = [
                'image/jpeg',
                'image/png',
                'image/webp'
            ]

            if image.content_type not in allowed_types:
                return render(request, 'report.html', {
                    'error': 'Please upload a JPG, PNG, or WEBP image.'
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

        except (ValueError, TypeError):

            return render(request, 'report.html', {
                'error': 'Please select a valid location on the map.'
            })

        complaint = Complaint.objects.create(
            title=title,
            description=description,
            category=category,
            location=location,
            latitude=latitude,
            longitude=longitude,
            image=image
        )

        analyze_complaint(complaint)

        return redirect(
            'complaint_success',
            tracking_id=complaint.tracking_id
        )

    return render(request, 'report.html')


# ==========================================
# COMPLAINT SUCCESS PAGE
# ==========================================

def complaint_success(request, tracking_id):

    complaint = get_object_or_404(
        Complaint,
        tracking_id=tracking_id
    )

    return render(request, 'success.html', {
        'complaint': complaint
    })


# ==========================================
# AUTHORITY DASHBOARD
# SEARCH, FILTERS AND PAGINATION
# ==========================================

@login_required(login_url='/admin/login/')
def authority_dashboard(request):

    # Update complaint status and department
    if request.method == 'POST':

        complaint_id = request.POST.get('complaint_id')

        complaint = get_object_or_404(
            Complaint,
            tracking_id=complaint_id
        )

        new_status = request.POST.get('status')

        new_department = request.POST.get(
            'assigned_department',
            ''
        ).strip()

        valid_statuses = {
            choice[0] for choice in Complaint.STATUS_CHOICES
        }

        if new_status in valid_statuses:
            complaint.status = new_status

        complaint.assigned_department = new_department
        complaint.save()

        return redirect('authority_dashboard')

    # Get all complaints for dashboard statistics
    all_complaints = Complaint.objects.all().order_by('-created_at')

    # Read search and filter values
    search_query = request.GET.get('search', '').strip()
    selected_category = request.GET.get('category', '')
    selected_priority = request.GET.get('priority', '')
    selected_status = request.GET.get('status', '')

    # Start with all complaints
    filtered_complaints = all_complaints

    # Search by title, description, location or tracking ID
    if search_query:

        filtered_complaints = filtered_complaints.filter(
            Q(title__icontains=search_query)
            | Q(description__icontains=search_query)
            | Q(location__icontains=search_query)
            | Q(tracking_id__icontains=search_query)
        )

    # Validate and apply category filter
    valid_categories = {
        choice[0] for choice in Complaint.CATEGORY_CHOICES
    }

    if selected_category in valid_categories:

        filtered_complaints = filtered_complaints.filter(
            category=selected_category
        )

    elif selected_category:
        selected_category = ''

    # Validate and apply priority filter
    valid_priorities = {
        choice[0] for choice in Complaint.PRIORITY_CHOICES
    }

    if selected_priority in valid_priorities:

        filtered_complaints = filtered_complaints.filter(
            priority=selected_priority
        )

    elif selected_priority:
        selected_priority = ''

    # Validate and apply status filter
    valid_statuses = {
        choice[0] for choice in Complaint.STATUS_CHOICES
    }

    if selected_status in valid_statuses:

        filtered_complaints = filtered_complaints.filter(
            status=selected_status
        )

    elif selected_status:
        selected_status = ''

    # Keep all filtered complaints for map and hotspot analysis
    map_complaints = list(filtered_complaints)

    hotspots = detect_hotspots(map_complaints)

    # Paginate the complaint table
    paginator = Paginator(map_complaints, 10)

    page_number = request.GET.get('page')

    page_obj = paginator.get_page(page_number)

    # Dashboard statistics always use all complaints
    context = {

        'complaints': page_obj,
        'page_obj': page_obj,

        'map_complaints': map_complaints,
        'hotspots': hotspots,

        'total_complaints': all_complaints.count(),

        'pending_complaints': all_complaints.exclude(
            status='Resolved'
        ).count(),

        'high_priority': all_complaints.filter(
            priority__in=['High', 'Critical']
        ).count(),

        'resolved_complaints': all_complaints.filter(
            status='Resolved'
        ).count(),

        # Search and filter values
        'search_query': search_query,
        'selected_category': selected_category,
        'selected_priority': selected_priority,
        'selected_status': selected_status,

        # Dropdown choices
        'category_choices': Complaint.CATEGORY_CHOICES,
        'priority_choices': Complaint.PRIORITY_CHOICES,
        'status_choices': Complaint.STATUS_CHOICES,
    }

    return render(
        request,
        'dashboard.html',
        context
    )


# ==========================================
# CITIZEN COMPLAINT TRACKING
# ==========================================

def track_complaint(request):

    complaint = None
    error = None

    if request.method == 'POST':

        tracking_id = request.POST.get(
            'tracking_id',
            ''
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
