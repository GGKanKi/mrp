![Project Banner](labels/novus_logo1.png)

# NovusMRP: Material Requirements Planning System

## Overview

NovusMRP is a specialized Material Requirements Planning system developed for **NOVUS INDUSTRY SOLUTIONS** to streamline inventory management, procurement,
and production tracking.  This application is the capstone project for the
Bachelor of Science in Information Technology programme at **City College of
Calamba**.

The primary objective of the system is to automate the tracking of materials,
manage supplier relationships, and generate accurate inventory reports that
reduce operational overhead and prevent stock‑outs.

## Key Features

- **Inventory Management:** Centralized tracking of stock levels, materials,
and product requirements.
- **Supplier & Client Management:** CRUD operations to maintain contact and
transaction history for business partners.
- **Audit Logging:** Secure user activity logging to monitor system usage and
ensure data integrity.
- **Order Processing:** Automated handling of production orders and material
replenishment.
- **User Authentication:** Secure login and signup module to manage access
control.

## Technology Stack

| Component      | Details                                    |
|---------------|--------------------------------------------|
| Language       | Python                                     |
| Data Storage   | JSON files & SQLite (flat‑file logging)     |
| GUI Library    | Tkinter / CustomTkinter                    |
| Target OS      | Windows                                    |

## Environment Setup

1. **Clone the repository:**
   ```bash
   git clone https://github.com/GGKanKi/mrp
   ```
2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```
3. **Configuration:**
   - Copy `.env.example` to `.env`.
   - Populate the file with your own Google API credentials and sheet IDs.
   - **Do not commit `.env`**; it is ignored by git to keep secrets private.

> A sample `.env.example` is provided to illustrate the required environment
> variables.  API keys and token files are never stored in the repository.

## Usage

Run the application from the project root:
```bash
python main_sys.py
```

## Project Structure

- `main_sys.py` – Entry point and primary system controller.
- `inventory_crud.py`, `product_crud.py`, etc. – CRUD logic for core entities.
- `json_f/` – JSON databases used for persistence.
- `log_f/` – System and activity log files.
- `labels/` – UI icons and branding assets.

## Thesis Details

- **Developed by:** GGKanki, Abcdy, Rhomar, Jade
- **Documentation by:** GGKanki, Rhomar, Jade
- **Verified by:** Rommel T. Garma, PhD
- **Adviser:** Rommel T. Garma
- **Company Partner:** NOVUS INDUSTRY SOLUTIONS
- **Date:** January 2026

## Acknowledgments
This project was developed as part of the requirements for the degree of
Bachelor of Science in Information Technology at City College of Calamba. We
thank NOVUS INDUSTRY SOLUTIONS for providing the data and insights necessary
to build this system.
