![Project Banner](novus_logo1.png)

NovusMRP: Material Requirements Planning System
Overview
NovusMRP is a specialized Material Requirements Planning system designed for NOVUS INDUSTRY SOLUTIONS to streamline inventory management, procurement, and production tracking. This system serves as the capstone project for BACHELOR OF SCIENCE IN INFORMATION TECHNOLOGY at CITY COLLEGE OF CALAMBA.

The primary objective of this system is to automate the tracking of materials, manage supplier relationships, and generate accurate inventory reports to reduce operational overhead and prevent stockouts.

Key Features
Inventory Management: Centralized tracking of stock levels, materials, and product requirements.

Supplier & Client Management: CRUD operations to maintain contact and transaction history for business partners.

Audit Logging: Secure user activity logging to monitor system usage and ensure data integrity.

Order Processing: Automated handling of production orders and material replenishment.

User Authentication: Secure login and signup module to manage access control.

Technology Stack
Language: Python

Data Storage: JSON-based data persistence and flat-file logging

Interface: Insert GUI library, e.g., Tkinter/CustomTkinter

Environment: Designed for Windows execution

Installation
Clone this repository to your local machine:

Bash

git clone https://github.com/GGKanKi/mrp
Ensure you have Python installed.

Install required dependencies (if applicable):

Bash

pip install -r requirements.txt
Usage
To launch the system, navigate to the project directory in your terminal and execute:

Bash

python main_sys.py
Project Structure
main_sys.py: The entry point and primary system controller.

inventory_crud.py / product_crud.py: Logic for managing core database entities.

json_f/: Directory containing JSON databases for persistence.

log_f/: Directory containing system and activity logs.

labels/: Asset folder for UI icons and branding.

Thesis Details
Developed by: GGKanki, Abcdy, Rhomar, Jade
Documentation by: GGKanki, Rhomar, Jade
Verified By; Rommel T. Garma, PhD

Adviser: Rommel T. Garma

Company Partner: NOVUS INDUSTRY SOLUTIONS

Date: JANUARY 2026

Acknowledgments
This project was developed as part of the requirements for the degree of BACHELOR OF SCIENCE IN INFORMATION TECHNOLOGY at CITY COLLEGE OF CALAMBA. We would like to thank NOVUS INDUSTRY SOLUTIONS for providing the data and insights necessary to build this system.
