import tkinter as tk
from tkinter import messagebox
import sqlite3
from datetime import datetime
from fpdf import FPDF
import os

# === Setup DB ===
conn = sqlite3.connect('db.sqlite3')
cursor = conn.cursor()

cursor.execute('''
    CREATE TABLE IF NOT EXISTS students (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT,
        program TEXT,
        advance_fee INTEGER,
        remaining_fee INTEGER,
        created_at TEXT
    )
''')
conn.commit()

# === Static Info ===
company_name = "AMZ Student Consultant"   # Your fixed company name here
developer_name = "Developed by Daniyal Kazmi"       # Your name here

# === GUI Setup ===
window = tk.Tk()
window.title("Slip Book Software")
window.geometry("500x700")

# === Company Name Header (Watermark Style) ===
tk.Label(window, text=company_name, font=('Arial', 16, 'bold'), fg='gray').pack(pady=10)

# === Student Form ===
tk.Label(window, text="Student Name").pack()
entry_name = tk.Entry(window, width=40)
entry_name.pack(pady=5)

tk.Label(window, text="Program Applied For").pack()
entry_program = tk.Entry(window, width=40)
entry_program.pack(pady=5)

tk.Label(window, text="Advance Fee Paid").pack()
entry_advance = tk.Entry(window, width=40)
entry_advance.pack(pady=5)

tk.Label(window, text="Remaining Fee (After Visa)").pack()
entry_remaining = tk.Entry(window, width=40)
entry_remaining.pack(pady=5)

# === Save Function ===
def save_student():
    name = entry_name.get()
    program = entry_program.get()
    advance = entry_advance.get()
    remaining = entry_remaining.get()

    if not (name and program and advance and remaining):
        messagebox.showerror("Error", "Please fill all fields.")
        return

    try:
        advance = int(advance)
        remaining = int(remaining)
    except ValueError:
        messagebox.showerror("Error", "Fee must be numeric.")
        return

    created_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    cursor.execute('''
        INSERT INTO students (name, program, advance_fee, remaining_fee, created_at)
        VALUES (?, ?, ?, ?, ?)
    ''', (name, program, advance, remaining, created_at))
    conn.commit()

    messagebox.showinfo("Saved", f"Student '{name}' saved.\nDate: {created_at}")

    entry_name.delete(0, tk.END)
    entry_program.delete(0, tk.END)
    entry_advance.delete(0, tk.END)
    entry_remaining.delete(0, tk.END)

# === PDF Slip Generator ===
def generate_slip():
    selected_name = student_var.get()
    if not selected_name:
        messagebox.showerror("Error", "Select a student to generate slip.")
        return

    cursor.execute("SELECT * FROM students WHERE name = ?", (selected_name,))
    student = cursor.fetchone()
    if not student:
        messagebox.showerror("Error", "Student not found.")
        return

    id, name, program, advance_fee, remaining_fee, created_at = student
    date_str = created_at.split()[0]
    filename = f"slip_{name.replace(' ', '')}_{date_str}.pdf"

    pdf = FPDF()
    pdf.add_page()

    # Optional: Add logo if available
    if os.path.exists("logo.png"):
        pdf.image("logo.png", x=10, y=8, w=30)

    pdf.set_font("Arial", 'B', 16)
    pdf.cell(200, 10, company_name, ln=True, align='C')
    pdf.ln(20)

    pdf.set_font("Arial", size=12)
    pdf.cell(100, 10, f"Student Name: {name}", ln=True)
    pdf.cell(100, 10, f"Program: {program}", ln=True)
    pdf.cell(100, 10, f"Advance Fee Paid: Rs. {advance_fee}", ln=True)
    pdf.cell(100, 10, f"Remaining Fee: Rs. {remaining_fee}", ln=True)
    pdf.cell(100, 10, f"Date: {created_at}", ln=True)
    pdf.ln(30)

    pdf.set_font("Arial", 'I', 8)
    pdf.set_text_color(150)
    pdf.cell(0, 10, developer_name, align='C')

    pdf.output(filename)
    messagebox.showinfo("Slip Created", f"Slip saved as:\n{filename}")

# === Monthly Report Generator ===
def generate_monthly_report():
    now = datetime.now()
    current_month = now.strftime("%Y-%m")

    cursor.execute('''
        SELECT name, program, advance_fee, remaining_fee, created_at 
        FROM students 
        WHERE strftime('%Y-%m', created_at) = ?
    ''', (current_month,))
    rows = cursor.fetchall()

    if not rows:
        messagebox.showinfo("No Data", "No students found for this month.")
        return

    total_students = len(rows)
    total_advance = sum(row[2] for row in rows)
    total_remaining = sum(row[3] for row in rows)

    pdf = FPDF()
    pdf.add_page()
    if os.path.exists("logo.png"):
        pdf.image("logo.png", x=10, y=8, w=30)

    pdf.set_font("Arial", "B", 14)
    pdf.cell(200, 10, txt=f"{company_name} - Monthly Report", ln=True, align="C")
    pdf.set_font("Arial", size=12)
    pdf.cell(200, 10, txt=f"Month: {now.strftime('%B %Y')}", ln=True, align="C")
    pdf.ln(10)

    pdf.set_font("Arial", size=11)
    pdf.cell(200, 10, txt=f"Total Students: {total_students}", ln=True)
    pdf.cell(200, 10, txt=f"Total Advance Fee Received: Rs. {total_advance}", ln=True)
    pdf.cell(200, 10, txt=f"Total Remaining Fee: Rs. {total_remaining}", ln=True)

    pdf.ln(10)
    pdf.set_font("Arial", "B", 12)
    pdf.cell(200, 10, txt="Student Summary:", ln=True)

    pdf.set_font("Arial", size=10)
    for row in rows:
        name, program, adv, rem, created = row
        pdf.cell(200, 8, txt=f"{name} | {program} | Advance: {adv} | Remaining: {rem} | {created}", ln=True)

    pdf.set_font("Arial", 'I', 8)
    pdf.set_text_color(150)
    pdf.ln(10)
    pdf.cell(0, 10, developer_name, align='C')

    filename = f"monthly_report_{now.strftime('%Y-%m')}.pdf"
    pdf.output(filename)
    messagebox.showinfo("Report Created", f"Monthly report saved as:\n{filename}")

# === Buttons ===
tk.Button(window, text="Save Student", command=save_student).pack(pady=20)

# === Generate Slip Section ===
tk.Label(window, text="Generate Slip for Student").pack()
student_var = tk.StringVar()
student_dropdown = tk.OptionMenu(window, student_var, '')
student_dropdown.pack(pady=5)

def refresh_student_list():
    cursor.execute("SELECT name FROM students")
    names = [row[0] for row in cursor.fetchall()]
    menu = student_dropdown["menu"]
    menu.delete(0, "end")
    for name in names:
        menu.add_command(label=name, command=lambda n=name: student_var.set(n))

tk.Button(window, text="Refresh Student List", command=refresh_student_list).pack(pady=5)
tk.Button(window, text="Generate PDF Slip", command=generate_slip).pack(pady=10)

# === Monthly Report Button ===
tk.Button(window, text="Generate Monthly Report", command=generate_monthly_report).pack(pady=20)

# === Developer Watermark ===
watermark = tk.Label(window, text=developer_name, font=("Arial", 8), fg="gray")
watermark.pack(side="bottom", pady=10)

# === On Close ===
def on_close():
    conn.close()
    window.destroy()

window.protocol("WM_DELETE_WINDOW", on_close)
window.mainloop()
