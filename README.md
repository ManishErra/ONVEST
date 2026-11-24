# ONVEST – Loan EMI & SIP Calculator

> **Calculate. Invest. Grow.**  
> A professional, modern, fully offline Windows desktop financial calculator developed with Python and CustomTkinter.

---

## 📌 Overview

**ONVEST** is an offline desktop financial planning application designed to empower individuals with accurate loan repayment modeling and disciplined investment growth forecasting. 

Developed as an engineering project, ONVEST adheres to fintech-grade design standards, offering a dark navy interface, real-time visual breakdowns, parameterized SQLite calculation history, and input validation.

---

## 🎨 Design Theme & Architecture

- **Theme Palette:**
  - **Main Background:** Deep Dark Navy (`#0B1220`)
  - **Sidebar:** Dark Navy (`#111D32`)
  - **Cards & Containers:** Elevated Navy (`#17243A`)
  - **Primary Action:** Vibrant Blue (`#3B82F6`)
  - **Wealth & Accent:** Emerald Green (`#10B981`)
  - **Warning & Cost:** Amber (`#F59E0B`)
  - **Error & Destructive:** Red (`#EF4444`)
  - **Main Typography:** Pure Slate White (`#F8FAFC`)
  - **Secondary Typography:** Cool Slate (`#94A3B8`)
- **Currency:** Indian Rupee (`₹`), formatted using the standard Indian Numbering System (Lakhs and Crores).
- **Offline Reliability:** 100% offline. Zero external APIs, zero cloud synchronizations.

---

## 🚀 Key Features

### 1. 📊 Executive Financial Dashboard
- **Live Database Counter:** Displays actual count of saved calculations.
- **Recent Activity Card:** Displays the most recent EMI or SIP calculation with rate, tenure, and financial totals.
- **Quick Access Cards:** Direct navigation to EMI and SIP tools.
- **Educational Overviews:** Guides explaining loan amortization dynamics and SIP compounding benefits.

### 2. 💳 Loan EMI Calculator
- **Inputs:** Principal loan amount (₹), Annual interest rate (% p.a.), Loan tenure (Years, max 50).
- **Standard Formula:**
  $$\text{EMI} = P \times r \times \frac{(1+r)^n}{(1+r)^n - 1}$$
  *(With zero-interest handling: $\text{EMI} = \frac{P}{n}$)*
- **Real-Time Financial Breakdown:**
  - Monthly Equated Installment (EMI)
  - Principal Borrowed Capital
  - Total Cumulative Interest Payable
  - Total Repayment Amount ($P + \text{Interest}$)
- **Visual Breakdown:** Proportional visual indicator showing the ratio of Principal vs Interest paid.
- **Actions:** Calculate EMI, Reset, and Save Calculation to SQLite.

### 3. 📈 Systematic Investment Plan (SIP) Calculator
- **Inputs:** Monthly investment (₹), Expected annual return rate (% p.a.), Duration (Years, max 50).
- **Compounding Annuity Formula:**
  $$\text{FV} = M \times \frac{(1+i)^n - 1}{i}$$
  *(With zero-return handling: $\text{FV} = M \times n$)*
- **Key Projections:**
  - Total Capital Invested
  - **ESTIMATED RETURNS** (Capital Appreciation)
  - Estimated Future Maturity Value
- **Visual Proportional Bar:** Displays the ratio of Capital Contributed vs Compounded Wealth.
- **Regulatory Disclosures:** Explicit market risk and estimation disclaimers.
- **Actions:** Calculate SIP, Reset, and Save Calculation to SQLite.

### 4. 📜 Calculation History
- **Table-like Layout:** Displays calculation type (`EMI` or `SIP`), input amounts, interest/return rates, duration in years and months, final computed amounts, and timestamps.
- **Management Controls:**
  - **Refresh:** Syncs live records from SQLite.
  - **Delete Record:** Remove individual records with one click.
  - **Clear All:** Protected with a modal confirmation dialog to prevent accidental deletion.
- **Persistent Storage:** Stored locally in `%LOCALAPPDATA%/ONVEST/onvest.db` with fallbacks.

### 5. ℹ️ About ONVEST
- Technical specifications, runtime environment, and architectural breakdown.
- Financial disclaimers regarding credit terms and mutual fund market risk.

---

## 📁 Project Structure

