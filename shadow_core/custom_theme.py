# shadow_gui/custom_theme.py
"""
Custom theme for Shadow AI GUI with dark mode optimization
"""

import customtkinter as ctk

class ShadowTheme:
    """Custom theme configuration for Shadow AI"""
    
    @staticmethod
    def setup_custom_theme():
        """Setup custom theme colors"""
        ctk.set_default_color_theme({
            "CTk": {
                "fg_color": ["#2B2B2B", "#2B2B2B"],
                "top_fg_color": ["#2B2B2B", "#2B2B2B"],
                "text_color": ["#FFFFFF", "#FFFFFF"],
            },
            "CTkButton": {
                "fg_color": ["#3B8ED0", "#3B8ED0"],
                "hover_color": ["#36719F", "#36719F"],
                "text_color": ["#FFFFFF", "#FFFFFF"],
            },
            "CTkEntry": {
                "fg_color": ["#3B3B3B", "#3B3B3B"],
                "border_color": ["#5D5D5D", "#5D5D5D"],
                "text_color": ["#FFFFFF", "#FFFFFF"],
            },
            "CTkTextbox": {
                "fg_color": ["#2B2B2B", "#2B2B2B"],
                "border_color": ["#5D5D5D", "#5D5D5D"],
                "text_color": ["#FFFFFF", "#FFFFFF"],
            },
            "CTkFrame": {
                "fg_color": ["#2B2B2B", "#2B2B2B"],
                "border_color": ["#5D5D5D", "#5D5D5D"],
            }
        })