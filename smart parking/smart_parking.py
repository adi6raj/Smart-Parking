import tkinter as tk
from tkinter import messagebox, ttk
from datetime import datetime, date
from pymongo import MongoClient
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from email.mime.application import MIMEApplication
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import smtplib
import cv2
import os           
import webbrowser
import uuid

# === CONFIG ===
ADMIN_USERNAME = "admin"
ADMIN_PASSWORD = "1234"
MAX_SLOTS = 10
RATE_PER_HOUR = 20
CAR_WASH_CHARGE = 50
SERVICE_CHARGE = 100
SENDER_EMAIL = "hey.adiii0@gmail.com"
SENDER_PASSWORD = "ndug rwci jztu uslc"

# Predefined parking locations (200 fictional locations)
PARKING_LOCATIONS = [
    {"name": f"Parking Lot {i}", "url": f"https://www.google.com/maps/place/{40.7128 + i*0.001},{74.0060 + i*0.001}"}
    for i in range(1, 201)
]

# === MongoDB SETUP ===
client = MongoClient("mongodb://localhost:27017/")
db = client["smart_parking"]
collection = db["entries"]
customers_collection = db["customers"]

# === Ensure snapshot folder exists ===
if not os.path.exists("snapshots"):
    os.makedirs("snapshots")

# === Email Notification ===
def send_email_notification(subject, body, to_email, attachments=None, location_url=None):
    msg = MIMEMultipart()
    msg['From'] = SENDER_EMAIL
    msg['To'] = to_email
    msg['Subject'] = subject
    
    # Enhanced HTML email template
    html_body = f"""
    <html>
        <body style="font-family: Arial, sans-serif; color: #333;">
            <div style="max-width: 600px; margin: 0 auto; padding: 20px; border: 1px solid #ddd; border-radius: 10px;">
                <h2 style="color: #2c3e50; text-align: center;">Smart Parking System</h2>
                <hr style="border: 1px solid #3498db;">
                <p style="font-size: 16px;">{body}</p>
                <p style="font-size: 14px; color: #7f8c8d;">For support, contact us at support@smartparking.com</p>
                <div style="text-align: center; margin-top: 20px;">
                    <a href="{location_url}" style="background-color: #3498db; color: white; padding: 10px 20px; text-decoration: none; border-radius: 5px;">View Parking Location</a>
                </div>
            </div>
        </body>
    </html>
    """
    msg.attach(MIMEText(html_body, 'html'))

    if attachments:
        for file_path in attachments:
            try:
                with open(file_path, 'rb') as f:
                    part = MIMEApplication(f.read(), Name=os.path.basename(file_path))
                    part['Content-Disposition'] = f'attachment; filename="{os.path.basename(file_path)}"'
                    msg.attach(part)
            except Exception as e:
                print(f"Attachment Error for {file_path}:", e)

    try:
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(SENDER_EMAIL, SENDER_PASSWORD)
        server.send_message(msg)
        server.quit()
    except Exception as e:
        print("Error sending email:", e)

# === Webcam Capture ===
def capture_snapshot(vehicle_no):
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("Webcam not accessible")
        return

    ret, frame = cap.read()
    if ret:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"snapshots/{vehicle_no}_{timestamp}.jpg"
        cv2.imwrite(filename, frame)
        print(f"Snapshot saved as {filename}")
    cap.release()
    cv2.destroyAllWindows()

