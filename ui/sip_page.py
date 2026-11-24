"""
SIP Calculator View for ONVEST.
Implements Systematic Investment Plan input forms, validation,
future value projection, visual breakdown, market disclaimer, and SQLite persistence.
"""

import customtkinter as ctk
from typing import Optional
from calculations.sip import calculate_sip, validate_sip_inputs, SIPCalculationResult
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


class SIPPage(ctk.CTkScrollableFrame):
    """SIP Calculator interface with compound wealth projection and SQLite persistence."""

    def __init__(self, master, on_history_updated=None, **kwargs):
        super().__init__(master, fg_color=BG_MAIN, corner_radius=0, **kwargs)
        self.on_history_updated = on_history_updated
        self.last_result: Optional[SIPCalculationResult] = None

        self._build_header()
        self._build_content_grid()

    def _build_header(self):
        """Top section header."""
        header = SectionHeader(
            self,
            title="SIP Calculator",
            subtitle="Project potential compound wealth creation through Systematic Investment Plans in mutual funds.",
        )
        header.pack(fill="x", padx=24, pady=(20, 10))

    def _build_content_grid(self):
        """Split view: Left = Input Form, Right = Projected Results & Visual Breakdown."""
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
            text="INVESTMENT PARAMETERS",
            font=FONT_BADGE,
            text_color=EMERALD_GREEN,
            anchor="w",
        ).pack(fill="x", pady=(0, 14))

        # Input 1: Monthly Investment Amount
        ctk.CTkLabel(
            inner_input,
            text="Monthly Investment (₹):",
            font=FONT_BODY_BOLD,
            text_color=TEXT_MAIN,
            anchor="w",
        ).pack(fill="x", pady=(0, 4))

        self.monthly_entry = ctk.CTkEntry(
            inner_input,
            placeholder_text="e.g. 5000",
            font=FONT_BODY,
            fg_color=BG_INPUT,
            border_color=BG_INPUT_BORDER,
            text_color=TEXT_MAIN,
            height=38,
            corner_radius=8,
        )
        self.monthly_entry.pack(fill="x", pady=(0, 14))

        # Input 2: Expected Annual Return Rate
        ctk.CTkLabel(
            inner_input,
            text="Expected Return Rate (% p.a.):",
            font=FONT_BODY_BOLD,
            text_color=TEXT_MAIN,
            anchor="w",
        ).pack(fill="x", pady=(0, 4))

        self.rate_entry = ctk.CTkEntry(
            inner_input,
            placeholder_text="e.g. 12.0",
            font=FONT_BODY,
            fg_color=BG_INPUT,
            border_color=BG_INPUT_BORDER,
            text_color=TEXT_MAIN,
            height=38,
            corner_radius=8,
        )
        self.rate_entry.pack(fill="x", pady=(0, 14))

        # Input 3: Investment Duration
        ctk.CTkLabel(
            inner_input,
            text="Investment Duration (Years):",
            font=FONT_BODY_BOLD,
            text_color=TEXT_MAIN,
            anchor="w",
        ).pack(fill="x", pady=(0, 4))

        self.duration_entry = ctk.CTkEntry(
            inner_input,
            placeholder_text="e.g. 10 (Max 50 years)",
            font=FONT_BODY,
            fg_color=BG_INPUT,
            border_color=BG_INPUT_BORDER,
            text_color=TEXT_MAIN,
            height=38,
            corner_radius=8,
        )
        self.duration_entry.pack(fill="x", pady=(0, 14))

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
            text="Calculate SIP",
            font=FONT_BODY_BOLD,
            fg_color=EMERALD_GREEN,
            hover_color=EMERALD_GREEN_HOVER,
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
            fg_color=PRIMARY_BLUE,
            hover_color=PRIMARY_BLUE_HOVER,
            text_color=TEXT_MAIN,
            height=38,
            corner_radius=8,
            command=self._handle_save,
        )
        self.save_btn.pack(fill="x", pady=(4, 0))

        # --- RIGHT: RESULTS & BREAKDOWN ---
        self.results_container = ctk.CTkFrame(container, fg_color="transparent")
        self.results_container.grid(row=0, column=1, sticky="nsew", padx=(12, 0))

        # Primary Metric: Estimated Future Value
        self.fv_card = MetricCard(
            self.results_container,
            title="Estimated Future Value (Maturity Corpus)",
            initial_value="₹0.00",
            caption="Projected maturity corpus including compound gains",
            highlight_color=EMERALD_GREEN,
            is_primary=True,
        )
        self.fv_card.pack(fill="x", pady=(0, 12))

        # Secondary 2x1 Grid for Invested vs Estimated Returns
        sub_grid = ctk.CTkFrame(self.results_container, fg_color="transparent")
        sub_grid.pack(fill="x", pady=(0, 12))
        sub_grid.grid_columnconfigure(0, weight=1)
        sub_grid.grid_columnconfigure(1, weight=1)

        self.invested_card = MetricCard(
            sub_grid,
            title="Total Invested Amount",
            initial_value="₹0.00",
            caption="Total capital contributed",
            highlight_color=PRIMARY_BLUE,
        )
        self.invested_card.grid(row=0, column=0, sticky="nsew", padx=(0, 6))

        self.returns_card = MetricCard(
            sub_grid,
            title="ESTIMATED RETURNS",
            initial_value="₹0.00",
            caption="Capital appreciation from compounding",
            highlight_color=EMERALD_GREEN,
        )
        self.returns_card.grid(row=0, column=1, sticky="nsew", padx=(6, 0))

        # Visual Proportional Breakdown Bar
        self.breakdown_bar = ProportionalBar(
            self.results_container,
            left_label="Invested Amount",
            right_label="Estimated Gains",
            left_color=PRIMARY_BLUE,
            right_color=EMERALD_GREEN,
        )
        self.breakdown_bar.pack(fill="x", pady=(0, 12))

        # Regulatory & Market Risk Disclaimer (Mandatory)
        disclaimer_card = ctk.CTkFrame(
            self.results_container,
            fg_color=BG_CARD,
            corner_radius=10,
            border_width=1,
            border_color=BORDER_COLOR,
        )
        disclaimer_card.pack(fill="x")

        d_inner = ctk.CTkFrame(disclaimer_card, fg_color="transparent")
        d_inner.pack(fill="x", padx=16, pady=12)

        ctk.CTkLabel(
            d_inner,
            text="IMPORTANT FINANCIAL DISCLAIMER",
            font=FONT_BADGE,
            text_color="#F59E0B",
            anchor="w",
        ).pack(fill="x", pady=(0, 4))

        disclaimer_text = (
            "SIP projections are illustrative estimates and actual mutual fund returns are "
            "market-dependent and not guaranteed. Future value calculations exclude taxes, exit loads, "
            "and expense ratios. Past market performance is not indicative of future returns."
        )
        ctk.CTkLabel(
            d_inner,
            text=disclaimer_text,
            font=FONT_BODY_SMALL,
            text_color=TEXT_MUTED,
            wraplength=480,
            justify="left",
            anchor="w",
        ).pack(fill="x")

    def _show_error(self, message: str):
        """Displays error message."""
        self.feedback_label.configure(text=f"⚠ {message}", text_color=ERROR_RED)

    def _show_success(self, message: str):
        """Displays success message."""
        self.feedback_label.configure(text=f"✓ {message}", text_color=EMERALD_GREEN)

    def _clear_feedback(self):
        """Clears feedback label."""
        self.feedback_label.configure(text="")

    def _handle_calculate(self):
        """Validates inputs and computes SIP projections."""
        self._clear_feedback()
        m_str = self.monthly_entry.get()
        r_str = self.rate_entry.get()
        d_str = self.duration_entry.get()

        try:
            m, r, d = validate_sip_inputs(m_str, r_str, d_str)
            res = calculate_sip(m, r, d)
            self.last_result = res

            # Update Metric Display
            self.fv_card.update_value(
                format_inr(res.future_value),
                f"Projected maturity value after {res.duration_years} years ({res.duration_months} monthly installments)",
            )
            self.invested_card.update_value(
                format_inr(res.total_invested),
                f"{res.invested_ratio * 100:.1f}% of final projected value",
            )
            self.returns_card.update_value(
                format_inr(res.estimated_returns),
                f"{res.returns_ratio * 100:.1f}% estimated capital growth",
            )

            # Update Visual Breakdown Bar
            self.breakdown_bar.update_ratios(
                left_ratio=res.invested_ratio,
                right_ratio=res.returns_ratio,
                left_amount=res.total_invested,
                right_amount=res.estimated_returns,
            )

        except ValueError as e:
            self.last_result = None
            self._show_error(str(e))
        except Exception as e:
            self.last_result = None
            self._show_error(f"Unexpected calculation error: {e}")

    def _handle_reset(self):
        """Resets all input fields and calculation results."""
        self.monthly_entry.delete(0, "end")
        self.rate_entry.delete(0, "end")
        self.duration_entry.delete(0, "end")
        self.last_result = None
        self._clear_feedback()

        self.fv_card.update_value("₹0.00", "Projected maturity corpus including compound gains")
        self.invested_card.update_value("₹0.00", "Total capital contributed")
        self.returns_card.update_value("₹0.00", "Capital appreciation from compounding")
        self.breakdown_bar.update_ratios(0.5, 0.5, 0, 0)

    def _handle_save(self):
        """Saves current calculation to SQLite database."""
        if self.last_result is None:
            self._handle_calculate()
            if self.last_result is None:
                self._show_error("Please enter valid investment details and calculate before saving.")
                return

        res = self.last_result
        calc_record = {
            "calc_type": "SIP",
            "principal_or_monthly": res.monthly_investment,
            "annual_rate": res.annual_return_rate,
            "duration_months": res.duration_months,
            "monthly_amount": res.monthly_investment,
            "total_interest_or_returns": res.estimated_returns,
            "total_amount": res.future_value,
        }

        try:
            rec_id = save_calculation(calc_record)
            self._show_success(f"Calculation saved to history! (Record #{rec_id})")
            if self.on_history_updated:
                self.on_history_updated()
        except Exception as e:
            self._show_error(f"Failed to save calculation: {e}")
