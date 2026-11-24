"""
Calculation History View for ONVEST.
Displays saved EMI and SIP records in a structured, table-like layout
with record deletion, table refresh, and confirmation-guarded total clear.
"""

import customtkinter as ctk
from typing import Callable, Optional
from database.history import (
    get_all_calculations,
    delete_calculation,
    clear_all_calculations,
    get_calculation_count,
)
from ui.styles import (
    BG_MAIN,
    BG_CARD,
    BORDER_COLOR,
    PRIMARY_BLUE,
    PRIMARY_BLUE_HOVER,
    EMERALD_GREEN,
    ERROR_RED,
    ERROR_RED_HOVER,
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
from ui.components import ConfirmationDialog, SectionHeader


class HistoryPage(ctk.CTkFrame):
    """Calculation History page with table-like list and management controls."""

    def __init__(self, master, on_history_updated: Optional[Callable[[], None]] = None, **kwargs):
        super().__init__(master, fg_color=BG_MAIN, corner_radius=0, **kwargs)
        self.on_history_updated = on_history_updated

        self._build_header_and_controls()
        self._build_table_container()
        self.refresh_table()

    def _build_header_and_controls(self):
        """Top bar with title, counter, and action buttons."""
        top_bar = ctk.CTkFrame(self, fg_color="transparent")
        top_bar.pack(fill="x", padx=24, pady=(20, 10))

        # Title on left
        left_box = ctk.CTkFrame(top_bar, fg_color="transparent")
        left_box.pack(side="left")

        ctk.CTkLabel(
            left_box,
            text="Calculation History",
            font=FONT_SUBTITLE,
            text_color=TEXT_MAIN,
            anchor="w",
        ).pack(anchor="w")

        self.count_badge = ctk.CTkLabel(
            left_box,
            text="0 saved records",
            font=FONT_BODY_SMALL,
            text_color=TEXT_SECONDARY,
            anchor="w",
        )
        self.count_badge.pack(anchor="w")

        # Buttons on right
        btn_box = ctk.CTkFrame(top_bar, fg_color="transparent")
        btn_box.pack(side="right")

        self.refresh_btn = ctk.CTkButton(
            btn_box,
            text="⟳ Refresh",
            font=FONT_BODY_BOLD,
            fg_color="#334155",
            hover_color="#475569",
            text_color=TEXT_MAIN,
            width=100,
            height=34,
            corner_radius=6,
            command=self.refresh_table,
        )
        self.refresh_btn.pack(side="left", padx=(0, 8))

        self.clear_all_btn = ctk.CTkButton(
            btn_box,
            text="Clear All",
            font=FONT_BODY_BOLD,
            fg_color=ERROR_RED,
            hover_color=ERROR_RED_HOVER,
            text_color=TEXT_MAIN,
            width=100,
            height=34,
            corner_radius=6,
            command=self._confirm_clear_all,
        )
        self.clear_all_btn.pack(side="left")

    def _build_table_container(self):
        """Table header row and scrollable records area."""
        # Table Header
        tbl_header = ctk.CTkFrame(
            self,
            fg_color="#132038",
            corner_radius=8,
            height=38,
            border_width=1,
            border_color=BORDER_COLOR,
        )
        tbl_header.pack(fill="x", padx=24, pady=(0, 8))
        tbl_header.pack_propagate(False)

        cols = [
            ("TYPE", 70),
            ("INPUT AMOUNT", 130),
            ("RATE", 80),
            ("DURATION", 110),
            ("MONTHLY / EMI", 130),
            ("TOTAL AMOUNT", 150),
            ("SAVED AT", 150),
            ("ACTION", 80),
        ]

        for title, width in cols:
            lbl = ctk.CTkLabel(
                tbl_header,
                text=title,
                font=FONT_BADGE,
                text_color=TEXT_SECONDARY,
                width=width,
                anchor="w",
            )
            lbl.pack(side="left", padx=10)

        # Scrollable rows area
        self.rows_frame = ctk.CTkScrollableFrame(
            self,
            fg_color="transparent",
            corner_radius=0,
        )
        self.rows_frame.pack(fill="both", expand=True, padx=24, pady=(0, 16))

    def refresh_table(self):
        """Fetches all records from SQLite and re-renders table rows."""
        # Clear existing rows
        for widget in self.rows_frame.winfo_children():
            widget.destroy()

        try:
            records = get_all_calculations()
            total_count = len(records)
            self.count_badge.configure(text=f"{total_count} saved records in local database")

            if total_count == 0:
                self._show_empty_state()
                return

            for rec in records:
                self._create_row(rec)

        except Exception as e:
            err_card = ctk.CTkFrame(self.rows_frame, fg_color=BG_CARD, corner_radius=8)
            err_card.pack(fill="x", pady=10)
            ctk.CTkLabel(
                err_card,
                text=f"Failed to load records from database: {e}",
                font=FONT_BODY,
                text_color=ERROR_RED,
                padx=20,
                pady=16,
            ).pack()

    def _show_empty_state(self):
        """Displays friendly empty state when no calculations exist."""
        empty_card = ctk.CTkFrame(
            self.rows_frame,
            fg_color=BG_CARD,
            corner_radius=12,
            border_width=1,
            border_color=BORDER_COLOR,
        )
        empty_card.pack(fill="x", pady=20)

        inner = ctk.CTkFrame(empty_card, fg_color="transparent")
        inner.pack(padx=24, pady=32)

        ctk.CTkLabel(
            inner,
            text="NO SAVED CALCULATIONS",
            font=FONT_BADGE,
            text_color=TEXT_MUTED,
        ).pack(pady=(0, 4))

        ctk.CTkLabel(
            inner,
            text="Your history is currently empty.",
            font=FONT_HEADING,
            text_color=TEXT_MAIN,
        ).pack(pady=(0, 4))

        ctk.CTkLabel(
            inner,
            text=(
                "Use the Loan EMI Calculator or SIP Calculator to perform calculations, "
                "then click 'Save Calculation' to store your results for future reference."
            ),
            font=FONT_BODY,
            text_color=TEXT_SECONDARY,
            wraplength=480,
            justify="center",
        ).pack()

    def _create_row(self, rec: dict):
        """Creates a single record row card with action buttons."""
        row_id = rec["id"]
        calc_type = rec["calc_type"]
        is_emi = calc_type == "EMI"

        row_card = ctk.CTkFrame(
            self.rows_frame,
            fg_color=BG_CARD,
            corner_radius=8,
            height=46,
            border_width=1,
            border_color=BORDER_COLOR,
        )
        row_card.pack(fill="x", pady=3)
        row_card.pack_propagate(False)

        # 1. Type Badge
        badge_fg = PRIMARY_BLUE if is_emi else EMERALD_GREEN
        type_frame = ctk.CTkFrame(row_card, fg_color="transparent", width=70)
        type_frame.pack(side="left", padx=(10, 0))
        type_frame.pack_propagate(False)

        badge_pill = ctk.CTkLabel(
            type_frame,
            text=calc_type,
            font=FONT_BADGE,
            text_color=TEXT_MAIN,
            fg_color=badge_fg,
            corner_radius=5,
            width=50,
            height=24,
        )
        badge_pill.pack(side="left")

        # 2. Input Amount
        amt_val = format_inr(rec["principal_or_monthly"])
        ctk.CTkLabel(
            row_card,
            text=amt_val,
            font=FONT_BODY_BOLD,
            text_color=TEXT_MAIN,
            width=130,
            anchor="w",
        ).pack(side="left", padx=10)

        # 3. Rate
        rate_val = f"{rec['annual_rate']:.1f}%"
        ctk.CTkLabel(
            row_card,
            text=rate_val,
            font=FONT_BODY,
            text_color=TEXT_SECONDARY,
            width=80,
            anchor="w",
        ).pack(side="left", padx=10)

        # 4. Duration
        duration_months = rec["duration_months"]
        duration_years = round(duration_months / 12, 1)
        dur_val = f"{duration_years}y ({duration_months}m)"
        ctk.CTkLabel(
            row_card,
            text=dur_val,
            font=FONT_BODY,
            text_color=TEXT_SECONDARY,
            width=110,
            anchor="w",
        ).pack(side="left", padx=10)

        # 5. Monthly / EMI Amount
        monthly_val = format_inr(rec["monthly_amount"])
        ctk.CTkLabel(
            row_card,
            text=monthly_val,
            font=FONT_BODY,
            text_color=PRIMARY_BLUE if is_emi else EMERALD_GREEN,
            width=130,
            anchor="w",
        ).pack(side="left", padx=10)

        # 6. Total Amount
        tot_val = format_inr(rec["total_amount"])
        ctk.CTkLabel(
            row_card,
            text=tot_val,
            font=FONT_BODY_BOLD,
            text_color=TEXT_MAIN,
            width=150,
            anchor="w",
        ).pack(side="left", padx=10)

        # 7. Saved At
        created_at = rec["created_at"]
        ctk.CTkLabel(
            row_card,
            text=created_at,
            font=FONT_BODY_SMALL,
            text_color=TEXT_MUTED,
            width=150,
            anchor="w",
        ).pack(side="left", padx=10)

        # 8. Action (Delete)
        action_frame = ctk.CTkFrame(row_card, fg_color="transparent", width=80)
        action_frame.pack(side="left", padx=10)
        action_frame.pack_propagate(False)

        del_btn = ctk.CTkButton(
            action_frame,
            text="Delete",
            font=FONT_BODY_SMALL,
            fg_color="#334155",
            hover_color=ERROR_RED,
            text_color=TEXT_MAIN,
            width=65,
            height=26,
            corner_radius=5,
            command=lambda r_id=row_id: self._handle_delete_record(r_id),
        )
        del_btn.pack(side="left")

    def _handle_delete_record(self, record_id: int):
        """Deletes a specific calculation record."""
        try:
            delete_calculation(record_id)
            self.refresh_table()
            if self.on_history_updated:
                self.on_history_updated()
        except Exception as e:
            pass

    def _confirm_clear_all(self):
        """Shows modal confirmation before clearing all history."""
        ConfirmationDialog(
            parent=self.winfo_toplevel(),
            title="Clear All History?",
            message="Are you sure you want to permanently delete all saved calculation records? This action cannot be undone.",
            confirm_text="Clear All",
            cancel_text="Cancel",
            on_confirm=self._execute_clear_all,
            is_destructive=True,
        )

    def _execute_clear_all(self):
        """Executes clearing all records."""
        try:
            clear_all_calculations()
            self.refresh_table()
            if self.on_history_updated:
                self.on_history_updated()
        except Exception as e:
            pass