# === Main App ===
def open_main_app():
    global label_slots, entry_vehicle_no, entry_slot, entry_email, chk_wash_var, chk_service_var, customer_dropdown, entry_customer_name, location_dropdown

    root = tk.Tk()
    root.title("Smart Parking System")
    root.geometry("600x800")
    root.configure(bg="#f0f2f5")

    def update_slot_display():
        occupied = [entry['slot_no'] for entry in collection.find({"exit_time": None})]
        available = [str(i) for i in range(1, MAX_SLOTS + 1) if i not in occupied]
        label_slots.config(text=f"Available Slots: {', '.join(available)}")

    def clear_fields():
        entry_vehicle_no.delete(0, tk.END)
        entry_slot.delete(0, tk.END)
        entry_email.delete(0, tk.END)
        entry_customer_name.delete(0, tk.END)
        chk_wash_var.set(False)
        chk_service_var.set(False)
        customer_dropdown.set("Select Customer")
        location_dropdown.set(PARKING_LOCATIONS[0]["name"])

    def populate_customer_dropdown():
        customers = customers_collection.find()
        customer_list = ["Select Customer"] + [f"{c['customer_name']} ({c['vehicle_no']} - {c['email']})" for c in customers]
        customer_dropdown['values'] = customer_list

    def on_customer_select(event):
        selection = customer_dropdown.get()
        if selection != "Select Customer":
            # Extract customer_name, vehicle_no, and email from selection
            try:
                customer_info = selection.split(" (")[1].rstrip(")")
                vehicle_no, email = customer_info.split(" - ")
                customer_name = selection.split(" (")[0]
                entry_vehicle_no.delete(0, tk.END)
                entry_vehicle_no.insert(0, vehicle_no)
                entry_email.delete(0, tk.END)
                entry_email.insert(0, email)
                entry_customer_name.delete(0, tk.END)
                entry_customer_name.insert(0, customer_name)
            except:
                pass

    def park_vehicle():
        vehicle_no = entry_vehicle_no.get().strip()
        slot_no = entry_slot.get().strip()
        email = entry_email.get().strip()
        customer_name = entry_customer_name.get().strip()
        car_wash = chk_wash_var.get()
        servicing = chk_service_var.get()
        location = location_dropdown.get()

        if not vehicle_no or not slot_no or not email or not customer_name:
            messagebox.showerror("Error", "All fields required")
            return

        try:
            slot_no = int(slot_no)
            if slot_no > MAX_SLOTS:
                raise ValueError
        except:
            messagebox.showerror("Error", f"Slot must be a number (1–{MAX_SLOTS})")
            return

        if collection.find_one({"slot_no": slot_no, "exit_time": None}):
            messagebox.showerror("Slot Occupied", "This slot is already in use.")
            return

        entry_time = datetime.now()
        selected_location = next(loc for loc in PARKING_LOCATIONS if loc["name"] == location)
        collection.insert_one({
            "vehicle_no": vehicle_no,
            "entry_time": entry_time,
            "exit_time": None,
            "slot_no": slot_no,
            "charges": None,
            "email": email,
            "customer_name": customer_name,
            "car_wash": car_wash,
            "servicing": servicing,
            "location": location
        })

        # Save customer details
        if not customers_collection.find_one({"vehicle_no": vehicle_no, "email": email, "customer_name": customer_name}):
            customers_collection.insert_one({"vehicle_no": vehicle_no, "email": email, "customer_name": customer_name})

        capture_snapshot(vehicle_no)

        extra_services = []
        if car_wash:
            extra_services.append("Car Wash")
        if servicing:
            extra_services.append("Servicing")
        services_str = ", ".join(extra_services) if extra_services else "None"

        send_email_notification(
            "Vehicle Parked Successfully",
            f"""
            Dear {customer_name},<br><br>
            Your vehicle <b>{vehicle_no}</b> has been successfully parked at <b>Slot {slot_no}</b> in <b>{location}</b>.<br>
            <b>Entry Time:</b> {entry_time.strftime('%Y-%m-%d %H:%M:%S')}<br>
            <b>Selected Services:</b> {services_str}<br><br>
            Thank you for choosing Smart Parking System!
            """,
            email,
            location_url=selected_location["url"]
        )

        messagebox.showinfo("Success", f"Vehicle parked at slot {slot_no}")
        clear_fields()
        populate_customer_dropdown()
        update_slot_display()

    def show_parked_vehicles():
        parked_window = tk.Toplevel(root)
        parked_window.title("Parked Vehicles")
        parked_window.geometry("700x400")
        parked_window.configure(bg="#ffffff")

        tk.Label(parked_window, text="Select Parked Vehicle", font=("Helvetica", 16, "bold"), bg="#ffffff").pack(pady=10)

        tree = ttk.Treeview(parked_window, columns=("Customer", "Vehicle", "Slot", "Entry Time"), show='headings')
        tree.heading("Customer", text="Customer Name")
        tree.heading("Vehicle", text="Vehicle No")
        tree.heading("Slot", text="Slot No")
        tree.heading("Entry Time", text="Entry Time")
        tree.pack(fill='both', expand=True, padx=10, pady=10)

        parked_vehicles = collection.find({"exit_time": None})
        vehicle_count = 0
        for vehicle in parked_vehicles:
            tree.insert('', tk.END, values=(
                vehicle['customer_name'],
                vehicle['vehicle_no'],
                vehicle['slot_no'],
                vehicle['entry_time'].strftime("%Y-%m-%d %H:%M:%S")
            ))
            vehicle_count += 1

        if vehicle_count == 0:
            tk.Label(parked_window, text="No vehicles currently parked", bg="#ffffff", font=("Helvetica", 12)).pack(pady=10)
            tk.Button(parked_window, text="Close", command=parked_window.destroy, bg="#e74c3c", fg="white", font=("Helvetica", 12)).pack(pady=5)
            return

        def select_vehicle():
            selected = tree.selection()
            if not selected:
                messagebox.showerror("Error", "Please select a vehicle")
                return
            vehicle_no = tree.item(selected)['values'][1]
            entry_vehicle_no.delete(0, tk.END)
            entry_vehicle_no.insert(0, vehicle_no)
            parked_window.destroy()
            process_exit_vehicle(vehicle_no)

        tk.Button(parked_window, text="Select", command=select_vehicle, bg="#3498db", fg="white", font=("Helvetica", 12)).pack(pady=10)
        tk.Button(parked_window, text="Cancel", command=parked_window.destroy, bg="#e74c3c", fg="white", font=("Helvetica", 12)).pack(pady=5)

    def exit_vehicle():
        show_parked_vehicles()

    def process_exit_vehicle(vehicle_no):
        active = collection.find_one({"vehicle_no": vehicle_no, "exit_time": None})
        if not active:
            messagebox.showerror("Not Found", "No active record found")
            return

        exit_time = datetime.now()
        entry_time = active['entry_time']
        duration = (exit_time - entry_time).total_seconds() / 3600
        base_charge = round(duration * RATE_PER_HOUR, 2)

        extra = 0
        details = ""
        if active.get("car_wash"):
            extra += CAR_WASH_CHARGE
            details += f"\nCar Wash: ₹{CAR_WASH_CHARGE}"
        if active.get("servicing"):
            extra += SERVICE_CHARGE
            details += f"\nServicing: ₹{SERVICE_CHARGE}"

        total_charges = base_charge + extra

        # Payment Window
        payment_window = tk.Toplevel(root)
        payment_window.title("Payment Details")
        payment_window.geometry("400x500")
        payment_window.configure(bg="#ffffff")

        tk.Label(payment_window, text="Payment Details", font=("Helvetica", 16, "bold"), bg="#ffffff").pack(pady=10)
        tk.Label(payment_window, text=f"Customer: {active['customer_name']}", bg="#ffffff").pack()
        tk.Label(payment_window, text=f"Vehicle: {vehicle_no}", bg="#ffffff").pack()
        tk.Label(payment_window, text=f"Entry: {entry_time.strftime('%Y-%m-%d %H:%M:%S')}", bg="#ffffff").pack()
        tk.Label(payment_window, text=f"Exit: {exit_time.strftime('%Y-%m-%d %H:%M:%S')}", bg="#ffffff").pack()
        tk.Label(payment_window, text=f"Duration: {round(duration, 2)} hours", bg="#ffffff").pack()
        tk.Label(payment_window, text=f"Parking Charges: ₹{base_charge}", bg="#ffffff").pack()
        if active.get("car_wash"):
            tk.Label(payment_window, text=f"Car Wash: ₹{CAR_WASH_CHARGE}", bg="#ffffff").pack()
        if active.get("servicing"):
            tk.Label(payment_window, text=f"Servicing: ₹{SERVICE_CHARGE}", bg="#ffffff").pack()
        tk.Label(payment_window, text=f"Total: ₹{total_charges}", font=("Helvetica", 12, "bold"), bg="#ffffff").pack(pady=10)

        payment_mode = tk.StringVar(value="Cash")
        tk.Label(payment_window, text="Select Payment Mode:", bg="#ffffff").pack()
        tk.Radiobutton(payment_window, text="Cash", variable=payment_mode, value="Cash", bg="#ffffff").pack()
        tk.Radiobutton(payment_window, text="Credit Card", variable=payment_mode, value="Credit Card", bg="#ffffff").pack()
        tk.Radiobutton(payment_window, text="UPI", variable=payment_mode, value="UPI", bg="#ffffff").pack()

        def confirm_payment():
            collection.update_one(
                {"_id": active['_id']},
                {"$set": {
                    "exit_time": exit_time,
                    "charges": total_charges,
                    "payment_mode": payment_mode.get()
                }}
            )

            pdf_file = f"{vehicle_no}_bill.pdf"
            c = canvas.Canvas(pdf_file, pagesize=letter)
            c.setFont("Helvetica-Bold", 16)
            c.drawString(100, 750, "Smart Parking System - Invoice")
            c.setFont("Helvetica", 12)
            c.drawString(100, 720, f"Invoice ID: {str(uuid.uuid4())[:8]}")
            c.drawString(100, 700, f"Customer Name: {active['customer_name']}")
            c.drawString(100, 680, f"Vehicle No: {vehicle_no}")
            c.drawString(100, 660, f"Entry Time: {entry_time.strftime('%Y-%m-%d %H:%M:%S')}")
            c.drawString(100, 640, f"Exit Time: {exit_time.strftime('%Y-%m-%d %H:%M:%S')}")
            c.drawString(100, 620, f"Duration: {round(duration, 2)} hours")
            c.drawString(100, 600, f"Parking Charges: ₹{base_charge}")
            y = 580
            if active.get("car_wash"):
                c.drawString(100, y, f"Car Wash: ₹{CAR_WASH_CHARGE}")
                y -= 20
            if active.get("servicing"):
                c.drawString(100, y, f"Servicing: ₹{SERVICE_CHARGE}")
                y -= 20
            c.drawString(100, y, f"Payment Mode: {payment_mode.get()}")
            c.drawString(100, y-20, f"Total Charges: ₹{total_charges}")
            c.save()

            snapshot_path = None
            snapshots = sorted(
                [f for f in os.listdir("snapshots") if f.startswith(vehicle_no)],
                reverse=True
            )
            if snapshots:
                snapshot_path = os.path.join("snapshots", snapshots[0])

            attachments = [pdf_file]
            if snapshot_path:
                attachments.append(snapshot_path)

            selected_location = next(loc for loc in PARKING_LOCATIONS if loc["name"] == active['location'])
            send_email_notification(
                "Vehicle Exit Invoice",
                f"""
                Dear {active['customer_name']},<br><br>
                Thank you for using Smart Parking System. Below are your invoice details:<br>
                <b>Invoice ID:</b> {str(uuid.uuid4())[:8]}<br>
                <b>Customer Name:</b> {active['customer_name']}<br>
                <b>Vehicle No:</b> {vehicle_no}<br>
                <b>Entry Time:</b> {entry_time.strftime('%Y-%m-%d %H:%M:%S')}<br>
                <b>Exit Time:</b> {exit_time.strftime('%Y-%m-%d %H:%M:%S')}<br>
                <b>Duration:</b> {round(duration, 2)} hours<br>
                <b>Parking Charges:</b> ₹{base_charge}<br>
                {details.replace('\n', '<br>')}
                <b>Payment Mode:</b> {payment_mode.get()}<br>
                <b>Total Charges:</b> ₹{total_charges}<br><br>
                Please find the invoice attached.
                """,
                active['email'],
                attachments,
                location_url=selected_location["url"]
            )

            messagebox.showinfo("Success", f"Payment completed. Charges: ₹{total_charges}")
            payment_window.destroy()
            clear_fields()
            update_slot_display()

        tk.Button(payment_window, text="Confirm Payment", command=confirm_payment, bg="#3498db", fg="white", font=("Helvetica", 12)).pack(pady=20)

    def show_admin_panel():
        panel = tk.Toplevel(root)
        panel.title("Admin Panel")
        panel.geometry("1000x400")
        panel.configure(bg="#f0f2f5")

        tree = ttk.Treeview(panel, columns=("ID", "Customer", "Vehicle", "Entry", "Exit", "Slot", "Charges", "Email", "Wash", "Service", "Payment", "Location"), show='headings')
        tree.pack(fill='both', expand=True)

        for col in tree['columns']:
            tree.heading(col, text=col)
            tree.column(col, width=100)

        for entry in collection.find():
            tree.insert('', tk.END, values=(
                str(entry['_id']),
                entry['customer_name'],
                entry['vehicle_no'],
                entry['entry_time'].strftime("%Y-%m-%d %H:%M:%S"),
                entry['exit_time'].strftime("%Y-%m-%d %H:%M:%S") if entry['exit_time'] else "---",
                entry['slot_no'],
                f"₹{entry['charges']:.2f}" if entry['charges'] else "---",
                entry['email'],
                "Yes" if entry.get("car_wash") else "No",
                "Yes" if entry.get("servicing") else "No",
                entry.get("payment_mode", "---"),
                entry.get("location", "---")
            ))

    def generate_pdf_report():
        today = date.today()
        entries = collection.find({
            "entry_time": {
                "$gte": datetime(today.year, today.month, today.day),
                "$lt": datetime(today.year, today.month, today.day, 23, 59, 59)
            }
        })

        file_name = f"Daily_Report_{today}.pdf"
        c = canvas.Canvas(file_name, pagesize=letter)
        c.setFont("Helvetica-Bold", 14)
        c.drawString(200, 770, f"Smart Parking Report - {today}")
        c.setFont("Helvetica", 12)
        y = 740
        c.drawString(20, y, "Customer  Vehicle  Entry  Exit  Slot  Charges  Payment")
        y -= 20

        for entry in entries:
            text = f"{entry['customer_name']}  {entry['vehicle_no']}  {entry['entry_time'].strftime('%H:%M')}  " \
                   f"{entry['exit_time'].strftime('%H:%M') if entry['exit_time'] else '---'}  " \
                   f"{entry['slot_no']}  ₹{entry['charges'] if entry['charges'] else 0:.2f}  " \
                   f"{entry.get('payment_mode', '---')}"
            c.drawString(20, y, text)
            y -= 20
            if y < 50:
                c.showPage()
                y = 770

        c.save()
        messagebox.showinfo("PDF Generated", f"Saved as {file_name}")

    def open_map():
        selected_location = location_dropdown.get()
        location = next(loc for loc in PARKING_LOCATIONS if loc["name"] == selected_location)
        webbrowser.open(location["url"])

    # === GUI Layout ===
    frame = tk.Frame(root, bg="#f0f2f5")
    frame.pack(pady=20, padx=20, fill="both", expand=True)

    tk.Label(frame, text="Smart Parking System", font=("Helvetica", 20, "bold"), bg="#f0f2f5", fg="#2c3e50").pack(pady=10)

    tk.Label(frame, text="Select Previous Customer", bg="#f0f2f5").pack()
    customer_dropdown = ttk.Combobox(frame, state="readonly")
    customer_dropdown.pack(pady=5)
    customer_dropdown.bind("<<ComboboxSelected>>", on_customer_select)
    populate_customer_dropdown()

    tk.Label(frame, text="Customer Name", bg="#f0f2f5").pack()
    entry_customer_name = tk.Entry(frame, font=("Helvetica", 12))
    entry_customer_name.pack(pady=5)

    tk.Label(frame, text="Vehicle Number", bg="#f0f2f5").pack()
    entry_vehicle_no = tk.Entry(frame, font=("Helvetica", 12))
    entry_vehicle_no.pack(pady=5)

    tk.Label(frame, text="Slot Number", bg="#f0f2f5").pack()
    entry_slot = tk.Entry(frame, font=("Helvetica", 12))
    entry_slot.pack(pady=5)

    tk.Label(frame, text="Owner Email ID", bg="#f0f2f5").pack()
    entry_email = tk.Entry(frame, font=("Helvetica", 12))
    entry_email.pack(pady=5)

    tk.Label(frame, text="Select Parking Location", bg="#f0f2f5").pack()
    location_dropdown = ttk.Combobox(frame, state="readonly", values=[loc["name"] for loc in PARKING_LOCATIONS])
    location_dropdown.set(PARKING_LOCATIONS[0]["name"])
    location_dropdown.pack(pady=5)

    chk_wash_var = tk.BooleanVar()
    chk_service_var = tk.BooleanVar()
    tk.Checkbutton(frame, text="Car Wash (₹50)", variable=chk_wash_var, bg="#f0f2f5", font=("Helvetica", 10)).pack()
    tk.Checkbutton(frame, text="Servicing (₹100)", variable=chk_service_var, bg="#f0f2f5", font=("Helvetica", 10)).pack()

    tk.Button(frame, text="Park Vehicle", command=park_vehicle, bg="#3498db", fg="white", font=("Helvetica", 12)).pack(pady=10)
    tk.Button(frame, text="Vehicle Exit", command=exit_vehicle, bg="#e74c3c", fg="white", font=("Helvetica", 12)).pack()
    label_slots = tk.Label(frame, text="Available Slots:", bg="#f0f2f5", font=("Helvetica", 12))
    label_slots.pack(pady=10)

    tk.Button(frame, text="📍 View Parking Map", command=open_map, bg="#2ecc71", fg="white", font=("Helvetica", 12)).pack(pady=5)
    tk.Button(frame, text="📂 Admin Panel", command=show_admin_panel, bg="#9b59b6", fg="white", font=("Helvetica", 12)).pack(pady=5)
    tk.Button(frame, text="📄 Export Today's Report", command=generate_pdf_report, bg="#f1c40f", fg="white", font=("Helvetica", 12)).pack(pady=5)

    update_slot_display()
    root.mainloop()

