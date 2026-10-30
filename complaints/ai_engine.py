
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

    documents = [set(words1), set(words2)]

    vocabulary = set(words1) | set(words2)

    vectors = []

    for words in [words1, words2]:

        counts = Counter(words)
        vector = {}

        for term in vocabulary:

            document_frequency = sum(
                term in document for document in documents
            )

            idf = math.log(
                3 / (1 + document_frequency)
            ) + 1

            tf = counts[term] / len(words)

            vector[term] = tf * idf

        vectors.append(vector)

    dot_product = sum(
        vectors[0][term] * vectors[1][term]
        for term in vocabulary
    )

    magnitude1 = math.sqrt(
        sum(value ** 2 for value in vectors[0].values())
    )

    magnitude2 = math.sqrt(
        sum(value ** 2 for value in vectors[1].values())
    )

    if magnitude1 == 0 or magnitude2 == 0:
        return 0.0

    return dot_product / (magnitude1 * magnitude2)


def detect_duplicate(complaint):

    from .models import Complaint

    current_location = complaint.location.strip().lower()

    current_text = (
        complaint.title + ' ' + complaint.description
    )

    candidates = Complaint.objects.filter(
        category=complaint.category
    ).exclude(pk=complaint.pk)

    best_match = None
    best_score = 0.0

    for candidate in candidates:

        if candidate.location.strip().lower() != current_location:
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

    if best_match and best_score >= 0.40:

        complaint.duplicate_of = best_match

        complaint.save(update_fields=['duplicate_of'])

        return (
            f"Possible duplicate of complaint "
            f"{best_match.tracking_id} "
            f"(similarity: {best_score:.0%})."
        )

    return "No likely duplicate found."


# 5. Automatic department assignment

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

# 5. Run the complete analysis

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

    complaint.save()

    duplicate_message = detect_duplicate(complaint)

    return {
        'category': complaint.category,
        'summary': complaint.ai_summary,
        'priority': complaint.priority,
        'priority_reason': complaint.priority_reason,
        'duplicate_message': duplicate_message
    }

# 6. Run the complete analysis

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

    # Automatically suggest department
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

