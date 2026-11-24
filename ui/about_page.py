"""
About View for ONVEST.
Displays application identity, full title, tagline, description,
version, platform, technology stack, and essential financial disclaimers.
"""

import customtkinter as ctk
from database.history import get_db_path
from ui.styles import (
    BG_MAIN,
    BG_CARD,
    BORDER_COLOR,
    PRIMARY_BLUE,
    EMERALD_GREEN,
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
)
from ui.components import SectionHeader


class AboutPage(ctk.CTkScrollableFrame):
    """About page displaying software metadata, architectural info, and disclaimers."""

    def __init__(self, master, **kwargs):
        super().__init__(master, fg_color=BG_MAIN, corner_radius=0, **kwargs)

        self._build_header()
        self._build_app_identity()
        self._build_specifications()
        self._build_disclaimers()

    def _build_header(self):
        """Section Header."""
        header = SectionHeader(
            self,
            title="About ONVEST",
            subtitle="Application identity, software architecture, and financial disclosures.",
        )
        header.pack(fill="x", padx=24, pady=(20, 10))

    def _build_app_identity(self):
        """Application overview banner."""
        card = ctk.CTkFrame(
            self,
            fg_color=BG_CARD,
            corner_radius=12,
            border_width=1,
            border_color=BORDER_COLOR,
        )
        card.pack(fill="x", padx=24, pady=(0, 16))

        inner = ctk.CTkFrame(card, fg_color="transparent")
        inner.pack(fill="x", padx=24, pady=20)

        # Title & Subtitle
        ctk.CTkLabel(
            inner,
            text="ONVEST",
            font=FONT_TITLE,
            text_color=TEXT_MAIN,
            anchor="w",
        ).pack(fill="x")

        ctk.CTkLabel(
            inner,
            text="Loan EMI & SIP Calculator",
            font=FONT_SUBTITLE,
            text_color=PRIMARY_BLUE,
            anchor="w",
        ).pack(fill="x", pady=(2, 4))

        ctk.CTkLabel(
            inner,
            text="Tagline: Calculate. Invest. Grow.",
            font=FONT_BODY_BOLD,
            text_color=EMERALD_GREEN,
            anchor="w",
        ).pack(fill="x", pady=(0, 12))

        desc = (
            "ONVEST is an offline desktop financial planning application that helps users estimate "
            "loan repayments and understand potential investment growth through simple and accessible financial calculations."
        )
        ctk.CTkLabel(
            inner,
            text=desc,
            font=FONT_BODY,
            text_color=TEXT_SECONDARY,
            wraplength=760,
            justify="left",
            anchor="w",
        ).pack(fill="x")

    def _build_specifications(self):
        """Technical specifications and runtime details."""
        card = ctk.CTkFrame(
            self,
            fg_color=BG_CARD,
            corner_radius=12,
            border_width=1,
            border_color=BORDER_COLOR,
        )
        card.pack(fill="x", padx=24, pady=(0, 16))

        inner = ctk.CTkFrame(card, fg_color="transparent")
        inner.pack(fill="x", padx=24, pady=20)

        ctk.CTkLabel(
            inner,
            text="TECHNICAL ARCHITECTURE & METADATA",
            font=FONT_BADGE,
            text_color=TEXT_MUTED,
            anchor="w",
        ).pack(fill="x", pady=(0, 12))

        specs = [
            ("Application Version", "1.0.0 (Release)"),
            ("Target Platform", "Microsoft Windows Desktop (x64)"),
            ("Core Programming Language", "Python 3"),
            ("Graphical User Interface", "CustomTkinter 6.0 + Tkinter"),
            ("Database Engine", "SQLite 3 (Built-in Relational Database)"),
            ("Database Storage Path", str(get_db_path())),
            ("Offline Capability", "100% Fully Offline (Zero internet or cloud dependencies)"),
            ("Project Purpose", "College Financial Software & Desktop Engineering Project"),
        ]

        grid_frame = ctk.CTkFrame(inner, fg_color="transparent")
        grid_frame.pack(fill="x")
        grid_frame.grid_columnconfigure(0, weight=1)
        grid_frame.grid_columnconfigure(1, weight=2)

        for i, (key, val) in enumerate(specs):
            ctk.CTkLabel(
                grid_frame,
                text=key,
                font=FONT_BODY_BOLD,
                text_color=TEXT_SECONDARY,
                anchor="w",
            ).grid(row=i, column=0, sticky="w", pady=4)

            ctk.CTkLabel(
                grid_frame,
                text=val,
                font=FONT_BODY,
                text_color=TEXT_MAIN,
                anchor="w",
            ).grid(row=i, column=1, sticky="w", pady=4, padx=(20, 0))

    def _build_disclaimers(self):
        """Financial and regulatory disclosures."""
        card = ctk.CTkFrame(
            self,
            fg_color=BG_CARD,
            corner_radius=12,
            border_width=1,
            border_color=BORDER_COLOR,
        )
        card.pack(fill="x", padx=24, pady=(0, 24))

        inner = ctk.CTkFrame(card, fg_color="transparent")
        inner.pack(fill="x", padx=24, pady=20)

        ctk.CTkLabel(
            inner,
            text="IMPORTANT FINANCIAL DISCLOSURES",
            font=FONT_BADGE,
            text_color="#F59E0B",
            anchor="w",
        ).pack(fill="x", pady=(0, 10))

        disclaimers = (
            "1. Loan EMI Disclosures: EMI calculations provided by ONVEST are mathematical estimates based on the "
            "standard reducing balance amortization formula. Actual loan offers, interest compounding frequencies, "
            "processing charges, and repayment schedules depend on specific banking institutions and regulatory lending norms.\n\n"
            "2. Mutual Fund SIP Disclosures: SIP projections are illustrative estimates assuming a constant annualized "
            "rate of return. Mutual fund investments are subject to market risks; read all scheme-related documents carefully. "
            "Calculations exclude capital gains taxes, dividend distribution taxes, exit loads, and inflation.\n\n"
            "3. Educational Project: This software is developed for educational and personal financial planning purposes."
        )

        ctk.CTkLabel(
            inner,
            text=disclaimers,
            font=FONT_BODY_SMALL,
            text_color=TEXT_MUTED,
            wraplength=760,
            justify="left",
            anchor="w",
        ).pack(fill="x")
