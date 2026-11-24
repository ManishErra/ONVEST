"""
Styling constants, color palette, typography, and utility formatters for ONVEST.
Strictly adheres to the Dark Navy + Blue + Emerald Green theme.
"""

# Color Palette
BG_MAIN = "#0B1220"          # Deep dark navy main background
BG_SIDEBAR = "#111D32"       # Sidebar navigation background
BG_CARD = "#17243A"          # Card container background
BG_CARD_HOVER = "#1E2F4D"    # Subtle hover on cards
BG_INPUT = "#0D1829"         # Dark input field background
BG_INPUT_BORDER = "#253856"  # Subtle border for inputs

PRIMARY_BLUE = "#3B82F6"     # Primary action blue
PRIMARY_BLUE_HOVER = "#2563EB"
PRIMARY_BLUE_LIGHT = "#60A5FA"

EMERALD_GREEN = "#10B981"    # Accent / Success emerald green
EMERALD_GREEN_HOVER = "#059669"
EMERALD_GREEN_LIGHT = "#34D399"
EMERALD_GREEN_BG = "#064E3B"

AMBER_ACCENT = "#F59E0B"     # Warm highlight
ERROR_RED = "#EF4444"        # Error text and warning buttons
ERROR_RED_HOVER = "#DC2626"
ERROR_RED_BG = "#450A0A"

TEXT_MAIN = "#F8FAFC"        # Bright off-white for headings and primary text
TEXT_SECONDARY = "#94A3B8"   # Cool gray for subtitles and labels
TEXT_MUTED = "#64748B"       # Subtle gray for notes and dividers

BORDER_COLOR = "#223554"     # Card and container borders

# Font Specifications
FONT_FAMILY = "Segoe UI"
FONT_TITLE = (FONT_FAMILY, 24, "bold")
FONT_SUBTITLE = (FONT_FAMILY, 18, "bold")
FONT_HEADING = (FONT_FAMILY, 15, "bold")
FONT_BODY_BOLD = (FONT_FAMILY, 13, "bold")
FONT_BODY = (FONT_FAMILY, 13)
FONT_BODY_SMALL = (FONT_FAMILY, 11)
FONT_BIG_METRIC = (FONT_FAMILY, 26, "bold")
FONT_MID_METRIC = (FONT_FAMILY, 20, "bold")
FONT_BADGE = (FONT_FAMILY, 11, "bold")


def format_inr(amount: float, include_paise: bool = True) -> str:
    """
    Formats a numeric value according to the Indian Numbering System (Lakhs, Crores).
    Example:
        1234567.89 -> '₹12,34,567.89'
        100000 -> '₹1,00,000.00'
        500 -> '₹500.00'
    """
    if amount is None:
        return "₹0.00" if include_paise else "₹0"

    is_negative = amount < 0
    abs_amt = abs(amount)

    if include_paise:
        rounded_amt = round(abs_amt, 2)
        int_part = int(rounded_amt)
        paise_part = f"{round(rounded_amt - int_part, 2):.2f}"[2:]
    else:
        int_part = int(round(abs_amt))
        paise_part = ""

    s = str(int_part)
    if len(s) <= 3:
        formatted_int = s
    else:
        last3 = s[-3:]
        rest = s[:-3]
        # Group rest in pairs of 2 from right to left
        chunks = []
        while len(rest) > 2:
            chunks.insert(0, rest[-2:])
            rest = rest[:-2]
        if rest:
            chunks.insert(0, rest)
        formatted_int = ",".join(chunks) + "," + last3

    sign = "-" if is_negative else ""
    if include_paise:
        return f"{sign}₹{formatted_int}.{paise_part}"
    return f"{sign}₹{formatted_int}"
