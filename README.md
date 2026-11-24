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
- **Calculation Convention (Option A — Theoretical-Total Formula Estimate with Rounding Adjustment):**
  - The monthly EMI is rounded to two decimal places (paise).
  - The unrounded theoretical reducing-balance formula total is calculated as $\text{exact\_total\_repayment} = \text{exact\_emi} \times n$.
  - Because regular monthly installments are rounded to paise, an explicit final-installment rounding adjustment is derived:
    $$\text{final\_installment} = \text{round}(\text{exact\_total\_repayment} - (\text{monthly\_emi} \times (n - 1)), 2)$$
  - Total repayment is reconciled with the displayed installment schedule:
    $$\text{total\_repayment} = \text{round}((\text{monthly\_emi} \times (n - 1)) + \text{final\_installment}, 2)$$
  - Total interest is derived strictly from total repayment minus principal:
    $$\text{total\_interest} = \text{round}(\text{total\_repayment} - \text{principal}, 2)$$
  - *Convention Note:* This describes a theoretical reducing-balance formula estimate with a final-installment rounding adjustment. It does not simulate a month-by-month lender amortization schedule with daily interest or lender-specific rounding.
- **Explanatory Disclaimer:**
  > *"This is an estimated reducing-balance EMI calculation. The displayed final installment adjusts for rounding differences. Actual lender repayment schedules may differ due to payment dates, daily interest calculations, fees, and lender-specific rounding policies."*
- **Real-Time Financial Breakdown:**
  - Monthly Equated Installment (EMI)
  - Final Installment Amount (with explanatory note when adjusted for paise rounding)
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
- **Key Projections (Illustrative Estimates — Not Guaranteed):**
  - Total Capital Invested
  - **ESTIMATED RETURNS** (Projected capital appreciation estimates, not guaranteed)
  - Estimated Future Maturity Value
- **Explanatory Disclaimer:**
  > *"SIP projections are illustrative estimates and actual mutual fund returns are market-dependent and not guaranteed. Projected returns are based on assumed constant compounding rates for illustration purposes and must not be regarded as guaranteed or assured returns. Future value calculations exclude taxes, exit loads, and expense ratios. Past market performance is not indicative of future returns."*
- **Visual Proportional Bar:** Displays the ratio of Capital Contributed vs Compounded Wealth.
- **Actions:** Calculate SIP, Reset, and Save Calculation to SQLite.

### 4. 📜 Calculation History & Resilient SQLite Storage
- **Table-like Layout:** Displays calculation type (`EMI` or `SIP`), input amounts, interest/return rates, duration in years and months, final computed amounts, and timestamps.
- **Management Controls:**
  - **Refresh:** Syncs live records from SQLite.
  - **Delete Record:** Remove individual records with one click.
  - **Clear All:** Protected with a modal confirmation dialog to prevent accidental deletion.
