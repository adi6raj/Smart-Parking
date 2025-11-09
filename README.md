# 🚗 Smart Parking System  

## 📘 Project Overview  
The **Smart Parking System** is a Python-based desktop application that automates vehicle parking management.  
It provides an easy-to-use graphical interface (built with **Tkinter**) for parking attendants or administrators to:

- Manage parking slot allocation  
- Track vehicle entries and exits  
- Calculate parking charges dynamically  
- Generate PDF invoices and daily reports  
- Send real-time email notifications to customers  
- View parking locations directly on Google Maps  

This project integrates **MongoDB** for data management, **OpenCV** for webcam snapshots, and **ReportLab** for PDF generation.  

---

## ✨ Key Features  

### 🔐 Login System  
Secure login for admin access.  
**Default credentials:**  

<img width="318" height="94" alt="image" src="https://github.com/user-attachments/assets/3e60f105-9ced-403e-8637-1f6c04956b47" />


### 🅿️ Parking Management  
- Park new vehicles and assign slot numbers.  
- Fetch customer data automatically from MongoDB.  
- Supports **Car Wash** and **Servicing** add-ons with extra charges.  
- Real-time display of available parking slots.  

---

### ⏱️ Exit & Billing  
- Calculates parking duration and total fee based on hourly rate.  
- Adds additional service charges when selected.  
- Generates professional **PDF invoices** for each customer.  
- Attaches **webcam snapshots** of parked vehicles.  
- Sends email receipts via **SMTP (Gmail)**.  

---

### 🧾 Daily Report  
- Exports all transactions of the current day as a **PDF report** using ReportLab.  

---

### 🌍 Location Integration  
- Contains 200+ predefined fictional parking locations.  
- Opens parking locations directly in **Google Maps**.  

---

### 📸 Snapshot System  
- Captures live vehicle images using **OpenCV**.  
- Stores snapshots in a dedicated `snapshots/` directory.  

---

### 🧑‍💼 Admin Panel  
- Displays all entries in a sortable **TreeView table**.  
- Includes customer details, timings, charges, and payment mode.  

---

## ⚙️ Technologies Used  

| Component | Technology |
|------------|-------------|
| **Frontend (GUI)** | Tkinter |
| **Database** | MongoDB |
| **Email Service** | SMTP (Gmail) |
| **PDF Generation** | ReportLab |
| **Image Capture** | OpenCV |
| **Language** | Python 3 |

---

## 🗂️ Project Structure  
<img width="613" height="184" alt="image" src="https://github.com/user-attachments/assets/b94b5c76-4a22-4798-9480-6bf50dfe9548" />


## ⚙️ Configuration & Constants  

| Variable | Description |
|-----------|-------------|
| `MAX_SLOTS = 10` | Maximum parking slots available |
| `RATE_PER_HOUR = 20` | Charge per hour |
| `CAR_WASH_CHARGE = 50` | Car wash cost |
| `SERVICE_CHARGE = 100` | Servicing fee |
| `SENDER_EMAIL` | Sender Gmail address |
| `SENDER_PASSWORD` | Gmail App password |

---

## 🧰 Installation & Setup  

### 1️⃣ Clone the Repository  
```bash
git clone https://github.com/adi6raj/Smart-Parking.git
cd smart-parking-system
```
### 📬 Email Notifications Example
Vehicle Parking Confirmation
Exit Invoice with Attached PDF & Snapshot
Daily Report Notification
Emails are formatted in HTML with smart styling and a link to the parking location.

### 👨‍💻 Author
 Adi
🎓 Student Developer | Python Enthusiast
📧 hey.adiii0@gmail.com
