"""Builds the application stylesheet from the shared palette.

Kept separate from main_window.py so the visual theme can be read, reviewed,
or swapped without touching any window logic.
"""
from __future__ import annotations

from config import PALETTE


def get_stylesheet() -> str:
    p = PALETTE
    return f"""
    QMainWindow, QWidget {{
        background-color: {p.background};
        color: {p.text};
        font-family: "Segoe UI", "Ubuntu", sans-serif;
        font-size: 13px;
    }}

    QFrame#leftPanel, QFrame#statsPanel {{
        background-color: {p.surface};
        border-right: 1px solid {p.border};
    }}

    QLabel#titleLabel {{
        font-size: 16px;
        font-weight: 600;
        padding: 10px 12px 4px 12px;
    }}

    QLabel#statusLabel {{
        color: {p.text_dim};
        padding: 0 12px 8px 12px;
        font-weight: 400;
    }}

    QLabel.statValue {{
        font-size: 20px;
        font-weight: 700;
        color: {p.accent};
    }}

    QLabel.statCaption {{
        color: {p.text_dim};
        font-size: 11px;
    }}

    QTableWidget {{
        background-color: {p.surface};
        alternate-background-color: {p.surface_alt};
        gridline-color: {p.border};
        border: none;
        selection-background-color: {p.accent};
        selection-color: white;
    }}

    QHeaderView::section {{
        background-color: {p.surface_alt};
        color: {p.text};
        padding: 6px;
        border: none;
        border-bottom: 1px solid {p.border};
        font-weight: 600;
    }}

    QLineEdit, QDoubleSpinBox, QSpinBox {{
        background-color: {p.surface_alt};
        border: 1px solid {p.border};
        border-radius: 4px;
        padding: 5px 7px;
        color: {p.text};
    }}

    QLineEdit:focus, QDoubleSpinBox:focus, QSpinBox:focus {{
        border: 1px solid {p.accent};
    }}

    QPushButton {{
        background-color: {p.accent};
        color: white;
        border: none;
        border-radius: 5px;
        padding: 8px 14px;
        font-weight: 600;
    }}

    QPushButton:hover {{
        background-color: {p.accent_hover};
    }}

    QPushButton:pressed {{
        background-color: {p.accent_hover};
        padding-top: 9px;
    }}

    QPushButton#mutedButton {{
        background-color: {p.surface_alt};
        border: 1px solid {p.border};
    }}

    QPushButton:disabled {{
        background-color: {p.surface_alt};
        color: {p.text_dim};
    }}

    QStatusBar {{
        background-color: {p.surface};
        color: {p.text_dim};
        border-top: 1px solid {p.border};
    }}

    QToolTip {{
        background-color: {p.surface_alt};
        color: {p.text};
        border: 1px solid {p.border};
        padding: 4px;
    }}
    """
