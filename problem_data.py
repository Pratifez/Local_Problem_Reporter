"""
=====================================================
      PROBLEM DATA  (settings for the reporter)
=====================================================
This file only stores DATA - no windows or logic.
Edit the lists below to match YOUR school / town!

Both files must be saved in the SAME folder.
"""

# Where the reports are saved (a JSON file is created automatically)
DATA_FILE = "reports.json"

# Types of problems people can report
CATEGORIES = [
    "Garbage / Waste",
    "Road / Pothole",
    "Street Light",
    "Water Supply / Leak",
    "Drainage / Flooding",
    "Air / Noise Pollution",
    "Public Safety",
    "Other",
]

# How urgent is the problem?
PRIORITIES = ["Low", "Medium", "High"]

# Row colors in the table (one per priority)
PRIORITY_COLORS = {
    "Low": "#d4edda",      # light green
    "Medium": "#fff3cd",   # light yellow
    "High": "#f8d7da",     # light red
}

# Status of a report
STATUS_OPEN = "Open"
STATUS_RESOLVED = "Resolved"