# === Login Screen ===
def login_screen():
    login = tk.Tk()
    login.title("Smart Parking Admin Login")
    login.geometry("500x400")
    login.configure(bg="#2c3e50")

    # Create a frame for the login form
    frame = tk.Frame(login, bg="#ffffff", bd=5)
    frame.place(relx=0.5, rely=0.5, anchor="center", width=350, height=300)

    # Stylish heading
    tk.Label(frame, text="Smart Parking", font=("Helvetica", 24, "bold"), bg="#ffffff", fg="#3498db").pack(pady=20)

    # Username
    tk.Label(frame, text="Username", bg="#ffffff", font=("Helvetica", 12)).pack()
    entry_user = tk.Entry(frame, font=("Helvetica", 12), width=25)
    entry_user.pack(pady=5)

    # Password
    tk.Label(frame, text="Password", bg="#ffffff", font=("Helvetica", 12)).pack()
    entry_pass = tk.Entry(frame, show="*", font=("Helvetica", 12), width=25)
    entry_pass.pack(pady=5)

    def validate_login():
        username = entry_user.get()
        password = entry_pass.get()
        if username == ADMIN_USERNAME and password == ADMIN_PASSWORD:
            login.destroy()
            open_main_app()
        else:
            messagebox.showerror("Login Failed", "Invalid credentials!")

    # Login Button
    tk.Button(frame, text="Login", command=validate_login, bg="#3498db", fg="white", font=("Helvetica", 12, "bold"), width=15).pack(pady=20)

    # Add some animation effect on hover
    def on_enter(e):
        e.widget['background'] = '#2980b9'

    def on_leave(e):
        e.widget['background'] = '#3498db'

    for widget in frame.winfo_children():
        if isinstance(widget, tk.Button):
            widget.bind("<Enter>", on_enter)
            widget.bind("<Leave>", on_leave)

    login.mainloop()

# === Start the App ===
login_screen()