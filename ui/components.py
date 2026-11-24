"""
Reusable UI components for ONVEST.
Includes MetricCard, ProportionalBar, SectionHeader, and custom ConfirmationDialog.
"""

import customtkinter as ctk
from typing import Callable, Optional
from ui.styles import (
    BG_CARD,
    BORDER_COLOR,
    TEXT_MAIN,
    TEXT_SECONDARY,
    TEXT_MUTED,
    PRIMARY_BLUE,
    PRIMARY_BLUE_HOVER,
    EMERALD_GREEN,
    ERROR_RED,
    ERROR_RED_HOVER,
    FONT_HEADING,
    FONT_SUBTITLE,
    FONT_BODY,
    FONT_BODY_BOLD,
    FONT_BODY_SMALL,
    FONT_BIG_METRIC,
    FONT_MID_METRIC,
    FONT_BADGE,
    format_inr,
)


class SectionHeader(ctk.CTkFrame):
    """Clean section header with title and subtitle."""

    def __init__(self, master, title: str, subtitle: str, **kwargs):
        super().__init__(master, fg_color="transparent", **kwargs)

        self.title_label = ctk.CTkLabel(
            self,
            text=title,
            font=FONT_SUBTITLE,
            text_color=TEXT_MAIN,
            anchor="w",
        )
        self.title_label.pack(fill="x", padx=0, pady=(0, 2))

        self.subtitle_label = ctk.CTkLabel(
            self,
            text=subtitle,
            font=FONT_BODY_SMALL,
            text_color=TEXT_SECONDARY,
            anchor="w",
        )
        self.subtitle_label.pack(fill="x", padx=0, pady=(0, 10))


class MetricCard(ctk.CTkFrame):
    """
    Card widget for displaying a single financial metric with title, formatted value,
    and optional secondary caption or badge.
    """

    def __init__(
        self,
        master,
        title: str,
        initial_value: str = "₹0.00",
        caption: str = "",
        highlight_color: Optional[str] = None,
        is_primary: bool = False,
        **kwargs,
    ):
        border_col = highlight_color if highlight_color else BORDER_COLOR
        border_width = 1.5 if (is_primary or highlight_color) else 1

        super().__init__(
            master,
            fg_color=BG_CARD,
            corner_radius=10,
            border_width=border_width,
            border_color=border_col,
            **kwargs,
        )

        self.highlight_color = highlight_color

        self.title_label = ctk.CTkLabel(
            self,
            text=title.upper(),
            font=FONT_BADGE,
            text_color=TEXT_SECONDARY,
            anchor="w",
        )
        self.title_label.pack(fill="x", padx=16, pady=(14, 4))

        val_font = FONT_BIG_METRIC if is_primary else FONT_MID_METRIC
        val_color = highlight_color if highlight_color else TEXT_MAIN

        self.value_label = ctk.CTkLabel(
            self,
            text=initial_value,
            font=val_font,
            text_color=val_color,
            anchor="w",
        )
        self.value_label.pack(fill="x", padx=16, pady=(0, 4))

        if caption:
            self.caption_label = ctk.CTkLabel(
                self,
                text=caption,
                font=FONT_BODY_SMALL,
                text_color=TEXT_MUTED,
                anchor="w",
            )
            self.caption_label.pack(fill="x", padx=16, pady=(0, 12))
        else:
            self.caption_label = None

    def update_value(self, new_value: str, caption: Optional[str] = None):
        """Updates the metric value and optional caption."""
        self.value_label.configure(text=new_value)
        if caption is not None and self.caption_label is not None:
            self.caption_label.configure(text=caption)


