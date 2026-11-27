"""
=====================================================
      LOCAL PROBLEM REPORTER  (Tkinter + JSON)
=====================================================
Report problems in your community (garbage, potholes,
broken street lights...), save them to a file, filter
them, view a category chart, and mark them as resolved.

FILES:  problem_reporter.py (this file - the program)
        problem_data.py     (categories, priorities, colors)
        reports.json        (created automatically to save reports)

tkinter and json come with Python - nothing to install.
"""

import json
import os
from datetime import datetime
import tkinter as tk
from tkinter import ttk, messagebox

# Our own data file - must be in the same folder

from problem_data import (DATA_FILE, CATEGORIES, PRIORITIES,
                          PRIORITY_COLORS, STATUS_OPEN, STATUS_RESOLVED)

# Print-friendly theme: restrained navy + teal with soft neutral surfaces
BG = "#F3F6F8"
SURFACE = "#FFFFFF"
NAVY = "#17324D"
TEAL = "#087E8B"
TEAL_DARK = "#06636D"
TEXT = "#263746"
MUTED = "#647583"
BORDER = "#D5DEE5"
SOFT_BLUE = "#EAF2F7"
SOFT_RED = "#FCE8E6"
SOFT_AMBER = "#FFF2D8"
SOFT_GREEN = "#E5F3EA"


# =====================================================
# PART 1: DATA FUNCTIONS (no windows here - just logic)
# =====================================================
def load_reports():
    """Read all saved reports from the JSON file."""
    if not os.path.exists(DATA_FILE):
        return []                       # first time: no file yet
    try:
        with open(DATA_FILE, "r", encoding="utf-8") as file:
            return json.load(file)
    except (json.JSONDecodeError, OSError):
        return []                       # damaged file: start fresh


def save_reports(reports):
    """Write all reports to the JSON file."""
    with open(DATA_FILE, "w", encoding="utf-8") as file:
        json.dump(reports, file, indent=2, ensure_ascii=False)


def add_report(reports, title, category, location, priority, description):
    """Create a new report (a dictionary) and add it to the list."""
    # New id = biggest id so far + 1
    new_id = max([r["id"] for r in reports], default=0) + 1

    report = {
        "id": new_id,
        "date": datetime.now().strftime("%Y-%m-%d %H:%M"),
        "title": title,
        "category": category,
        "location": location,
        "priority": priority,
        "description": description,
        "status": STATUS_OPEN,
    }
    reports.append(report)
    return report


def count_stats(reports):
    """Return (total, open, resolved) counts."""
    total = len(reports)
    resolved = len([r for r in reports if r["status"] == STATUS_RESOLVED])
    return total, total - resolved, resolved


def filter_reports(reports, category, status):
    """Keep only reports that match the chosen filters ('All' = no filter)."""
    result = []
    for report in reports:
        if category != "All" and report["category"] != category:
            continue
        if status != "All" and report["status"] != status:
            continue
        result.append(report)
    return result


