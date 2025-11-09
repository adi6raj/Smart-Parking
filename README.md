#🚗 Smart Parking System
📘 Project Overview

The Smart Parking System is a Python-based desktop application that helps automate the process of vehicle parking management.
It provides an easy-to-use graphical interface (built with Tkinter) for parking attendants or administrators to:

Manage parking slot allocation
Track vehicle entries and exits
Calculate parking charges dynamically
Generate PDF invoices and daily reports
Send real-time email notifications to customers
View parking locations directly on Google Maps
This project integrates MongoDB for database management, OpenCV for webcam snapshots, and ReportLab for PDF report generation.

#🧩 Key Features
#🔐 Login System

Secure login for admin access.
Default credentials:
<img width="318" height="94" alt="image" src="https://github.com/user-attachments/assets/3e60f105-9ced-403e-8637-1f6c04956b47" />

#🅿️ Parking Management

Park new vehicles and assign slot numbers.
Fetch customer data automatically from MongoDB.
Supports Car Wash and Servicing add-ons with extra charges.
Real-time display of available parking slots.

#🕒 Exit and Billing
Automatically calculates total duration and parking fee based on hourly rate.
Adds additional service charges if selected.
Generates professional PDF invoices for each customer.
Attaches webcam snapshots of parked vehicles in invoices.
Sends email receipts using SMTP.

#🧾 Daily Report
Exports all transactions of the current day as a PDF report using ReportLab.

#🌍 Location Integration
Predefined 200+ fictional parking locations.
Opens selected parking location directly in Google Maps via browser.

#🖼️ Snapshot System
Captures live vehicle images through a webcam using OpenCV.
Stores them in a dedicated snapshots/ directory.

#🧑‍💼 Admin Panel
Displays all vehicle data in tabular form using Tkinter’s Treeview.
Includes entry, exit, slot, customer details, charges, and payment mode.

⚙️ Technologies Used
Component	               Technology
Frontend (GUI)	          Tkinter
Database	                MongoDB
Email Service	            SMTP (Gmail)
PDF Generation	          ReportLab
Image Capture	            OpenCV
Backend Language	        Python 3
IDE (Recommended)	        PyCharm / VS Code

#🗂️ Project Structure
<img width="613" height="184" alt="image" src="https://github.com/user-attachments/assets/b94b5c76-4a22-4798-9480-6bf50dfe9548" />

#🧮 Configuration & Constants
Parameter              	Description
MAX_SLOTS = 10	         Maximum parking slots
RATE_PER_HOUR = 20	     Charge per hour
CAR_WASH_CHARGE = 50	   Optional car wash fee
SERVICE_CHARGE = 100	   Optional servicing fee
SENDER_EMAIL	           Email address for sending notifications
SENDER_PASSWORD	         App password for Gmail SMTP

#📬 Email Notifications Example
Vehicle Parking Confirmation
Exit Invoice with Attached PDF & Snapshot
Daily Report Notification
Emails are formatted in HTML with smart styling and a link to the parking location.

#👨‍💻 Author
Adi
🎓 Student Developer | Python Enthusiast
📧 hey.adiii0@gmail.com