class ProportionalBar(ctk.CTkFrame):
    """
    Horizontal dual-colored proportional breakdown bar.
    Displays Left Component (e.g. Principal / Invested) and Right Component (e.g. Interest / Returns)
    with proportional widths, color fills, and a neat breakdown legend.
    """

    def __init__(
        self,
        master,
        left_label: str,
        right_label: str,
        left_color: str = PRIMARY_BLUE,
        right_color: str = EMERALD_GREEN,
        height: int = 14,
        **kwargs,
    ):
        super().__init__(master, fg_color=BG_CARD, corner_radius=10, border_width=1, border_color=BORDER_COLOR, **kwargs)

        self.left_label_text = left_label
        self.right_label_text = right_label
        self.left_color = left_color
        self.right_color = right_color
        self.bar_height = height

        # Header
        header_frame = ctk.CTkFrame(self, fg_color="transparent")
        header_frame.pack(fill="x", padx=16, pady=(12, 8))

        ctk.CTkLabel(
            header_frame,
            text="VISUAL PROPORTIONAL BREAKDOWN",
            font=FONT_BADGE,
            text_color=TEXT_SECONDARY,
        ).pack(side="left")

        # Container for the segmented bar
        self.bar_container = ctk.CTkFrame(
            self,
            fg_color="#0F172A",
            corner_radius=7,
            height=self.bar_height,
        )
        self.bar_container.pack(fill="x", padx=16, pady=(0, 12))
        self.bar_container.pack_propagate(False)

        # Left segment
        self.left_bar = ctk.CTkFrame(
            self.bar_container,
            fg_color=self.left_color,
            corner_radius=5,
            height=self.bar_height,
        )
        self.left_bar.place(relx=0.0, rely=0.0, relwidth=0.5, relheight=1.0)

        # Right segment
        self.right_bar = ctk.CTkFrame(
            self.bar_container,
            fg_color=self.right_color,
            corner_radius=5,
            height=self.bar_height,
        )
        self.right_bar.place(relx=0.5, rely=0.0, relwidth=0.5, relheight=1.0)

        # Legend frame
        self.legend_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.legend_frame.pack(fill="x", padx=16, pady=(0, 12))

        # Left legend
        left_box = ctk.CTkFrame(self.legend_frame, fg_color="transparent")
        left_box.pack(side="left", fill="x", expand=True)

        left_pill = ctk.CTkFrame(left_box, fg_color=self.left_color, width=10, height=10, corner_radius=3)
        left_pill.pack(side="left", padx=(0, 6))

        self.left_text_lbl = ctk.CTkLabel(
            left_box,
            text=f"{self.left_label_text}: 50.0%",
            font=FONT_BODY_BOLD,
            text_color=TEXT_MAIN,
        )
        self.left_text_lbl.pack(side="left")

        # Right legend
        right_box = ctk.CTkFrame(self.legend_frame, fg_color="transparent")
        right_box.pack(side="right", fill="x", expand=True)

        self.right_text_lbl = ctk.CTkLabel(
            right_box,
            text=f"{self.right_label_text}: 50.0%",
            font=FONT_BODY_BOLD,
            text_color=TEXT_MAIN,
            anchor="e",
        )
        self.right_text_lbl.pack(side="right")

        right_pill = ctk.CTkFrame(right_box, fg_color=self.right_color, width=10, height=10, corner_radius=3)
        right_pill.pack(side="right", padx=(0, 6))

    def update_ratios(self, left_ratio: float, right_ratio: float, left_amount: float = 0, right_amount: float = 0):
        """
        Updates the segment widths and legend percentages.
        Ratios should sum to 1.0 (clamped).
        """
        total = left_ratio + right_ratio
        if total <= 0:
            left_ratio = 1.0
            right_ratio = 0.0
        else:
            left_ratio = left_ratio / total
            right_ratio = right_ratio / total

        # Avoid disappearing bar if ratio is tiny but positive
        display_left = max(0.02, left_ratio) if left_ratio > 0 else 0.0
        display_right = 1.0 - display_left if left_ratio > 0 else 1.0

        self.left_bar.place(relx=0.0, rely=0.0, relwidth=display_left, relheight=1.0)
        self.right_bar.place(relx=display_left, rely=0.0, relwidth=display_right, relheight=1.0)

        left_pct = left_ratio * 100.0
        right_pct = right_ratio * 100.0

        if left_amount > 0 or right_amount > 0:
            self.left_text_lbl.configure(text=f"{self.left_label_text}: {format_inr(left_amount)} ({left_pct:.1f}%)")
            self.right_text_lbl.configure(text=f"{self.right_label_text}: {format_inr(right_amount)} ({right_pct:.1f}%)")
        else:
            self.left_text_lbl.configure(text=f"{self.left_label_text}: {left_pct:.1f}%")
            self.right_text_lbl.configure(text=f"{self.right_label_text}: {right_pct:.1f}%")


class ConfirmationDialog(ctk.CTkToplevel):
    """
    Clean modal confirmation dialog for destructive operations.
    """

    def __init__(
        self,
        parent,
        title: str,
        message: str,
        confirm_text: str = "Confirm",
        cancel_text: str = "Cancel",
        on_confirm: Optional[Callable[[], None]] = None,
        is_destructive: bool = True,
    ):
        super().__init__(parent)

        self.title(title)
        self.geometry("420x220")
        self.resizable(False, False)
        self.configure(fg_color=BG_CARD)

        self.on_confirm = on_confirm

        # Make modal
        self.transient(parent)
        self.grab_set()

        # Center relative to parent
        parent.update_idletasks()
        x = parent.winfo_x() + (parent.winfo_width() // 2) - 210
        y = parent.winfo_y() + (parent.winfo_height() // 2) - 110
        self.geometry(f"+{max(50, x)}+{max(50, y)}")

        # Container
        content_frame = ctk.CTkFrame(self, fg_color="transparent")
        content_frame.pack(fill="both", expand=True, padx=24, pady=20)

        title_lbl = ctk.CTkLabel(
            content_frame,
            text=title,
            font=FONT_HEADING,
            text_color=TEXT_MAIN,
            anchor="w",
        )
        title_lbl.pack(fill="x", pady=(0, 8))

        msg_lbl = ctk.CTkLabel(
            content_frame,
            text=message,
            font=FONT_BODY,
            text_color=TEXT_SECONDARY,
            wraplength=370,
            justify="left",
            anchor="w",
        )
        msg_lbl.pack(fill="x", pady=(0, 20))

        btn_frame = ctk.CTkFrame(content_frame, fg_color="transparent")
        btn_frame.pack(fill="x", side="bottom")

        cancel_btn = ctk.CTkButton(
            btn_frame,
            text=cancel_text,
            fg_color="#334155",
            hover_color="#475569",
            text_color=TEXT_MAIN,
            font=FONT_BODY_BOLD,
            width=100,
            height=36,
            corner_radius=6,
            command=self._on_cancel,
        )
        cancel_btn.pack(side="right", padx=(8, 0))

        confirm_fg = ERROR_RED if is_destructive else PRIMARY_BLUE
        confirm_hover = ERROR_RED_HOVER if is_destructive else PRIMARY_BLUE_HOVER

        confirm_btn = ctk.CTkButton(
            btn_frame,
            text=confirm_text,
            fg_color=confirm_fg,
            hover_color=confirm_hover,
            text_color=TEXT_MAIN,
            font=FONT_BODY_BOLD,
            width=110,
            height=36,
            corner_radius=6,
            command=self._on_confirm_action,
        )
        confirm_btn.pack(side="right")

    def _on_confirm_action(self):
        self.destroy()
        if self.on_confirm:
            self.on_confirm()

    def _on_cancel(self):
        self.destroy()
