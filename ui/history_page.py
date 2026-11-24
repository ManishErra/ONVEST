"""
Calculation History View for ONVEST.
Displays saved EMI and SIP records in a responsive, table-like layout
with record deletion, table refresh, feedback messages, and confirmation-guarded total clear.
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
    """Calculation History page with responsive table-like list and management controls."""

    def __init__(self, master, on_history_updated: Optional[Callable[[], None]] = None, **kwargs):
        super().__init__(master, fg_color=BG_MAIN, corner_radius=0, **kwargs)
        self.on_history_updated = on_history_updated

        self._build_header_and_controls()
        self._build_feedback_area()
        self._build_table_container()
        self.refresh_table()

    def _build_header_and_controls(self):
        """Top bar with title, counter, and action buttons."""
        top_bar = ctk.CTkFrame(self, fg_color="transparent")
        top_bar.pack(fill="x", padx=20, pady=(18, 6))

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
            width=90,
            height=32,
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
            width=90,
            height=32,
            corner_radius=6,
            command=self._confirm_clear_all,
        )
        self.clear_all_btn.pack(side="left")

    def _build_feedback_area(self):
        """Feedback label for operation success and error messages."""
        self.feedback_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.feedback_frame.pack(fill="x", padx=20, pady=(0, 4))

        self.feedback_label = ctk.CTkLabel(
            self.feedback_frame,
            text="",
            font=FONT_BODY_SMALL,
            text_color=TEXT_SECONDARY,
            anchor="w",
        )
        self.feedback_label.pack(fill="x")

    def _show_error(self, message: str):
        """Displays error feedback message."""
        self.feedback_label.configure(text=f"⚠ {message}", text_color=ERROR_RED)

    def _show_success(self, message: str):
        """Displays success feedback message."""
        self.feedback_label.configure(text=f"✓ {message}", text_color=EMERALD_GREEN)

    def _clear_feedback(self):
        """Clears feedback message."""
        self.feedback_label.configure(text="")

    def _build_table_container(self):
        """Responsive table header row and scrollable records area."""
        # Table Header Frame using grid for proportional column responsiveness
        self.tbl_header = ctk.CTkFrame(
            self,
            fg_color="#132038",
            corner_radius=8,
            height=36,
            border_width=1,
            border_color=BORDER_COLOR,
        )
        self.tbl_header.pack(fill="x", padx=20, pady=(0, 6))
        self.tbl_header.pack_propagate(False)

        # Configure responsive grid column weights
        self._configure_grid_weights(self.tbl_header)

        headers = [
            (0, "TYPE", "w"),
            (1, "INPUT AMOUNT", "w"),
            (2, "RATE", "w"),
            (3, "DURATION", "w"),
            (4, "MONTHLY/EMI", "w"),
            (5, "TOTAL AMOUNT", "w"),
            (6, "SAVED AT", "w"),
            (7, "ACTION", "e"),
        ]

        for col_idx, title, anchor in headers:
            lbl = ctk.CTkLabel(
                self.tbl_header,
                text=title,
                font=FONT_BADGE,
                text_color=TEXT_SECONDARY,
                anchor=anchor,
            )
            lbl.grid(row=0, column=col_idx, sticky="ew", padx=6, pady=4)

        # Scrollable rows area
        self.rows_frame = ctk.CTkScrollableFrame(
            self,
            fg_color="transparent",
            corner_radius=0,
        )
        self.rows_frame.pack(fill="both", expand=True, padx=20, pady=(0, 14))

    def _configure_grid_weights(self, frame: ctk.CTkFrame):
        """Applies responsive column weights to header and row frames."""
        frame.grid_columnconfigure(0, weight=0, minsize=52)   # Type badge
        frame.grid_columnconfigure(1, weight=2, minsize=90)   # Input amount
        frame.grid_columnconfigure(2, weight=1, minsize=46)   # Rate
        frame.grid_columnconfigure(3, weight=1, minsize=52)   # Duration
        frame.grid_columnconfigure(4, weight=2, minsize=92)   # Monthly/EMI
        frame.grid_columnconfigure(5, weight=2, minsize=100)  # Total amount
        frame.grid_columnconfigure(6, weight=2, minsize=108)  # Timestamp
        frame.grid_columnconfigure(7, weight=0, minsize=64)   # Delete action

    def refresh_table(self):
        """Fetches all records from SQLite and re-renders table rows."""
        # Clear existing rows
        for widget in self.rows_frame.winfo_children():
            widget.destroy()

        try:
            total_count = get_calculation_count()
            records = get_all_calculations(limit=100)
            displayed_count = len(records)

            if total_count > displayed_count:
                self.count_badge.configure(
                    text=f"{total_count} saved records in database (displaying latest {displayed_count})"
                )
            else:
                self.count_badge.configure(
                    text=f"{total_count} saved record{'s' if total_count != 1 else ''} in local database"
                )

            if total_count == 0:
                self._show_empty_state()
                return

            for rec in records:
                self._create_row(rec)

        except Exception as e:
            self._show_error(f"Failed to load records from database: {e}")
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
        """Creates a single responsive record row card with action buttons."""
        row_id = rec["id"]
        calc_type = rec["calc_type"]
        is_emi = calc_type == "EMI"

        row_card = ctk.CTkFrame(
            self.rows_frame,
            fg_color=BG_CARD,
            corner_radius=8,
            height=44,
            border_width=1,
            border_color=BORDER_COLOR,
        )
        row_card.pack(fill="x", pady=3)
        row_card.pack_propagate(False)

        self._configure_grid_weights(row_card)

        # 0. Type Badge
        badge_fg = PRIMARY_BLUE if is_emi else EMERALD_GREEN
        badge_pill = ctk.CTkLabel(
            row_card,
            text=calc_type,
            font=FONT_BADGE,
            text_color=TEXT_MAIN,
            fg_color=badge_fg,
            corner_radius=5,
            width=46,
            height=22,
        )
        badge_pill.grid(row=0, column=0, sticky="w", padx=6, pady=8)

        # 1. Input Amount
        amt_val = format_inr(rec["principal_or_monthly"])
        ctk.CTkLabel(
            row_card,
            text=amt_val,
            font=FONT_BODY_BOLD,
            text_color=TEXT_MAIN,
            anchor="w",
        ).grid(row=0, column=1, sticky="ew", padx=6, pady=8)

        # 2. Rate
        rate_val = f"{rec['annual_rate']:.1f}%"
        ctk.CTkLabel(
            row_card,
            text=rate_val,
            font=FONT_BODY,
            text_color=TEXT_SECONDARY,
            anchor="w",
        ).grid(row=0, column=2, sticky="ew", padx=6, pady=8)

        # 3. Duration
        duration_months = rec["duration_months"]
        duration_years = round(duration_months / 12, 1)
        dur_val = f"{duration_years}y"
        ctk.CTkLabel(
            row_card,
            text=dur_val,
            font=FONT_BODY,
            text_color=TEXT_SECONDARY,
            anchor="w",
        ).grid(row=0, column=3, sticky="ew", padx=6, pady=8)

        # 4. Monthly / EMI Amount
        monthly_val = format_inr(rec["monthly_amount"])
        ctk.CTkLabel(
            row_card,
            text=monthly_val,
            font=FONT_BODY,
            text_color=PRIMARY_BLUE if is_emi else EMERALD_GREEN,
            anchor="w",
        ).grid(row=0, column=4, sticky="ew", padx=6, pady=8)

        # 5. Total Amount
        tot_val = format_inr(rec["total_amount"])
        ctk.CTkLabel(
            row_card,
            text=tot_val,
            font=FONT_BODY_BOLD,
            text_color=TEXT_MAIN,
            anchor="w",
        ).grid(row=0, column=5, sticky="ew", padx=6, pady=8)

        # 6. Saved At
        created_at = rec["created_at"]
        ctk.CTkLabel(
            row_card,
            text=created_at,
            font=FONT_BODY_SMALL,
            text_color=TEXT_MUTED,
            anchor="w",
        ).grid(row=0, column=6, sticky="ew", padx=6, pady=8)

        # 7. Action (Delete)
        del_btn = ctk.CTkButton(
            row_card,
            text="Delete",
            font=FONT_BODY_SMALL,
            fg_color="#334155",
            hover_color=ERROR_RED,
            text_color=TEXT_MAIN,
            width=58,
            height=24,
            corner_radius=5,
            command=lambda r_id=row_id: self._handle_delete_record(r_id),
        )
        del_btn.grid(row=0, column=7, sticky="e", padx=(4, 6), pady=8)

    def _handle_delete_record(self, record_id: int):
        """Deletes a specific calculation record with error handling and feedback."""
        self._clear_feedback()
        try:
            deleted = delete_calculation(record_id)
            if deleted:
                self._show_success(f"Record #{record_id} deleted successfully.")
                self.refresh_table()
                if self.on_history_updated:
                    self.on_history_updated()
            else:
                self._show_error(f"Could not delete Record #{record_id}: record not found.")
        except Exception as e:
            self._show_error(f"Failed to delete record #{record_id}: {e}")

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
        """Executes clearing all records with error handling and feedback."""
        self._clear_feedback()
        try:
            success = clear_all_calculations()
            if success:
                self._show_success("All calculation history has been cleared.")
                self.refresh_table()
                if self.on_history_updated:
                    self.on_history_updated()
            else:
                self._show_error("Failed to clear calculation history.")
        except Exception as e:
            self._show_error(f"Failed to clear calculation history: {e}")
