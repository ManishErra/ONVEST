"""
ONVEST – Loan EMI & SIP Calculator
Main Application Entry Point.

Tagline: Calculate. Invest. Grow.
GUI Framework: CustomTkinter
Database: SQLite 3
Platform: Windows Desktop
"""

import sys
import customtkinter as ctk
from database.history import init_db
from ui.dashboard import DashboardPage
from ui.emi_page import EMIPage
from ui.sip_page import SIPPage
from ui.history_page import HistoryPage
from ui.about_page import AboutPage
from ui.styles import (
    BG_MAIN,
    BG_SIDEBAR,
    BG_CARD,
    BORDER_COLOR,
    PRIMARY_BLUE,
    PRIMARY_BLUE_HOVER,
    EMERALD_GREEN,
    TEXT_MAIN,
    TEXT_SECONDARY,
    TEXT_MUTED,
    FONT_TITLE,
    FONT_HEADING,
    FONT_SUBTITLE,
    FONT_BODY,
    FONT_BODY_BOLD,
    FONT_BODY_SMALL,
    FONT_BADGE,
)


class OnvestApp(ctk.CTk):
    """
    ONVEST Desktop Application Window.
    Provides persistent sidebar navigation and dynamic view switching.
    """

    def __init__(self):
        super().__init__()

        # Window Configuration
        self.title("ONVEST – Loan EMI & SIP Calculator")
        self.geometry("1180x760")
        self.minsize(1020, 660)
        self.configure(fg_color=BG_MAIN)

        # Initialize SQLite Database
        init_db()

        # Layout: Grid with 2 columns (Sidebar = col 0, Content Area = col 1)
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=0, minsize=260)
        self.grid_columnconfigure(1, weight=1)

        # Build UI Panels
        self._build_sidebar()
        self._build_content_area()

        # Default View: Dashboard
        self.current_view_key = None
        self.navigate_to("dashboard")

    def _build_sidebar(self):
        """Builds persistent left navigation sidebar."""
        self.sidebar_frame = ctk.CTkFrame(
            self,
            fg_color=BG_SIDEBAR,
            corner_radius=0,
            border_width=1,
            border_color=BORDER_COLOR,
            width=260,
        )
        self.sidebar_frame.grid(row=0, column=0, sticky="nsew")
        self.sidebar_frame.grid_propagate(False)

        # --- Brand Header ---
        brand_frame = ctk.CTkFrame(self.sidebar_frame, fg_color="transparent")
        brand_frame.pack(fill="x", padx=20, pady=(24, 28))

        # Brand title
        ctk.CTkLabel(
            brand_frame,
            text="ONVEST",
            font=(FONT_TITLE[0], 22, "bold"),
            text_color=TEXT_MAIN,
            anchor="w",
        ).pack(fill="x")

        # Subtitle
        ctk.CTkLabel(
            brand_frame,
            text="Loan EMI & SIP Calculator",
            font=FONT_BODY_SMALL,
            text_color=PRIMARY_BLUE,
            anchor="w",
        ).pack(fill="x", pady=(1, 2))

        # Tagline
        ctk.CTkLabel(
            brand_frame,
            text="Calculate. Invest. Grow.",
            font=FONT_BADGE,
            text_color=EMERALD_GREEN,
            anchor="w",
        ).pack(fill="x")

        # Subtle divider
        ctk.CTkFrame(
            self.sidebar_frame,
            fg_color=BORDER_COLOR,
            height=1,
        ).pack(fill="x", padx=20, pady=(0, 20))

        # Navigation label
        ctk.CTkLabel(
            self.sidebar_frame,
            text="NAVIGATION",
            font=FONT_BADGE,
            text_color=TEXT_MUTED,
            anchor="w",
        ).pack(fill="x", padx=24, pady=(0, 8))

        # Navigation Buttons dictionary
        self.nav_buttons = {}

        nav_items = [
            ("dashboard", "📊  Dashboard"),
            ("emi", "💳  Loan EMI Calculator"),
            ("sip", "📈  SIP Calculator"),
            ("history", "📜  Calculation History"),
            ("about", "ℹ️  About ONVEST"),
        ]

        for key, label in nav_items:
            btn = ctk.CTkButton(
                self.sidebar_frame,
                text=label,
                font=FONT_BODY_BOLD,
                fg_color="transparent",
                hover_color=BG_CARD,
                text_color=TEXT_SECONDARY,
                anchor="w",
                height=42,
                corner_radius=8,
                command=lambda k=key: self.navigate_to(k),
            )
            btn.pack(fill="x", padx=16, pady=3)
            self.nav_buttons[key] = btn

        # --- Sidebar Footer ---
        footer_frame = ctk.CTkFrame(self.sidebar_frame, fg_color="transparent")
        footer_frame.pack(side="bottom", fill="x", padx=20, pady=20)

        ctk.CTkFrame(footer_frame, fg_color=BORDER_COLOR, height=1).pack(fill="x", pady=(0, 14))

        status_box = ctk.CTkFrame(footer_frame, fg_color="transparent")
        status_box.pack(fill="x")

        # Green indicator dot for offline SQLite
        dot = ctk.CTkFrame(status_box, fg_color=EMERALD_GREEN, width=8, height=8, corner_radius=4)
        dot.pack(side="left", padx=(0, 8))

        ctk.CTkLabel(
            status_box,
            text="SQLite Storage Active",
            font=FONT_BODY_SMALL,
            text_color=TEXT_SECONDARY,
            anchor="w",
        ).pack(side="left")

        ctk.CTkLabel(
            footer_frame,
            text="v1.0.0 • Offline Desktop",
            font=FONT_BODY_SMALL,
            text_color=TEXT_MUTED,
            anchor="w",
        ).pack(fill="x", pady=(4, 0))

    def _build_content_area(self):
        """Creates container and instantiates all pages."""
        self.content_container = ctk.CTkFrame(self, fg_color=BG_MAIN, corner_radius=0)
        self.content_container.grid(row=0, column=1, sticky="nsew")
        self.content_container.grid_rowconfigure(0, weight=1)
        self.content_container.grid_columnconfigure(0, weight=1)

        # Create all page instances
        self.pages = {
            "dashboard": DashboardPage(
                self.content_container,
                navigate_callback=self.navigate_to,
            ),
            "emi": EMIPage(
                self.content_container,
                on_history_updated=self._on_history_changed,
            ),
            "sip": SIPPage(
                self.content_container,
                on_history_updated=self._on_history_changed,
            ),
            "history": HistoryPage(
                self.content_container,
                on_history_updated=self._on_history_changed,
            ),
            "about": AboutPage(
                self.content_container,
            ),
        }

        # Place all pages in the content container grid
        for page in self.pages.values():
            page.grid(row=0, column=0, sticky="nsew")

    def navigate_to(self, page_key: str):
        """Switches active view and updates sidebar highlighting."""
        if page_key not in self.pages:
            return

        # Bring requested page to top
        page = self.pages[page_key]
        page.tkraise()
        self.current_view_key = page_key

        # Update sidebar button states
        for key, btn in self.nav_buttons.items():
            if key == page_key:
                btn.configure(
                    fg_color=BG_CARD,
                    text_color=PRIMARY_BLUE,
                )
            else:
                btn.configure(
                    fg_color="transparent",
                    text_color=TEXT_SECONDARY,
                )

        # Refresh page data if applicable
        if page_key == "dashboard":
            self.pages["dashboard"].refresh_data()
        elif page_key == "history":
            self.pages["history"].refresh_table()

    def _on_history_changed(self):
        """Called whenever a calculation is saved or deleted."""
        # Refresh dashboard and history tables if already initialized
        if "dashboard" in self.pages:
            self.pages["dashboard"].refresh_data()
        if "history" in self.pages:
            self.pages["history"].refresh_table()


def main():
    """Application entry point."""
    # CustomTkinter theme settings
    ctk.set_appearance_mode("dark")
    ctk.set_default_color_theme("blue")

    app = OnvestApp()
    app.mainloop()


if __name__ == "__main__":
    main()
