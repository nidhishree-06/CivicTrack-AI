
import re
import math
from collections import Counter


# 1. Automatic complaint categorization

CATEGORY_KEYWORDS = {
    'Road Damage': [
        'pothole', 'road damage', 'broken road',
        'cracked road', 'damaged road'
    ],
    'Waterlogging': [
        'waterlogging', 'flood', 'flooded',
        'standing water', 'water accumulation'
    ],
    'Garbage': [
        'garbage', 'waste', 'trash', 'rubbish',
        'overflowing bin', 'dump'
    ],
    'Streetlight': [
        'streetlight', 'street light',
        'lamp', 'dark road', 'light not working'
    ],
    'Drainage': [
        'drain', 'sewage', 'blocked drainage',
        'drainage blockage', 'manhole'
    ],
}


def categorize_complaint(text, selected_category):
    text = text.lower()

    for category, keywords in CATEGORY_KEYWORDS.items():
        if any(keyword in text for keyword in keywords):
            return category

    return selected_category


# 2. Complaint summarization

def summarize_complaint(text):
    text = ' '.join(text.split())
    sentences = re.split(r'(?<=[.!?])\s+', text)

    summary = sentences[0] if sentences else text

    if len(summary) > 180:
        summary = summary[:177] + '...'

    return summary


# 3. Explainable priority assignment

def calculate_priority(text):
    text = text.lower()

    critical_keywords = [
        'open manhole', 'accident', 'injury',
        'exposed electric wire', 'electrocution',
        'collapsed building', 'fire'
    ]

    high_keywords = [
        'severe pothole', 'large pothole',
        'heavy flooding', 'overflowing sewage',
        'dangerous road', 'school entrance',
        'hospital entrance', 'blocked main road'
    ]

    medium_keywords = [
        'garbage', 'waste', 'streetlight',
        'waterlogging', 'blocked drain'
    ]

    for keyword in critical_keywords:
        if keyword in text:
            return 'Critical', (
                f"Critical priority because the report mentions "
                f"a serious safety hazard: {keyword}."
            )

    for keyword in high_keywords:
        if keyword in text:
            return 'High', (
                f"High priority because the report mentions "
                f"a potentially dangerous issue: {keyword}."
            )

    for keyword in medium_keywords:
        if keyword in text:
            return 'Medium', (
                f"Medium priority because the report mentions "
                f"a public service or infrastructure problem: {keyword}."
            )

    return 'Low', (
        "Low priority based on the currently recognized keywords. "
        "Manual review may change this assessment."
    )


# 4. Text similarity for duplicate detection

STOPWORDS = {
    'the', 'is', 'a', 'an', 'and', 'of', 'to',
    'in', 'near', 'on', 'for', 'it', 'has',
    'been', 'there', 'are', 'with', 'this',
    'that', 'at', 'my', 'our', 'very'
}


def tokenize(text):
    words = re.findall(r'[a-z]+', text.lower())

    return [
        word for word in words
        if word not in STOPWORDS and len(word) > 2
    ]


def cosine_similarity(text1, text2):
    words1 = tokenize(text1)
    words2 = tokenize(text2)

    if not words1 or not words2:
        return 0.0

    counts1 = Counter(words1)
    counts2 = Counter(words2)

    vocabulary = set(counts1) | set(counts2)

    dot_product = sum(
        counts1[word] * counts2[word]
        for word in vocabulary
    )

    magnitude1 = math.sqrt(
        sum(value ** 2 for value in counts1.values())
    )

    magnitude2 = math.sqrt(
        sum(value ** 2 for value in counts2.values())
    )

    if magnitude1 == 0 or magnitude2 == 0:
        return 0.0

    return dot_product / (magnitude1 * magnitude2)


# 5. Geographic distance calculation

def calculate_distance(lat1, lon1, lat2, lon2):
    earth_radius = 6371000

    lat1 = math.radians(lat1)
    lon1 = math.radians(lon1)
    lat2 = math.radians(lat2)
    lon2 = math.radians(lon2)

    dlat = lat2 - lat1
    dlon = lon2 - lon1

    a = (
        math.sin(dlat / 2) ** 2
        + math.cos(lat1) * math.cos(lat2)
        * math.sin(dlon / 2) ** 2
    )

    c = 2 * math.atan2(
        math.sqrt(a),
        math.sqrt(1 - a)
    )

    return earth_radius * c


# 6. Improved duplicate detection

def detect_duplicate(complaint):
    from .models import Complaint

    candidates = Complaint.objects.filter(
        category=complaint.category
    ).exclude(pk=complaint.pk)

    current_text = (
        complaint.title + ' ' + complaint.description
    )

    current_location = complaint.location.strip().lower()

    best_match = None
    best_score = 0.0
    best_distance = None

    for candidate in candidates:

        candidate_location = candidate.location.strip().lower()

        same_location = (
            current_location == candidate_location
        )

        distance = None

        # Exact location text match
        if same_location:
            pass

        # Otherwise compare geographical coordinates
        elif (
            complaint.latitude is not None
            and complaint.longitude is not None
            and candidate.latitude is not None
            and candidate.longitude is not None
        ):
            distance = calculate_distance(
                complaint.latitude,
                complaint.longitude,
                candidate.latitude,
                candidate.longitude
            )

            if distance > 500:
                continue

        else:
            continue

        existing_text = (
            candidate.title + ' ' + candidate.description
        )

        score = cosine_similarity(
            current_text,
            existing_text
        )

        if score > best_score:
            best_score = score
            best_match = candidate
            best_distance = distance

    # Check similarity threshold
    if best_match and best_score >= 0.30:

        complaint.duplicate_of = best_match

        complaint.save(update_fields=['duplicate_of'])

        if best_distance is not None:
            location_info = (
                f" The reports are approximately "
                f"{best_distance:.0f} metres apart."
            )
        else:
            location_info = (
                " Both reports have the same location name."
            )

        return (
            f"Possible duplicate of complaint "
            f"{best_match.tracking_id} "
            f"(text similarity: {best_score:.0%})."
            f"{location_info}"
        )

    complaint.duplicate_of = None
    complaint.save(update_fields=['duplicate_of'])

    return "No likely duplicate found."


# 7. Automatic department assignment

DEPARTMENT_MAPPING = {
    'Road Damage': 'Road Maintenance Department',
    'Waterlogging': 'Water Management Department',
    'Garbage': 'Sanitation Department',
    'Streetlight': 'Electrical Department',
    'Drainage': 'Drainage Department',
    'Other': 'General Municipal Department',
}


def assign_department(category):
    return DEPARTMENT_MAPPING.get(
        category,
        'General Municipal Department'
    )


# 8. Complete complaint analysis

def analyze_complaint(complaint):
    combined_text = (
        complaint.title + ' ' + complaint.description
    )

    complaint.category = categorize_complaint(
        combined_text,
        complaint.category
    )

    complaint.ai_summary = summarize_complaint(
        complaint.description
    )

    priority, reason = calculate_priority(combined_text)

    complaint.priority = priority
    complaint.priority_reason = reason

    complaint.assigned_department = assign_department(
        complaint.category
    )

    complaint.save()

    duplicate_message = detect_duplicate(complaint)

    return {
        'category': complaint.category,
        'summary': complaint.ai_summary,
        'priority': complaint.priority,
        'priority_reason': complaint.priority_reason,
        'assigned_department': complaint.assigned_department,
        'duplicate_message': duplicate_message
    }