- **Resilient Multi-Tier Database Fallback with Dual-Case Probing:**
  ONVEST verifies actual database write access by inspecting the candidate database file directly, not merely its parent directory:
  1. **Existing Database Verification:** If `onvest.db` already exists at a candidate path, ONVEST connects, performs an integrity check (`PRAGMA quick_check`), and verifies write access inside a transaction that is immediately rolled back (`conn.rollback()`). This guarantees existing user tables, calculation history, and records are never modified, committed, or deleted. If an existing database file is read-only (`chmod 0o444`), corrupt, or unusable, ONVEST automatically falls back to the next candidate.
  2. **New Database Directory Verification:** If `onvest.db` does not yet exist, ONVEST verifies directory write permissions using a uniquely named temporary SQLite probe database (`.probe_write_<uuid>.tmp`). The probe file and any SQLite sidecars (`-journal`, `-wal`, `-shm`) are safely unlinked in a strict `finally` block. If probe cleanup fails (e.g. file cannot be unlinked), the error is not suppressed: the candidate is rejected, a diagnostic failure reason is retained, and pre-existing user files are never deleted.
  
  The ordered candidate hierarchy is:
  1. **Primary (`%LOCALAPPDATA%/ONVEST/onvest.db`):** Selected during standard Windows desktop sessions where per-user application data storage is available.
  2. **Secondary (`~/.onvest/onvest.db`):** Selected if `%LOCALAPPDATA%` is unset, invalid, read-only, or lacks write permissions.
  3. **Portable Fallback (`<project_root>/data/onvest.db`):** Selected when running in portable mode, sandboxed test harnesses, or restricted profiles.
  
  Normal insert, read, count, and delete operations are fully verified across whichever candidate path is selected. If every candidate location is unwritable or unusable, a clear and actionable `PermissionError` is raised with full diagnostic details. All automated database tests strictly inject isolated temporary directories and never access or modify real user or project databases.

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
│   ├── test_emi.py             # 23 comprehensive unit tests for EMI math, rounding, and validation
│   ├── test_sip.py             # 12 unit tests for SIP math, effective durations, and validation
│   ├── test_database.py        # 19 unit tests for SQLite storage, delete, clear, rollback, isolated paths, and safe probing
│   └── test_ui_smoke.py        # 9 programmatic smoke tests for UI, visible navigation, and save guards
│
├── requirements.txt            # Minimal third-party dependencies (customtkinter)
└── README.md                   # Complete documentation
```

---

## 🛠️ Installation & Setup (Portable Windows Guide)

### Prerequisites
- Python 3.10+ (tested on Python 3.13)
- Windows 10 or Windows 11

### 1. Open Workspace / Project Directory
When opening a PowerShell or Command Prompt terminal, always enclose paths in quotes if directories contain spaces:

```powershell
cd "c:\Users\Manish\OneDrive\Projects\Onvest Main"
```

### 2. (Recommended) Virtual Environment Setup
To keep dependencies cleanly isolated and portable:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

### 3. Install Dependencies
Install the required GUI library using pip:

```powershell
pip install -r requirements.txt
```
*(Only `customtkinter>=6.0.0` is required. All other libraries—`sqlite3`, `math`, `datetime`, `pathlib`, `unittest`—are built into Python standard library).*

---

## 💻 Running the Application

To launch ONVEST:

```powershell
python main.py
```

If your Windows environment has multiple Python versions or Microsoft Store alias conflicts, invoke the exact Python binary using quoted execution syntax:

```powershell
& "C:\Users\Manish\AppData\Local\Programs\Python\Python313\python.exe" main.py
```

---

## 🧪 Running Automated Tests

Run the full automated test suite using Python's built-in `unittest` runner:

```powershell
python -m unittest discover -s tests -p "test_*.py" -v
```

Or run the specific core test modules:

```powershell
python -m unittest tests.test_emi tests.test_sip tests.test_database tests.test_ui_smoke -v
```

### Test Coverage Summary (63 Tests Total):
- **`test_emi.py`** (23 tests):
  1. Normal loan calculation ($10,00,000 @ 10% for 5 years)
  2. Zero-interest loan ($1,20,000 @ 0% for 1 year)
  3. Small loan amount ($5,00,000 @ 12% for 6 months)
  4. Very small loan principal ($10 loan with non-negative interest and ratio checks)
  5. Very low interest rate ($100,000 @ 0.01% p.a.)
  6. Total repayment and interest exact mathematical consistency
  7. Final installment normal loan with paise difference ($100,000 @ 12% 1yr -> 11x 8884.88 + 8884.87)
  8. Final installment very low rate with long tenure ($1,234.56 @ 0.01% 50yr -> 599x 2.06 + 3.71)
  9. Final installment very long tenure (30 years)
  10. Final installment zero-interest loan
  11. Final installment very small valid principal
  12. Final installment single-month tenure ($n = 1$)
  13. Paise rounding boundaries with awkward decimal values
  14. Effective duration normalization (1.04y -> 1.0y, 1.5y -> 1.5y, 2.25y -> 2.25y)
  15. Long loan tenure ($5,00,000 @ 8.5% for 30 years)
  16. Maximum tenure bound ($1,000,000 @ 9.0% for 50 years)
  17. Unrepresentable sub-paisa EMI handling (< 1 paisa raises clear ValueError)
  18. Invalid zero principal rejection
  19. Invalid negative principal rejection
  20. Invalid tenure rejection (zero, negative, >50 years)
  21. NaN and Infinity rejection (string and direct numeric inputs)
  22. Final installment financial transparency regression (installment sum equality, total interest equality, positivity and finiteness, zero-interest loans)
  23. Option A theoretical-total convention regression test ($5,00,000 @ 10.5% for 3 years: EMI ₹16,251.22, final payment ₹16,251.28, total repayment ₹5,85,043.98)
- **`test_sip.py`** (12 tests):
  1. Normal SIP calculation ($10,00,000/mo @ 12% for 10 years)
  2. Zero-return calculation ($5,00,000/mo @ 0% for 2 years)
  3. Effective duration normalization & fractional years (1.04y, 1.5y, 2.25y)
  4. Small monthly investment ($500/mo @ 15% for 1 year)
  5. Long investment duration ($5,000/mo @ 12% for 30 years)
  6. Very large valid inputs ($10,000,000/mo @ 15% for 30 years)
  7. Invalid zero investment rejection
  8. Invalid negative investment rejection
  9. Invalid duration rejection (zero, negative, >50 years)
  10. NaN rejection (string and direct numeric inputs)
  11. Infinity rejection (positive and negative infinity, string and numeric)
  12. Empty and alphabetic string validation
- **`test_database.py`** (19 tests):
  1. Database and table schema initialization
  2. Saving EMI calculation with parameterized queries
  3. Saving SIP calculation with parameterized queries
  4. Retrieving history sorted newest first
  5. Deleting an individual record
  6. Clearing all history safely
  7. Transaction rollback on invalid record save preserving existing data
  8. Failed clear history does not report success on database errors
  9. More than 100 records counting accuracy
  10. Count refresh after deletion and clearing
  11. Safe write-access probe and path verification on `get_default_db_path()` (isolated in temp directory)
  12. Safe probe cleanup: leaves no temporary files or SQLite sidecars behind
  13. Collision-safe probe: pre-existing `_onvest_write_probe` table and data remain completely untouched (isolated fixture)
  14. Multi-tier database fallback when higher-priority locations are unwritable and clear `PermissionError` if all fail
  15. Existing writable database verification via rolled-back transaction preserving tables and records
  16. Existing read-only candidate database detection and fallback
  17. Existing corrupt candidate database detection and fallback
  18. Pre-existing user files preserved: probe cleanup never deletes existing files on success or failure
  19. Probe cleanup failure rejection: ensures failure to unlink probe files rejects candidate, retains diagnostic, and never deletes pre-existing files
- **`test_ui_smoke.py`** (9 tests):
  1. Window and all 5 view pages initialization
  2. Navigation flow (programmatic regression verification that sidebar button clicks and `navigate_to()` actively map the selected page with `winfo_manager() == 'grid'`, raise it to the top of the stacking order, unmap all inactive pages with `grid_remove()`, and verify Dashboard quick-access routes to EMI and SIP)
  3. Standard EMI calculation and save
  4. EMI save after changing inputs prevents saving stale previous calculations
  5. EMI invalid current inputs cannot save previous calculations
  6. SIP save after changing inputs prevents saving stale previous calculations
  7. SIP invalid current inputs cannot save previous calculations
  8. History UI accurate count display and clear refresh
  9. Disclaimers and rounding explanations present in EMI and SIP UI results

---

## ⚖️ Financial Disclaimers

1. **Loan EMI Estimates:**
   > *"This is an estimated reducing-balance EMI calculation. The displayed final installment adjusts for rounding differences. Actual lender repayment schedules may differ due to payment dates, daily interest calculations, fees, and lender-specific rounding policies."*
2. **Mutual Fund Market Risk & SIP Estimates:**
   > *"SIP projections are illustrative estimates and actual mutual fund returns are market-dependent and not guaranteed. Projected returns are based on assumed constant compounding rates for illustration purposes and must not be regarded as guaranteed or assured returns. Future value calculations exclude taxes, exit loads, and expense ratios. Past market performance is not indicative of future returns."*

---

## 📄 License
Academic & Educational Project — All Rights Reserved.
