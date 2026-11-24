"""
Loan EMI Calculator View for ONVEST.
Implements input forms, validation, calculation triggering,
financial summary cards, visual proportional breakdown, and SQLite persistence.
"""

import customtkinter as ctk
from typing import Optional
from calculations.emi import calculate_emi, validate_emi_inputs, EMICalculationResult
from database.history import save_calculation
from ui.styles import (
    BG_MAIN,
    BG_CARD,
    BG_INPUT,
    BG_INPUT_BORDER,
    BORDER_COLOR,
    PRIMARY_BLUE,
    PRIMARY_BLUE_HOVER,
    EMERALD_GREEN,
    EMERALD_GREEN_HOVER,
    ERROR_RED,
    TEXT_MAIN,
    TEXT_SECONDARY,
    TEXT_MUTED,
    FONT_TITLE,
    FONT_SUBTITLE,
    FONT_HEADING,
    FONT_BODY,
    FONT_BODY_BOLD,
    FONT_BODY_SMALL,
    FONT_BADGE,
    format_inr,
)
from ui.components import MetricCard, ProportionalBar, SectionHeader


class EMIPage(ctk.CTkScrollableFrame):
    """Loan EMI Calculator interface with input validation and SQLite saving."""

    def __init__(self, master, on_history_updated=None, **kwargs):
        super().__init__(master, fg_color=BG_MAIN, corner_radius=0, **kwargs)
        self.on_history_updated = on_history_updated
        self.last_result: Optional[EMICalculationResult] = None

        self._build_header()
        self._build_content_grid()

    def _build_header(self):
        """Top section header."""
        header = SectionHeader(
            self,
            title="Loan EMI Calculator",
            subtitle="Calculate Equated Monthly Installments, total interest payable, and comprehensive loan repayment schedule.",
        )
        header.pack(fill="x", padx=24, pady=(20, 10))

    def _build_content_grid(self):
        """Split view: Left = Input Form, Right = Results & Proportional Breakdown."""
        container = ctk.CTkFrame(self, fg_color="transparent")
        container.pack(fill="both", expand=True, padx=24, pady=(0, 24))
        container.grid_columnconfigure(0, weight=4)  # Inputs
        container.grid_columnconfigure(1, weight=5)  # Results

        # --- LEFT: INPUT CARD ---
        input_card = ctk.CTkFrame(
            container,
            fg_color=BG_CARD,
            corner_radius=12,
            border_width=1,
            border_color=BORDER_COLOR,
        )
        input_card.grid(row=0, column=0, sticky="nsew", padx=(0, 12))

        inner_input = ctk.CTkFrame(input_card, fg_color="transparent")
        inner_input.pack(fill="both", expand=True, padx=22, pady=20)

        ctk.CTkLabel(
            inner_input,
            text="LOAN PARAMETERS",
            font=FONT_BADGE,
            text_color=PRIMARY_BLUE,
            anchor="w",
        ).pack(fill="x", pady=(0, 14))

        # Input 1: Principal Amount
        ctk.CTkLabel(
            inner_input,
            text="Loan Principal Amount (₹):",
            font=FONT_BODY_BOLD,
            text_color=TEXT_MAIN,
            anchor="w",
        ).pack(fill="x", pady=(0, 4))

        self.principal_entry = ctk.CTkEntry(
            inner_input,
            placeholder_text="e.g. 1000000 (10 Lakhs)",
            font=FONT_BODY,
            fg_color=BG_INPUT,
            border_color=BG_INPUT_BORDER,
            text_color=TEXT_MAIN,
            height=38,
            corner_radius=8,
        )
        self.principal_entry.pack(fill="x", pady=(0, 14))

        # Input 2: Annual Interest Rate
        ctk.CTkLabel(
            inner_input,
            text="Annual Interest Rate (% p.a.):",
            font=FONT_BODY_BOLD,
            text_color=TEXT_MAIN,
            anchor="w",
        ).pack(fill="x", pady=(0, 4))

        self.rate_entry = ctk.CTkEntry(
            inner_input,
            placeholder_text="e.g. 8.5",
            font=FONT_BODY,
            fg_color=BG_INPUT,
            border_color=BG_INPUT_BORDER,
            text_color=TEXT_MAIN,
            height=38,
            corner_radius=8,
        )
        self.rate_entry.pack(fill="x", pady=(0, 14))

        # Input 3: Tenure in Years
        ctk.CTkLabel(
            inner_input,
            text="Loan Tenure (Years):",
            font=FONT_BODY_BOLD,
            text_color=TEXT_MAIN,
            anchor="w",
        ).pack(fill="x", pady=(0, 4))

        self.tenure_entry = ctk.CTkEntry(
            inner_input,
            placeholder_text="e.g. 5 (Max 50 years)",
            font=FONT_BODY,
            fg_color=BG_INPUT,
            border_color=BG_INPUT_BORDER,
            text_color=TEXT_MAIN,
            height=38,
            corner_radius=8,
        )
        self.tenure_entry.pack(fill="x", pady=(0, 14))

        # Feedback & Error Display
        self.feedback_label = ctk.CTkLabel(
            inner_input,
            text="",
            font=FONT_BODY_SMALL,
            text_color=ERROR_RED,
            wraplength=320,
            justify="left",
            anchor="w",
        )
        self.feedback_label.pack(fill="x", pady=(0, 10))

        # Action Buttons
        btn_box = ctk.CTkFrame(inner_input, fg_color="transparent")
        btn_box.pack(fill="x", pady=(0, 10))
        btn_box.grid_columnconfigure(0, weight=3)
        btn_box.grid_columnconfigure(1, weight=2)

        self.calc_btn = ctk.CTkButton(
            btn_box,
            text="Calculate EMI",
            font=FONT_BODY_BOLD,
            fg_color=PRIMARY_BLUE,
            hover_color=PRIMARY_BLUE_HOVER,
            text_color=TEXT_MAIN,
            height=40,
            corner_radius=8,
            command=self._handle_calculate,
        )
        self.calc_btn.grid(row=0, column=0, sticky="ew", padx=(0, 6))

        self.reset_btn = ctk.CTkButton(
            btn_box,
            text="Reset",
            font=FONT_BODY_BOLD,
            fg_color="#334155",
            hover_color="#475569",
            text_color=TEXT_MAIN,
            height=40,
            corner_radius=8,
            command=self._handle_reset,
        )
        self.reset_btn.grid(row=0, column=1, sticky="ew", padx=(6, 0))

        # Save Calculation Button
        self.save_btn = ctk.CTkButton(
            inner_input,
            text="Save Calculation to History",
            font=FONT_BODY_BOLD,
            fg_color=EMERALD_GREEN,
            hover_color=EMERALD_GREEN_HOVER,
            text_color=TEXT_MAIN,
            height=38,
            corner_radius=8,
            command=self._handle_save,
        )
        self.save_btn.pack(fill="x", pady=(4, 0))

        # --- RIGHT: RESULTS & BREAKDOWN ---
        self.results_container = ctk.CTkFrame(container, fg_color="transparent")
        self.results_container.grid(row=0, column=1, sticky="nsew", padx=(12, 0))

        # Primary Metric: Monthly EMI
        self.emi_card = MetricCard(
            self.results_container,
            title="Monthly Equated Installment (EMI)",
            initial_value="₹0.00",
            caption="Calculated based on reducing balance method",
            highlight_color=PRIMARY_BLUE,
            is_primary=True,
        )
        self.emi_card.pack(fill="x", pady=(0, 12))

        # Secondary 2x1 Grid for Principal & Interest
        sub_grid = ctk.CTkFrame(self.results_container, fg_color="transparent")
        sub_grid.pack(fill="x", pady=(0, 12))
        sub_grid.grid_columnconfigure(0, weight=1)
        sub_grid.grid_columnconfigure(1, weight=1)

        self.principal_card = MetricCard(
            sub_grid,
            title="Principal Loan Amount",
            initial_value="₹0.00",
            caption="Base borrowed capital",
        )
        self.principal_card.grid(row=0, column=0, sticky="nsew", padx=(0, 6))

        self.interest_card = MetricCard(
            sub_grid,
            title="Total Interest Payable",
            initial_value="₹0.00",
            caption="Cumulative cost of borrowing",
            highlight_color="#F59E0B",
        )
        self.interest_card.grid(row=0, column=1, sticky="nsew", padx=(6, 0))

        # Total Repayment Metric Card
        self.total_card = MetricCard(
            self.results_container,
            title="Total Repayment Amount (Principal + Interest)",
            initial_value="₹0.00",
            caption="Total outflow over the entire tenure",
        )
        self.total_card.pack(fill="x", pady=(0, 12))

        # Visual Proportional Breakdown Bar
        self.breakdown_bar = ProportionalBar(
            self.results_container,
            left_label="Principal",
            right_label="Interest",
            left_color=PRIMARY_BLUE,
            right_color="#F59E0B",
        )
        self.breakdown_bar.pack(fill="x")

    def _show_error(self, message: str):
        """Displays error message and resets confirmation."""
        self.feedback_label.configure(text=f"⚠ {message}", text_color=ERROR_RED)

    def _show_success(self, message: str):
        """Displays success message."""
        self.feedback_label.configure(text=f"✓ {message}", text_color=EMERALD_GREEN)

    def _clear_feedback(self):
        """Clears feedback label."""
        self.feedback_label.configure(text="")

    def _handle_calculate(self):
        """Validates inputs and computes EMI."""
        self._clear_feedback()
        p_str = self.principal_entry.get()
        r_str = self.rate_entry.get()
        t_str = self.tenure_entry.get()

        try:
            p, r, t = validate_emi_inputs(p_str, r_str, t_str)
            res = calculate_emi(p, r, t)
            self.last_result = res

            # Update Metric Display
            self.emi_card.update_value(
                format_inr(res.monthly_emi),
                f"Payable monthly for {res.tenure_months} installments ({res.tenure_years} yrs)",
            )
            self.principal_card.update_value(
                format_inr(res.principal),
                f"{res.principal_ratio * 100:.1f}% of total repayment",
            )
            self.interest_card.update_value(
                format_inr(res.total_interest),
                f"{res.interest_ratio * 100:.1f}% of total repayment",
            )
            self.total_card.update_value(
                format_inr(res.total_repayment),
                f"Principal {format_inr(res.principal)} + Interest {format_inr(res.total_interest)}",
            )

            # Update Visual Breakdown Bar
            self.breakdown_bar.update_ratios(
                left_ratio=res.principal_ratio,
                right_ratio=res.interest_ratio,
                left_amount=res.principal,
                right_amount=res.total_interest,
            )

        except ValueError as e:
            self.last_result = None
            self._show_error(str(e))
        except Exception as e:
            self.last_result = None
            self._show_error(f"Unexpected calculation error: {e}")

    def _handle_reset(self):
        """Resets all input fields and calculation results."""
        self.principal_entry.delete(0, "end")
        self.rate_entry.delete(0, "end")
        self.tenure_entry.delete(0, "end")
        self.last_result = None
        self._clear_feedback()

        self.emi_card.update_value("₹0.00", "Calculated based on reducing balance method")
        self.principal_card.update_value("₹0.00", "Base borrowed capital")
        self.interest_card.update_value("₹0.00", "Cumulative cost of borrowing")
        self.total_card.update_value("₹0.00", "Total outflow over the entire tenure")
        self.breakdown_bar.update_ratios(0.5, 0.5, 0, 0)

    def _handle_save(self):
        """Saves current calculation to SQLite database."""
        if self.last_result is None:
            # Try computing first
            self._handle_calculate()
            if self.last_result is None:
                self._show_error("Please enter valid loan details and calculate before saving.")
                return

        res = self.last_result
        calc_record = {
            "calc_type": "EMI",
            "principal_or_monthly": res.principal,
            "annual_rate": res.annual_rate,
            "duration_months": res.tenure_months,
            "monthly_amount": res.monthly_emi,
            "total_interest_or_returns": res.total_interest,
            "total_amount": res.total_repayment,
        }

        try:
            rec_id = save_calculation(calc_record)
            self._show_success(f"Calculation saved to history! (Record #{rec_id})")
            if self.on_history_updated:
                self.on_history_updated()
        except Exception as e:
            self._show_error(f"Failed to save calculation: {e}")
