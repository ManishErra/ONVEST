"""
Dashboard view for ONVEST.
Displays application branding, key metrics, quick access buttons,
latest saved calculation summary, and introductory guides for EMI & SIP tools.
"""

import customtkinter as ctk
from typing import Callable, Optional
from database.history import get_calculation_count, get_latest_calculation
from ui.styles import (
    BG_MAIN,
    BG_CARD,
    BG_CARD_HOVER,
    PRIMARY_BLUE,
    PRIMARY_BLUE_HOVER,
    EMERALD_GREEN,
    EMERALD_GREEN_HOVER,
    TEXT_MAIN,
    TEXT_SECONDARY,
    TEXT_MUTED,
    BORDER_COLOR,
    FONT_TITLE,
    FONT_SUBTITLE,
    FONT_HEADING,
    FONT_BODY,
    FONT_BODY_BOLD,
    FONT_BODY_SMALL,
    FONT_BIG_METRIC,
    FONT_MID_METRIC,
    FONT_BADGE,
    format_inr,
)


class DashboardPage(ctk.CTkScrollableFrame):
    """Dashboard page showing live statistics and quick navigation."""

    def __init__(self, master, navigate_callback: Callable[[str], None], **kwargs):
        super().__init__(master, fg_color=BG_MAIN, corner_radius=0, **kwargs)
        self.navigate_callback = navigate_callback

        self._build_header()
        self._build_stats_row()
        self._build_quick_access()
        self._build_feature_cards()

        # Load real database data
        self.refresh_data()

    def _build_header(self):
        """Top banner with greeting and description."""
        banner = ctk.CTkFrame(
            self,
            fg_color=BG_CARD,
            corner_radius=12,
            border_width=1,
            border_color=BORDER_COLOR,
        )
        banner.pack(fill="x", padx=24, pady=(20, 16))

        content = ctk.CTkFrame(banner, fg_color="transparent")
        content.pack(fill="x", padx=24, pady=20)

        # Tagline badge
        badge = ctk.CTkLabel(
            content,
            text="FINANCIAL PLANNING SUITE",
            font=FONT_BADGE,
            text_color=EMERALD_GREEN,
            anchor="w",
        )
        badge.pack(fill="x", pady=(0, 4))

        # Title
        title = ctk.CTkLabel(
            content,
            text="Welcome to ONVEST",
            font=FONT_TITLE,
            text_color=TEXT_MAIN,
            anchor="w",
        )
        title.pack(fill="x", pady=(0, 4))

        # Description
        desc = ctk.CTkLabel(
            content,
            text=(
                "Smart, precise, and completely offline financial calculation toolkit. "
                "Plan loan amortization with the Loan EMI Calculator or project compound wealth "
                "accumulation with the Systematic Investment Plan (SIP) Calculator."
            ),
            font=FONT_BODY,
            text_color=TEXT_SECONDARY,
            wraplength=760,
            justify="left",
            anchor="w",
        )
        desc.pack(fill="x")

    def _build_stats_row(self):
        """Displays total saved calculations and the latest calculation summary."""
        stats_frame = ctk.CTkFrame(self, fg_color="transparent")
        stats_frame.pack(fill="x", padx=24, pady=(0, 16))
        stats_frame.grid_columnconfigure(0, weight=1)
        stats_frame.grid_columnconfigure(1, weight=2)

        # Card 1: Total Saved Calculations
        self.count_card = ctk.CTkFrame(
            stats_frame,
            fg_color=BG_CARD,
            corner_radius=12,
            border_width=1,
            border_color=BORDER_COLOR,
        )
        self.count_card.grid(row=0, column=0, sticky="nsew", padx=(0, 10))

        count_content = ctk.CTkFrame(self.count_card, fg_color="transparent")
        count_content.pack(fill="both", expand=True, padx=20, pady=16)

        ctk.CTkLabel(
            count_content,
            text="SAVED CALCULATIONS",
            font=FONT_BADGE,
            text_color=TEXT_SECONDARY,
            anchor="w",
        ).pack(fill="x", pady=(0, 4))

        self.count_val_label = ctk.CTkLabel(
            count_content,
            text="0",
            font=FONT_BIG_METRIC,
            text_color=PRIMARY_BLUE,
            anchor="w",
        )
        self.count_val_label.pack(fill="x", pady=(0, 2))

        self.count_sub_label = ctk.CTkLabel(
            count_content,
            text="Stored securely in local SQLite database",
            font=FONT_BODY_SMALL,
            text_color=TEXT_MUTED,
            anchor="w",
        )
        self.count_sub_label.pack(fill="x")

        # Card 2: Latest Calculation Summary
        self.latest_card = ctk.CTkFrame(
            stats_frame,
            fg_color=BG_CARD,
            corner_radius=12,
            border_width=1,
            border_color=BORDER_COLOR,
        )
        self.latest_card.grid(row=0, column=1, sticky="nsew", padx=(10, 0))

        latest_content = ctk.CTkFrame(self.latest_card, fg_color="transparent")
        latest_content.pack(fill="both", expand=True, padx=20, pady=16)

        ctk.CTkLabel(
            latest_content,
            text="MOST RECENT ACTIVITY",
            font=FONT_BADGE,
            text_color=TEXT_SECONDARY,
            anchor="w",
        ).pack(fill="x", pady=(0, 4))

        self.latest_headline_label = ctk.CTkLabel(
            latest_content,
            text="No calculations saved yet",
            font=FONT_HEADING,
            text_color=TEXT_MAIN,
            anchor="w",
        )
        self.latest_headline_label.pack(fill="x", pady=(0, 2))

        self.latest_detail_label = ctk.CTkLabel(
            latest_content,
            text="Perform and save an EMI or SIP calculation to see details here.",
            font=FONT_BODY_SMALL,
            text_color=TEXT_MUTED,
            anchor="w",
        )
        self.latest_detail_label.pack(fill="x")

    def _build_quick_access(self):
        """Action cards for quick navigation directly to calculators."""
        qa_frame = ctk.CTkFrame(self, fg_color="transparent")
        qa_frame.pack(fill="x", padx=24, pady=(0, 16))
        qa_frame.grid_columnconfigure(0, weight=1)
        qa_frame.grid_columnconfigure(1, weight=1)

        # Quick access EMI
        emi_btn_card = ctk.CTkFrame(
            qa_frame,
            fg_color=BG_CARD,
            corner_radius=12,
            border_width=1,
            border_color=BORDER_COLOR,
        )
        emi_btn_card.grid(row=0, column=0, sticky="nsew", padx=(0, 10))

        emi_inner = ctk.CTkFrame(emi_btn_card, fg_color="transparent")
        emi_inner.pack(fill="both", expand=True, padx=20, pady=18)

        ctk.CTkLabel(
            emi_inner,
            text="LOAN PLANNING",
            font=FONT_BADGE,
            text_color=PRIMARY_BLUE,
            anchor="w",
        ).pack(fill="x")

        ctk.CTkLabel(
            emi_inner,
            text="Loan EMI Calculator",
            font=FONT_HEADING,
            text_color=TEXT_MAIN,
            anchor="w",
        ).pack(fill="x", pady=(2, 4))

        ctk.CTkLabel(
            emi_inner,
            text="Calculate monthly installments, interest breakdown, and overall repayment liability.",
            font=FONT_BODY_SMALL,
            text_color=TEXT_SECONDARY,
            wraplength=340,
            justify="left",
            anchor="w",
        ).pack(fill="x", pady=(0, 14))

        ctk.CTkButton(
            emi_inner,
            text="Open EMI Calculator →",
            font=FONT_BODY_BOLD,
            fg_color=PRIMARY_BLUE,
            hover_color=PRIMARY_BLUE_HOVER,
            text_color=TEXT_MAIN,
            height=38,
            corner_radius=8,
            command=lambda: self.navigate_callback("emi"),
        ).pack(fill="x")

        # Quick access SIP
        sip_btn_card = ctk.CTkFrame(
            qa_frame,
            fg_color=BG_CARD,
            corner_radius=12,
            border_width=1,
            border_color=BORDER_COLOR,
        )
        sip_btn_card.grid(row=0, column=1, sticky="nsew", padx=(10, 0))

        sip_inner = ctk.CTkFrame(sip_btn_card, fg_color="transparent")
        sip_inner.pack(fill="both", expand=True, padx=20, pady=18)

        ctk.CTkLabel(
            sip_inner,
            text="WEALTH CREATION",
            font=FONT_BADGE,
            text_color=EMERALD_GREEN,
            anchor="w",
        ).pack(fill="x")

        ctk.CTkLabel(
            sip_inner,
            text="SIP Growth Calculator",
            font=FONT_HEADING,
            text_color=TEXT_MAIN,
            anchor="w",
        ).pack(fill="x", pady=(2, 4))

        ctk.CTkLabel(
            sip_inner,
            text="Simulate monthly investments, compounding growth, and projected maturity values.",
            font=FONT_BODY_SMALL,
            text_color=TEXT_SECONDARY,
            wraplength=340,
            justify="left",
            anchor="w",
        ).pack(fill="x", pady=(0, 14))

        ctk.CTkButton(
            sip_inner,
            text="Open SIP Calculator →",
            font=FONT_BODY_BOLD,
            fg_color=EMERALD_GREEN,
            hover_color=EMERALD_GREEN_HOVER,
            text_color=TEXT_MAIN,
            height=38,
            corner_radius=8,
            command=lambda: self.navigate_callback("sip"),
        ).pack(fill="x")

    def _build_feature_cards(self):
        """Introductory informational cards explaining EMI and SIP concepts."""
        info_frame = ctk.CTkFrame(self, fg_color="transparent")
        info_frame.pack(fill="x", padx=24, pady=(0, 24))
        info_frame.grid_columnconfigure(0, weight=1)
        info_frame.grid_columnconfigure(1, weight=1)

        # EMI Guide Card
        card_emi = ctk.CTkFrame(
            info_frame,
            fg_color=BG_CARD,
            corner_radius=12,
            border_width=1,
            border_color=BORDER_COLOR,
        )
        card_emi.grid(row=0, column=0, sticky="nsew", padx=(0, 10))

        c1_content = ctk.CTkFrame(card_emi, fg_color="transparent")
        c1_content.pack(fill="both", expand=True, padx=20, pady=16)

        ctk.CTkLabel(
            c1_content,
            text="ABOUT EQUATED MONTHLY INSTALLMENTS",
            font=FONT_BADGE,
            text_color=TEXT_MUTED,
            anchor="w",
        ).pack(fill="x", pady=(0, 4))

        ctk.CTkLabel(
            c1_content,
            text="How Loan EMI Works",
            font=FONT_HEADING,
            text_color=TEXT_MAIN,
            anchor="w",
        ).pack(fill="x", pady=(0, 6))

        emi_guide = (
            "• An EMI consists of both principal reduction and monthly interest.\n"
            "• Early installments allocate more towards interest, while later ones pay down principal.\n"
            "• Shorter tenures incur higher monthly EMIs but save substantial interest overall.\n"
            "• Longer tenures reduce monthly burden but increase cumulative interest payout."
        )
        ctk.CTkLabel(
            c1_content,
            text=emi_guide,
            font=FONT_BODY_SMALL,
            text_color=TEXT_SECONDARY,
            justify="left",
            anchor="w",
        ).pack(fill="x")

        # SIP Guide Card
        card_sip = ctk.CTkFrame(
            info_frame,
            fg_color=BG_CARD,
            corner_radius=12,
            border_width=1,
            border_color=BORDER_COLOR,
        )
        card_sip.grid(row=0, column=1, sticky="nsew", padx=(10, 0))

        c2_content = ctk.CTkFrame(card_sip, fg_color="transparent")
        c2_content.pack(fill="both", expand=True, padx=20, pady=16)

        ctk.CTkLabel(
            c2_content,
            text="ABOUT SYSTEMATIC INVESTMENT PLANS",
            font=FONT_BADGE,
            text_color=TEXT_MUTED,
            anchor="w",
        ).pack(fill="x", pady=(0, 4))

        ctk.CTkLabel(
            c2_content,
            text="The Power of Compounding",
            font=FONT_HEADING,
            text_color=TEXT_MAIN,
            anchor="w",
        ).pack(fill="x", pady=(0, 6))

        sip_guide = (
            "• SIP encourages disciplined monthly savings regardless of market conditions.\n"
            "• Rupee cost averaging reduces the impact of short-term market volatility.\n"
            "• Compound returns generate exponential growth when maintained over long horizons.\n"
            "• Starting even 5 years earlier can more than double your eventual maturity corpus."
        )
        ctk.CTkLabel(
            c2_content,
            text=sip_guide,
            font=FONT_BODY_SMALL,
            text_color=TEXT_SECONDARY,
            justify="left",
            anchor="w",
        ).pack(fill="x")

    def refresh_data(self):
        """Refreshes live SQLite metrics on the dashboard."""
        try:
            count = get_calculation_count()
            self.count_val_label.configure(text=str(count))
            if count == 1:
                self.count_sub_label.configure(text="1 calculation saved in local database")
            else:
                self.count_sub_label.configure(text=f"{count} calculations saved in local database")

            latest = get_latest_calculation()
            if latest:
                calc_type = latest["calc_type"]
                created_at = latest["created_at"]

                if calc_type == "EMI":
                    principal = format_inr(latest["principal_or_monthly"])
                    emi = format_inr(latest["monthly_amount"])
                    rate = latest["annual_rate"]
                    duration_yr = round(latest["duration_months"] / 12, 1)

                    self.latest_headline_label.configure(
                        text=f"EMI: {emi}/mo for {principal} loan",
                        text_color=PRIMARY_BLUE,
                    )
                    self.latest_detail_label.configure(
                        text=f"{rate}% p.a. over {duration_yr} yrs • Saved on {created_at}",
                        text_color=TEXT_SECONDARY,
                    )
                else:
                    monthly = format_inr(latest["principal_or_monthly"])
                    fv = format_inr(latest["total_amount"])
                    rate = latest["annual_rate"]
                    duration_yr = round(latest["duration_months"] / 12, 1)

                    self.latest_headline_label.configure(
                        text=f"SIP: {monthly}/mo → Projected {fv}",
                        text_color=EMERALD_GREEN,
                    )
                    self.latest_detail_label.configure(
                        text=f"{rate}% expected return over {duration_yr} yrs • Saved on {created_at}",
                        text_color=TEXT_SECONDARY,
                    )
            else:
                self.latest_headline_label.configure(
                    text="No calculations saved yet",
                    text_color=TEXT_MAIN,
                )
                self.latest_detail_label.configure(
                    text="Perform and save an EMI or SIP calculation to see details here.",
                    text_color=TEXT_MUTED,
                )
        except Exception as e:
            self.count_val_label.configure(text="—")
            self.latest_headline_label.configure(text="Database unavailable")
            self.latest_detail_label.configure(text=str(e))
