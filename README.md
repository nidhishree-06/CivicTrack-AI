
# CivicTrack AI
### From Complaints to Action

CivicTrack AI is a web-based civic complaint management platform that helps citizens report public issues and helps authorities understand, prioritize, and manage complaints efficiently.

The platform processes citizen reports using rule-based AI techniques to categorize complaints, generate summaries, identify possible duplicate reports, assign priorities, and detect geographic hotspots.

## Problem Statement

Communities frequently experience public issues such as damaged roads, waterlogging, overflowing garbage bins, broken streetlights, and drainage problems.

These complaints often reach authorities through different channels. Duplicate reports, unclear priorities, and limited progress tracking make complaint management difficult.

CivicTrack AI aims to organize these reports into a structured system that supports faster review and transparent complaint tracking.

## Features

### 1. Citizen Complaint Submission
- Submit complaints with a title and description.
- Select a complaint category.
- Provide location using an interactive map.
- Upload supporting images.
- Receive a unique tracking ID.

### 2. AI-Based Complaint Analysis
- Automatic complaint categorization.
- Short summary generation.
- Priority assignment based on urgency-related keywords.
- Explainable priority reasons.
- Possible duplicate complaint detection using text similarity.
- Automatic department assignment.

### 3. Geographic Hotspot Detection
- Displays complaint locations on an interactive map.
- Identifies geographic clusters of complaints.
- Displays potential hotspots based on nearby reports.
- Helps authorities identify recurring local problems.

### 4. Authority Dashboard
- Displays complaint statistics.
- Provides complaint management facilities.
- Allows authorities to update complaint status and assigned department.
- Displays complaint evidence images.
- Shows possible duplicate reports.

### 5. Citizen Complaint Tracking
- Citizens can track complaints using their tracking ID.
- Displays the current complaint status.
- Provides a visual complaint progress timeline.

## Technologies Used

| Technology | Purpose |
|---|---|
| Python | Backend programming |
| Django | Web framework |
| HTML | Page structure |
| CSS | Styling |
| JavaScript | Interactive functionality |
| SQLite | Database |
| Leaflet.js | Interactive maps |
| OpenStreetMap | Map data |
| Pillow | Image processing |

## AI Implementation

CivicTrack AI uses lightweight, explainable AI techniques.

### Complaint Categorization
Uses predefined keywords to identify complaint categories such as road damage, waterlogging, garbage, streetlights, and drainage.

### Complaint Summarization
Generates a concise summary from the submitted complaint description.

### Priority Assignment
Uses urgency-related keywords and predefined rules to assign Critical, High, Medium, or Low priority.

### Duplicate Detection
Uses text tokenization and cosine similarity to identify potentially similar complaints. Geographic distance and location information are also considered.

### Hotspot Detection
Uses geographic coordinates and distance calculations to identify areas with multiple nearby complaints.

These methods are suitable for a prototype. They do not use a trained deep-learning model or a live external AI service.

## Project Structure

```text
CivicTrack-AI/
│
├── civictrack/
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
│
├── complaints/
│   ├── management/
│   │   └── commands/
│   │       └── load_sample_data.py
│   │
│   ├── migrations/
│   ├── static/
│   │   └── complaints/
│   │       └── style.css
│   │
│   ├── templates/
│   │   ├── base.html
│   │   ├── home.html
│   │   ├── report.html
│   │   ├── success.html
│   │   ├── track.html
│   │   └── dashboard.html
│   │
│   ├── ai_engine.py
│   ├── models.py
│   ├── urls.py
│   └── views.py
│
├── manage.py
├── requirements.txt
├── .gitignore
└── README.md
```

## Installation and Setup

### 1. Clone the repository

```bash
git clone https://github.com/nidhishree-06/CivicTrack-AI.git
```

### 2. Open the project folder

```bash
cd CivicTrack-AI
```

### 3. Create a virtual environment

```bash
python -m venv .venv
```

### 4. Activate the virtual environment

For Windows PowerShell:

```powershell
.venv\Scripts\Activate.ps1
```

### 5. Install dependencies

```bash
pip install -r requirements.txt
```

### 6. Apply database migrations

```bash
python manage.py migrate
```

### 7. Load synthetic sample complaints

```bash
python manage.py load_sample_data
```

### 8. Start the development server

```bash
python manage.py runserver
```

Open the following address in your browser:

http://127.0.0.1:8000/

## Limitations and Honesty Note

- Complaint categorization and priority assignment use predefined rules and keywords.
- Duplicate detection uses text similarity and geographic information. It may produce false matches or miss genuine duplicates.
- Hotspot detection depends on the availability and accuracy of complaint coordinates.
- Complaint summaries are generated using the implemented text-processing logic.
- The prototype does not connect to live municipal systems or automatically dispatch field workers.
- Synthetic sample data is used for demonstration.
- The platform is a prototype and has not been deployed for real-world civic administration.

## Future Improvements

- Integration with trained machine-learning and language models.
- Improved semantic duplicate detection.
- Real-time municipal authority integration.
- Notifications for complaint status updates.
- More advanced geographic analysis and reporting.

## Conclusion

CivicTrack AI provides a structured approach to civic complaint management by combining citizen reporting, explainable complaint analysis, geographic hotspot detection, authority-side management, and citizen tracking.

The goal is to help transform scattered civic complaints into organized and actionable information.

---

**Project:** CivicTrack AI  
**Repository:** https://github.com/nidhishree-06/CivicTrack-AI
```

## Step 2: Save and upload

1. Press `Ctrl + S`.
2. Open the VS Code terminal.
3. Run:

```powershell
git add README.md
git commit -m "Add project documentation"
git push origin main
```

<badge color="success">README preparation</badge>

**One important check:** This README assumes `requirements.txt` already exists in your project root. If it doesn't, tell me before pushing. We should create it with your actual dependencies.