```text
ONVEST/
│
├── main.py                     # Application entry point, window management, routing
│
├── ui/
│   ├── __init__.py             # UI view exports
│   ├── styles.py               # Theme colors, fonts, and Indian currency formatter
│   ├── components.py           # MetricCard, ProportionalBar, SectionHeader, ConfirmationDialog
│   ├── dashboard.py            # Dashboard view with live stats and quick access
│   ├── emi_page.py             # Loan EMI calculator view and validation
│   ├── sip_page.py             # SIP investment calculator view and visual breakdown
│   ├── history_page.py         # Calculation history table and management
│   └── about_page.py           # Application metadata, tech stack, and disclosures
│
├── calculations/
│   ├── __init__.py             # Calculation modules export
│   ├── emi.py                  # Reducing-balance EMI math and input validators
│   └── sip.py                  # Compound annuity SIP math and input validators
│
├── database/
│   ├── __init__.py             # Database operations export
│   └── history.py              # SQLite CRUD operations, connection management, schema init
│
├── tests/
│   ├── __init__.py
│   ├── test_emi.py             # 7 required unit tests for EMI math and validation
│   ├── test_sip.py             # 7 required unit tests for SIP math and validation
│   └── test_database.py        # 6 unit tests for SQLite storage, delete, and clear
│
├── requirements.txt            # Minimal third-party dependencies (customtkinter)
└── README.md                   # Complete documentation
```

---

## 🛠️ Installation & Setup

### Prerequisites
- Python 3.10+ (tested on Python 3.13)
- Windows 10 or Windows 11

### 1. Clone or Open Workspace
Ensure you are in the project root directory:
```powershell
cd "c:\Users\Manish\OneDrive\Projects\Onvest Main"
```

### 2. Install Dependencies
Install the required GUI library using pip:
```powershell
pip install -r requirements.txt
```
*(Only `customtkinter>=6.0.0` is required. All other libraries—`sqlite3`, `math`, `datetime`, `pathlib`, `unittest`—are built into Python).*

---

## 💻 Running the Application

To launch ONVEST:
```powershell
python main.py
```
*(Or specify the explicit Python executable path if your environment aliases require it):*
```powershell
& "C:\Users\Manish\AppData\Local\Programs\Python\Python313\python.exe" main.py
```

---

## 🧪 Running Automated Tests

Run the comprehensive unit test suite using Python's built-in `unittest` runner:

```powershell
python -m unittest discover -s tests -p "test_*.py" -v
```

### Test Coverage Summary:
- **`test_emi.py`**:
  1. Normal loan calculation ($10,00,000 @ 10% for 5 years)
  2. Zero-interest loan ($1,20,000 @ 0% for 1 year)
  3. Small loan amount ($5,000 @ 12% for 6 months)
  4. Long loan tenure ($50,00,000 @ 8.5% for 30 years)
  5. Invalid zero principal rejection
  6. Invalid negative principal rejection
  7. Invalid tenure rejection (zero, negative, >50 years)
  8. Empty and alphabetic string validation
- **`test_sip.py`**:
  1. Normal SIP calculation ($10,000/mo @ 12% for 10 years)
  2. Zero-return calculation ($5,000/mo @ 0% for 2 years)
  3. Small monthly investment ($500/mo @ 15% for 1 year)
  4. Long investment duration ($5,000/mo @ 12% for 30 years)
  5. Invalid zero investment rejection
  6. Invalid negative investment rejection
  7. Invalid duration rejection (zero, negative, >50 years)
  8. Empty and alphabetic string validation
- **`test_database.py`**:
  1. Database and table schema initialization
  2. Saving EMI calculation with parameterized queries
  3. Saving SIP calculation with parameterized queries
  4. Retrieving history sorted newest first
  5. Deleting an individual record
  6. Clearing all history safely

---

## ⚖️ Financial Disclaimers

1. **Loan EMI Estimates:** Calculations are based on standard monthly compound reducing-balance formulas. Individual financial institutions may levy upfront processing fees, GST, documentation charges, and variable benchmark reset periods.
2. **Mutual Fund Market Risk:** SIP future values are projections assuming an uninterrupted constant annual return. Mutual fund investments are subject to market fluctuations. Past performance does not guarantee future results.

---

## 📄 License
Academic & Educational Project — All Rights Reserved.
