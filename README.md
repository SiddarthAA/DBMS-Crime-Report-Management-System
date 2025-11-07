# **Crime Reporting and Management System (CRMS)**

**Course:** UE23CS351A — Database Management Systems (DBMS) Mini Project
**Institution:** PES University
**Semester:** V
**Team Members:**

* **Siddartha A Y** — *PES1UG23AM301*
* **Siddrth Reddy** — *PES1UG23AM300*

---

## **📖 Project Overview**

The **Crime Reporting and Management System (CRMS)** is a Flask-based web application integrated with a MySQL database. It enables **citizens** to report crimes, **officers** to manage and investigate cases, and **administrators** to oversee the entire workflow via a secure, role-based access system.

This project demonstrates core DBMS principles — including **data modeling, referential integrity, normalization, CRUD operations, and transaction handling** — implemented through a full-stack web interface.

---

## **🎯 Objectives**

* Design and implement a **normalized relational database schema** for crime management.
* Provide a secure interface for **citizens, officers, and admins**.
* Enable real-time reporting, assignment, and tracking of crimes.
* Ensure **data consistency and referential integrity** using foreign keys and transactions.
* Showcase DBMS integration with **Flask (Python)** for practical application.

---

## **⚙️ Tech Stack**

| Component             | Technology Used          |
| --------------------- | ------------------------ |
| **Backend Framework** | Flask (Python)           |
| **Database**          | MySQL                    |
| **Frontend**          | HTML5, CSS3, Bootstrap   |
| **ORM / Connector**   | PyMySQL                  |
| **Version Control**   | Git & GitHub             |
| **Server Runtime**    | Flask development server |
| **Template Engine**   | Jinja2                   |

---

## **🧩 Features**

### **1. Role-Based Access Control**

* **Admin:**

  * Manage users (add, delete, assign roles).
  * Oversee all reported crimes.
  * Generate and view crime reports.

* **Officer:**

  * View and manage assigned cases.
  * Update case statuses and add evidence.
  * Submit investigation reports.

* **Citizen:**

  * Report new crimes.
  * View the status of submitted cases.

---

### **2. Core Functional Modules**

| Module                          | Description                                                                         |
| ------------------------------- | ----------------------------------------------------------------------------------- |
| **User Management**             | Handles registration, authentication, and roles (`admin`, `officer`, `citizen`).    |
| **Crime Reporting**             | Citizens can submit new crime reports via web forms.                                |
| **Case Management**             | Admin/officers can view and update status (`Pending`, `Investigating`, `Resolved`). |
| **Evidence & Witness Tracking** | Store evidence files, witness statements, and related data.                         |
| **Reports Generation**          | Generate and maintain detailed investigation reports.                               |

---

## **🗂️ Project Folder Structure**

```
Crime-Reporting-and-Management-System/
│
├── app.py                  # Main Flask application file
├── crms.sql                # MySQL database schema and sample data
├── README.md               # Project documentation
│
├── static/                 # Frontend static assets
│   ├── css/                # Custom CSS stylesheets
│   ├── js/                 # JavaScript files
│   └── images/             # Icons and images
│
├── templates/              # HTML templates rendered using Jinja2
│   ├── base.html           # Common layout (navbar, footer, etc.)
│   ├── login.html          # Login page
│   ├── register.html       # User registration page
│   ├── dashboard_admin.html
│   ├── dashboard_officer.html
│   ├── dashboard_citizen.html
│   ├── citizen_report_crime.html
│   ├── view_crimes.html
│   └── manage_users.html
│
└── venv/ (optional)        # Virtual environment (not pushed to GitHub)
```

---

## **🗃️ Database Design**

The database `CRMS` is normalized and ensures referential integrity through well-defined foreign keys.

### **Key Tables**

| Table                | Description                                                              |
| -------------------- | ------------------------------------------------------------------------ |
| **users**            | Stores user details and roles.                                           |
| **case_status**      | Defines case states (`Pending`, `Investigating`, `Resolved`).            |
| **crimes**           | Records all reported crimes, linking to reporters and assigned officers. |
| **criminals**        | Stores known offenders' data.                                            |
| **case_assignments** | Tracks officer-case mappings.                                            |
| **evidence**         | Holds metadata and file paths for uploaded evidence.                     |
| **witnesses**        | Contains statements and contact details of witnesses.                    |
| **reports**          | Generated by officers/admins for case documentation.                     |

### **Schema Relationships**

* `crimes.reported_by` → `users.user_id`
* `crimes.officer_id` → `users.user_id`
* `crimes.status_id` → `case_status.status_id`
* `reports.generated_by` → `users.user_id`
* `evidence.crime_id`, `witnesses.crime_id`, `case_assignments.crime_id` → `crimes.crime_id`

---

## **💻 Setup and Installation**

### **1. Clone the Repository**

```bash
git clone https://github.com/<your-username>/Crime-Reporting-and-Management-System.git
cd Crime-Reporting-and-Management-System
```

### **2. Create a Virtual Environment**

```bash
python3 -m venv venv
source venv/bin/activate   # (on Linux/Mac)
venv\Scripts\activate      # (on Windows)
```

### **3. Install Dependencies**

```bash
pip install -r requirements.txt
```

*(If you don’t have a requirements file, install manually:)*

```bash
pip install flask pymysql
```

### **4. Setup the Database**

1. Open MySQL in your terminal:

   ```bash
   mysql -u root -p
   ```
2. Create a new database and import the schema:

   ```sql
   CREATE DATABASE CRMS;
   USE CRMS;
   SOURCE crms.sql;
   ```

### **5. Configure Database Connection**

In `app.py`, update your connection details:

```python
def get_db():
    return pymysql.connect(
        host='localhost',
        user='root',
        password='your_password',
        database='CRMS'
    )
```

### **6. Run the Application**

```bash
python app.py
```

Access it on:
👉 `http://127.0.0.1:5000/`

---

## **🧠 Learning Outcomes**

* Understanding of **relational database design** and foreign key constraints.
* Integration of **Flask with MySQL** for real-world web applications.
* Handling **CRUD operations**, transactions, and role-based access control.
* Designing normalized schemas for **complex multi-role systems**.
* Using **Flask routing, Jinja2 templates, and session management** effectively.

---

## **🔐 Future Enhancements**

* Add **password hashing (bcrypt)** for stronger authentication.
* Implement **AJAX-based case status updates** for better interactivity.
* Enable **file uploads** for evidence (PDFs, images).
* Add **email notifications** for users and officers.
* Deploy to **Render / Heroku / AWS** for cloud hosting.

---

## **📜 License**

This project was developed as part of the **DBMS Mini Project (UE23CS351A)** at **PES University**.
All rights reserved © 2025 — *Siddartha A Y & Siddrth Reddy.*