# =====================================================
# PART 2: THE WINDOW
# =====================================================
class ProblemReporter:
    def __init__(self, window):
        self.window = window
        window.title("📍 Local Problem Reporter")
        window.geometry("900x700")
        window.minsize(820, 640)
        window.configure(bg=BG)

        style = ttk.Style()
        style.theme_use("clam")
        style.configure("TCombobox", fieldbackground=SURFACE,
                        background=SURFACE, foreground=TEXT,
                        bordercolor=BORDER, arrowcolor=NAVY, padding=4)
        style.map("TCombobox", fieldbackground=[("readonly", SURFACE)],
                  foreground=[("readonly", TEXT)])
        style.configure("Treeview", background=SURFACE, foreground=TEXT,
                        fieldbackground=SURFACE, rowheight=27,
                        bordercolor=BORDER, font=("Arial", 9))
        style.configure("Treeview.Heading", background=NAVY, foreground="white",
                        font=("Arial", 9, "bold"), padding=7)
        style.map(
        "Treeview.Heading",
         background=[("active", NAVY)],
         foreground=[("active", "white")]
)

        self.reports = load_reports()       # load saved reports
        self.chart_window = None
        self.chart_canvas = None

        self.build_form()
        self.build_table()
        self.refresh_table()

    # ---------- The form at the top ----------
    def build_form(self):
        tk.Label(self.window, text="📍 Local Problem Reporter",
                 font=("Arial", 19, "bold"), bg=BG, fg=NAVY).pack(pady=(12, 2))
        tk.Label(self.window, text="Report a problem in your community. Fill the form and click Submit.",
                 font=("Arial", 10), bg=BG, fg=MUTED).pack()

        form = tk.LabelFrame(self.window, text="  Report a new problem  ",
                             font=("Arial", 11, "bold"), padx=12, pady=10,
                             bg=SURFACE, fg=TEAL, bd=1, relief="solid",
                             highlightthickness=0)
        form.pack(fill="x", padx=15, pady=12)

        # Title
        tk.Label(form, text="Title *:", bg=SURFACE, fg=TEXT).grid(row=0, column=0, sticky="w")
        self.title_var = tk.StringVar()
        tk.Entry(form, textvariable=self.title_var, width=35, bg="#FBFCFD", fg=TEXT, insertbackground=TEXT, relief="solid", bd=1).grid(row=0, column=1, pady=3, sticky="w")

        # Category (drop-down list)
        tk.Label(form, text="Category *:", bg=SURFACE, fg=TEXT).grid(row=0, column=2, sticky="w", padx=(20, 0))
        self.category_var = tk.StringVar()
        ttk.Combobox(form, textvariable=self.category_var, values=CATEGORIES,
                     state="readonly", width=22).grid(row=0, column=3, sticky="w")

        # Location
        tk.Label(form, text="Location *:", bg=SURFACE, fg=TEXT).grid(row=1, column=0, sticky="w")
        self.location_var = tk.StringVar()
        tk.Entry(form, textvariable=self.location_var, width=35, bg="#FBFCFD", fg=TEXT, insertbackground=TEXT, relief="solid", bd=1).grid(row=1, column=1, pady=3, sticky="w")

        # Priority (radio buttons - pick only one)
        tk.Label(form, text="Priority:", bg=SURFACE, fg=TEXT).grid(row=1, column=2, sticky="w", padx=(20, 0))
        self.priority_var = tk.StringVar(value=PRIORITIES[0])
        priority_frame = tk.Frame(form, bg=SURFACE)
        priority_frame.grid(row=1, column=3, sticky="w")
        for level in PRIORITIES:
            tk.Radiobutton(priority_frame, text=level, value=level,
                           variable=self.priority_var, bg=SURFACE, fg=TEXT, activebackground=SURFACE, selectcolor=SOFT_BLUE).pack(side="left")

        # Description (multi-line box)
        tk.Label(form, text="Details:", bg=SURFACE, fg=TEXT).grid(row=2, column=0, sticky="nw")
        self.description_box = tk.Text(form, height=4, width=70, bg="#FBFCFD", fg=TEXT, insertbackground=TEXT, relief="solid", bd=1, highlightthickness=1, highlightbackground=BORDER)
        self.description_box.grid(row=2, column=1, columnspan=3, pady=3, sticky="w")

        tk.Label(form, text="* required fields", font=("Arial", 8), bg=SURFACE, fg=MUTED).grid(row=3, column=0, sticky="w")
        # Submit button
        tk.Button(form, text="  Submit Report  ", font=("Arial", 10, "bold"),
                  bg=TEAL, fg="white", activebackground=TEAL_DARK,
                  activeforeground="white", relief="flat", bd=0,
                  padx=10, pady=6, cursor="hand2",
                  command=self.submit_report).grid(row=3, column=1, pady=8, sticky="w")

    # ---------- The table of reports ----------
    def build_table(self):
        # Filters
        filter_frame = tk.Frame(self.window, bg=BG)
        filter_frame.pack(fill="x", padx=15)

        tk.Label(filter_frame, text="Show category:", bg=BG, fg=TEXT, font=("Arial", 9, "bold")).pack(side="left")
        self.filter_category = tk.StringVar(value="All")
        box1 = ttk.Combobox(filter_frame, textvariable=self.filter_category,
                            values=["All"] + CATEGORIES, state="readonly", width=20)
        box1.pack(side="left", padx=5)

        tk.Label(filter_frame, text="Status:", bg=BG, fg=TEXT, font=("Arial", 9, "bold")).pack(side="left", padx=(15, 0))
        self.filter_status = tk.StringVar(value="All")
        box2 = ttk.Combobox(filter_frame, textvariable=self.filter_status,
                            values=["All", STATUS_OPEN, STATUS_RESOLVED],
                            state="readonly", width=10)
        box2.pack(side="left", padx=5)

        # Refresh the table whenever a filter changes
        box1.bind("<<ComboboxSelected>>", self.refresh_table)
        box2.bind("<<ComboboxSelected>>", self.refresh_table)

        # Table (Treeview)
        columns = ("id", "date", "title", "category", "location", "priority", "status")
        self.table = ttk.Treeview(self.window, columns=columns, show="headings", height=10)
        widths = (35, 110, 170, 130, 130, 65, 70)
        for name, width in zip(columns, widths):
            self.table.heading(name, text=name.capitalize())
            self.table.column(name, width=width)
        self.table.pack(fill="both", expand=True, padx=15, pady=8)

        # Color each row by priority
        priority_row_colors = {
            "High": SOFT_RED,
            "Medium": SOFT_AMBER,
            "Low": SOFT_GREEN,
        }
        for level in PRIORITIES:
            self.table.tag_configure(
                level, background=priority_row_colors.get(level, SOFT_BLUE),
                foreground=TEXT
            )

        # Double-click a row to read the full details
        self.table.bind("<Double-1>", self.show_details)

        # Buttons
        button_frame = tk.Frame(self.window, bg=BG)
        button_frame.pack(pady=(0, 5))
        button_specs = [
            ("View Details", self.show_details, NAVY),
            ("Mark Resolved", self.mark_resolved, TEAL),
            ("Delete", self.delete_report, "#A64B45"),
            ("View Chart", self.show_chart, "#526B83"),
        ]
        for label, command, color in button_specs:
            tk.Button(button_frame, text=f"  {label}  ", command=command,
                      bg=color, fg="white", activebackground=color,
                      activeforeground="white", relief="flat", bd=0,
                      padx=7, pady=5, cursor="hand2").pack(side="left", padx=5)

        # Statistics line
        self.stats_label = tk.Label(self.window, font=("Arial", 11, "bold"),
                                    bg=BG, fg=NAVY)
        self.stats_label.pack(pady=(0, 10))

    # ---------- Actions ----------
    def submit_report(self):
        title = self.title_var.get().strip()
        location = self.location_var.get().strip()
        category = self.category_var.get()
        description = self.description_box.get("1.0", "end").strip()

        # Check that the important boxes are filled in
        if title == "" or location == "" or category == "":
            messagebox.showwarning("Missing info", "Please fill in the title, category and location.")
            return

        add_report(self.reports, title, category, location,
                   self.priority_var.get(), description)
        save_reports(self.reports)

        # Clear the form for the next report
        self.title_var.set("")
        self.location_var.set("")
        self.category_var.set("")
        self.description_box.delete("1.0", "end")

        self.refresh_table()
        messagebox.showinfo("Thank you!", "Your report has been saved.")

    def get_selected_report(self):
        """Return the report dictionary for the selected table row (or None)."""
        selected = self.table.selection()
        if not selected:
            messagebox.showinfo("Select a report", "Click a report in the table first.")
            return None
        report_id = int(self.table.item(selected[0])["values"][0])
        for report in self.reports:
            if report["id"] == report_id:
                return report

    def show_details(self, event=None):
        report = self.get_selected_report()
        if report:
            text = (f"Title: {report['title']}\n"
                    f"Category: {report['category']}\n"
                    f"Location: {report['location']}\n"
                    f"Priority: {report['priority']}\n"
                    f"Reported: {report['date']}\n"
                    f"Status: {report['status']}\n\n"
                    f"Details:\n{report['description'] or '(none)'}")
            messagebox.showinfo(f"Report #{report['id']}", text)

    def mark_resolved(self):
        report = self.get_selected_report()
        if report:
            report["status"] = STATUS_RESOLVED
            save_reports(self.reports)
            self.refresh_table()

    def delete_report(self):
        report = self.get_selected_report()
        if report and messagebox.askyesno("Delete", f"Delete report '{report['title']}'?"):
            self.reports.remove(report)
            save_reports(self.reports)
            self.refresh_table()

    # ---------- Redraw the table and statistics ----------
    def refresh_table(self, event=None):
        # Remove all old rows
        for row in self.table.get_children():
            self.table.delete(row)

        # Add the rows that match the filters (newest first)
        shown = filter_reports(self.reports, self.filter_category.get(), self.filter_status.get())
        for r in reversed(shown):
            self.table.insert("", "end", tags=(r["priority"],),
                              values=(r["id"], r["date"], r["title"], r["category"],
                                      r["location"], r["priority"], r["status"]))

        total, open_count, resolved = count_stats(self.reports)
        self.stats_label.config(
            text=f"📊 Total: {total}   |   🔴 Open: {open_count}   |   🟢 Resolved: {resolved}")

        if self.chart_canvas is not None and self.chart_canvas.winfo_exists():
            self.draw_chart(self.chart_canvas)

    def show_chart(self):
        if self.chart_window is not None and self.chart_window.winfo_exists():
            self.chart_window.lift()
            self.draw_chart(self.chart_canvas)
            return

        self.chart_window = tk.Toplevel(self.window)
        self.chart_window.title("Community Report Insights")
        self.chart_window.geometry("980x720")
        self.chart_window.minsize(780, 620)
        self.chart_window.configure(bg=BG)

        self.chart_canvas = tk.Canvas(
            self.chart_window, background=BG, highlightthickness=0
        )
        self.chart_canvas.pack(fill="both", expand=True, padx=12, pady=12)
        self.chart_canvas.bind(
            "<Configure>", lambda event: self.draw_chart(self.chart_canvas)
        )
        self.chart_window.protocol("WM_DELETE_WINDOW", self.close_chart)
        self.draw_chart(self.chart_canvas)

    def close_chart(self):
        if self.chart_window is not None:
            self.chart_window.destroy()
        self.chart_window = None
        self.chart_canvas = None

    def draw_chart(self, canvas):
        canvas.delete("all")
        width = canvas.winfo_width()
        height = canvas.winfo_height()
        if width < 100 or height < 100:
            return

        background = BG
        card = SURFACE
        border = BORDER
        text = NAVY
        muted = MUTED
        open_color = "#C65B52"
        resolved_color = TEAL
        accent = TEAL
        margin = 24
        right = width - margin

        canvas.configure(background=background)
        canvas.create_text(
            margin, 18, anchor="nw", text="COMMUNITY REPORT ANALYTICS",
            font=("Arial", 9, "bold"), fill=accent
        )
        canvas.create_text(
            margin, 39, anchor="nw", text="A clearer view of local issues",
            font=("Arial", 20, "bold"), fill=text
        )
        canvas.create_text(
            margin, 69, anchor="nw", text="Live overview • updated from your saved reports",
            font=("Arial", 10), fill=muted
        )

        total, open_count, resolved_count = count_stats(self.reports)
        high_open_count = sum(
            1 for report in self.reports
            if report.get("priority") == "High" and report.get("status") == STATUS_OPEN
        )
        card_top = 104
        card_bottom = 184
        gap = 12
        card_width = (width - 2 * margin - 2 * gap) / 3
        kpis = (
            ("TOTAL REPORTS", total, accent),
            ("OPEN REPORTS", open_count, open_color),
            ("RESOLVED", resolved_count, resolved_color),
        )
        for index, (label, value, color) in enumerate(kpis):
            x = margin + index * (card_width + gap)
            canvas.create_rectangle(
                x, card_top, x + card_width, card_bottom,
                fill=card, outline=border
            )
            canvas.create_rectangle(
                x + 14, card_top + 14, x + 17, card_bottom - 14,
                fill=color, outline=""
            )
            canvas.create_text(
                x + 28, card_top + 17, anchor="nw", text=label,
                font=("Arial", 8, "bold"), fill=muted
            )
            canvas.create_text(
                x + 28, card_top + 36, anchor="nw", text=str(value),
                font=("Arial", 20, "bold"), fill=text
            )

        graph_top = 198
        insight_top = height - 78
        graph_bottom = insight_top - 12
        canvas.create_rectangle(
            margin, graph_top, right, graph_bottom,
            fill=card, outline=border
        )
        graph_left = margin + 18
        graph_right = right - 18
        canvas.create_text(
            graph_left, graph_top + 16, anchor="nw",
            text="Issue mix", font=("Arial", 13, "bold"), fill=text
        )
        canvas.create_text(
            graph_left, graph_top + 40, anchor="nw",
            text="Reports by category, split by status",
            font=("Arial", 9), fill=muted
        )
        legend_y = graph_top + 23
        canvas.create_rectangle(
            graph_right - 158, legend_y, graph_right - 146, legend_y + 12,
            fill=open_color, outline=""
        )
        canvas.create_text(
            graph_right - 140, legend_y + 6, anchor="w",
            text=STATUS_OPEN, font=("Arial", 9), fill=muted
        )
        canvas.create_rectangle(
            graph_right - 76, legend_y, graph_right - 64, legend_y + 12,
            fill=resolved_color, outline=""
        )
        canvas.create_text(
            graph_right - 58, legend_y + 6, anchor="w",
            text=STATUS_RESOLVED, font=("Arial", 9), fill=muted
        )

        if self.reports:
            categories = list(CATEGORIES)
            for report in self.reports:
                category = report.get("category", "Other")
                if category not in categories:
                    categories.append(category)

            counts = {}
            for category in categories:
                matching = [
                    report for report in self.reports
                    if report.get("category") == category
                ]
                resolved = sum(
                    1 for report in matching
                    if report.get("status") == STATUS_RESOLVED
                )
                counts[category] = (len(matching) - resolved, resolved)

            categories.sort(
                key=lambda category: sum(counts[category]), reverse=True
            )
            max_count = max(sum(values) for values in counts.values())
            bar_x = graph_left + 206
            bar_right = graph_right - 34
            bar_width = max(30, bar_right - bar_x)
            rows_top = graph_top + 91
            rows_bottom = graph_bottom - 22
            row_height = max(
                20, min(30, (rows_bottom - rows_top) / len(categories))
            )
            bar_height = 12

            for tick in sorted(set(
                int(round(max_count * step / 4)) for step in range(5)
            )):
                tick_x = bar_x + bar_width * tick / max_count
                canvas.create_line(
                    tick_x, rows_top - 7,
                    tick_x, rows_top + row_height * len(categories) - 5,
                    fill=border, dash=(2, 4)
                )
                canvas.create_text(
                    tick_x, rows_top - 13, anchor="s",
                    text=str(tick), font=("Arial", 8), fill=muted
                )

            for index, category in enumerate(categories):
                y = rows_top + index * row_height
                open_value, resolved_value = counts[category]
                open_width = bar_width * open_value / max_count
                resolved_width = bar_width * resolved_value / max_count
                total_for_category = open_value + resolved_value
                canvas.create_text(
                    graph_left, y + bar_height / 2, anchor="w",
                    text=category, font=("Arial", 9), fill=text
                )
                canvas.create_rectangle(
                    bar_x, y, bar_right, y + bar_height,
                    fill="#E5EBEF", outline=""
                )
                if open_width:
                    canvas.create_rectangle(
                        bar_x, y, bar_x + open_width, y + bar_height,
                        fill=open_color, outline=""
                    )
                if resolved_width:
                    canvas.create_rectangle(
                        bar_x + open_width, y,
                        bar_x + open_width + resolved_width, y + bar_height,
                        fill=resolved_color, outline=""
                    )
                canvas.create_text(
                    min(bar_x + open_width + resolved_width + 7, width - 18),
                    y + bar_height / 2, anchor="w",
                    text=str(total_for_category),
                    font=("Arial", 9, "bold"), fill=muted
                )
        else:
            canvas.create_text(
                width / 2, (graph_top + graph_bottom) / 2,
                text="Add a few reports to see category patterns here.",
                font=("Arial", 11), fill=muted
            )

        canvas.create_rectangle(
            margin, insight_top, right, height - 18,
            fill=SOFT_BLUE, outline=BORDER
        )
        canvas.create_text(
            margin + 16, insight_top + 13, anchor="nw",
            text="LOCAL SMART INSIGHT", font=("Arial", 8, "bold"), fill=accent
        )
        if self.reports:
            top_category = max(
                counts, key=lambda category: sum(counts[category])
            )
            top_count = sum(counts[top_category])
            insight = f"Most reported: {top_category} ({top_count}). "
            if high_open_count:
                insight += (
                    f"{high_open_count} high-priority open "
                    f"{'report needs' if high_open_count == 1 else 'reports need'} attention."
                )
            else:
                insight += "No high-priority open reports right now."
        else:
            insight = "A simple, explainable pattern summary will appear once reports are added."
        canvas.create_text(
            margin + 174, insight_top + 13, anchor="nw", width=right - margin - 192,
            text=insight, font=("Arial", 9), fill=text
        )


# =====================================================
# MAIN PROGRAM
# =====================================================
if __name__ == "__main__":
    root = tk.Tk()
    ProblemReporter(root)
    root.mainloop()





