"""
UI Package for ONVEST.
Exports main views and styles.
"""

from .dashboard import DashboardPage
from .emi_page import EMIPage
from .sip_page import SIPPage
from .history_page import HistoryPage
from .about_page import AboutPage

__all__ = [
    "DashboardPage",
    "EMIPage",
    "SIPPage",
    "HistoryPage",
    "AboutPage",
]
