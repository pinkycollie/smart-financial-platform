"""
Theme management service for DEAF FIRST platform.
Handles creation and management of white-label themes for resellers.
"""

import os
import json
from datetime import datetime
from flask import current_app
from simple_app import db
from models_reseller import ResellerTheme, Reseller, ResellerBranding, SubResellerBranding
from models_licensing import LicenseeBranding

class ThemeManagementService:
    """
    Service for managing white-label themes for resellers.
    """
    
    def __init__(self, app_config=None):
        """Initialize theme management service with optional configuration"""
        self.app_config = app_config or {}
        self.themes_folder = self.app_config.get('THEMES_FOLDER', 'static/themes')
        
        # Ensure themes directory exists
        os.makedirs(self.themes_folder, exist_ok=True)
        
        # Default themes
        self.default_themes = [
            {
                "theme_name": "DEAF FIRST Blue",
                "description": "The default DEAF FIRST theme with blue accents",
                "primary_color": "#0066CC",
                "secondary_color": "#00AA55",
                "accent_color": "#FF5500",
                "font_family": "Open Sans, sans-serif",
                "background_color": "#FFFFFF",
                "text_color": "#333333",
                "button_style": {
                    "border_radius": "4px",
                    "shadow": "0 2px 4px rgba(0,0,0,0.1)",
                    "padding": "0.5rem 1rem"
                },
                "card_style": {
                    "border_radius": "8px",
                    "shadow": "0 4px 6px rgba(0,0,0,0.1)",
                    "border": "none"
                },
                "header_style": {
                    "background": "linear-gradient(135deg, #0066CC 0%, #004499 100%)",
                    "shadow": "0 2px 4px rgba(0,0,0,0.1)",
                    "text_color": "#FFFFFF"
                }
            },
            {
                "theme_name": "Dark Mode",
                "description": "A dark theme with high contrast for better visibility",
                "primary_color": "#7B68EE",
                "secondary_color": "#4CAF50",
                "accent_color": "#FF9800",
                "font_family": "Roboto, sans-serif",
                "background_color": "#121212",
                "text_color": "#E0E0E0",
                "button_style": {
                    "border_radius": "4px",
                    "shadow": "0 2px 4px rgba(0,0,0,0.25)",
                    "padding": "0.5rem 1rem"
                },
                "card_style": {
                    "border_radius": "8px",
                    "shadow": "0 4px 8px rgba(0,0,0,0.3)",
                    "border": "1px solid #333333"
                },
                "header_style": {
                    "background": "#1E1E1E",
                    "shadow": "0 2px 4px rgba(0,0,0,0.25)",
                    "text_color": "#FFFFFF"
                }
            },
            {
                "theme_name": "Professional",
                "description": "A clean, professional theme suitable for financial advisors",
                "primary_color": "#003366",
                "secondary_color": "#336699",
                "accent_color": "#FF6B35",
                "font_family": "Montserrat, sans-serif",
                "background_color": "#F5F5F5",
                "text_color": "#333333",
                "button_style": {
                    "border_radius": "0",
                    "shadow": "none",
                    "padding": "0.75rem 1.5rem"
                },
                "card_style": {
                    "border_radius": "0",
                    "shadow": "0 1px 3px rgba(0,0,0,0.12)",
                    "border": "1px solid #E0E0E0"
                },
                "header_style": {
                    "background": "#003366",
                    "shadow": "none",
                    "text_color": "#FFFFFF"
                }
            },
            {
                "theme_name": "Vibrant",
                "description": "A bold, colorful theme with high visual impact",
                "primary_color": "#6200EA",
                "secondary_color": "#00C853",
                "accent_color": "#FFC400",
                "font_family": "Nunito, sans-serif",
                "background_color": "#FFFFFF",
                "text_color": "#333333",
                "button_style": {
                    "border_radius": "30px",
                    "shadow": "0 4px 10px rgba(98,0,234,0.2)",
                    "padding": "0.5rem 1.5rem"
                },
                "card_style": {
                    "border_radius": "16px",
                    "shadow": "0 8px 16px rgba(0,0,0,0.1)",
                    "border": "none"
                },
                "header_style": {
                    "background": "linear-gradient(135deg, #6200EA 0%, #B388FF 100%)",
                    "shadow": "0 4px 10px rgba(98,0,234,0.2)",
                    "text_color": "#FFFFFF"
                }
            }
        ]
    
    def get_default_themes(self):
        """
        Get list of default themes.
        
        Returns:
            list: Default themes
        """
        return self.default_themes
    
    def create_default_themes(self):
        """
        Create default themes in the database if they don't exist.
        
        Returns:
            list: Created theme IDs
        """
        # Check existing themes
        existing_themes = ResellerTheme.query.filter(ResellerTheme.reseller_id.is_(None)).all()
        existing_names = [theme.theme_name for theme in existing_themes]
        
        created_ids = []
        
        for theme_data in self.default_themes:
            if theme_data["theme_name"] not in existing_names:
                theme = ResellerTheme(
                    reseller_id=None,  # Global theme
                    theme_name=theme_data["theme_name"],
                    description=theme_data["description"],
                    is_public=True,
                    primary_color=theme_data["primary_color"],
                    secondary_color=theme_data["secondary_color"],
                    accent_color=theme_data["accent_color"],
                    font_family=theme_data["font_family"],
                    background_color=theme_data["background_color"],
                    text_color=theme_data["text_color"],
                    button_style=theme_data["button_style"],
                    card_style=theme_data["card_style"],
                    header_style=theme_data["header_style"]
                )
                
                db.session.add(theme)
                db.session.flush()
                created_ids.append(theme.id)
        
        if created_ids:
            db.session.commit()
            
        return created_ids
    
    def create_theme(self, theme_name, description, primary_color, secondary_color, reseller_id=None, **kwargs):
        """
        Create a new theme.
        
        Args:
            theme_name (str): Theme name
            description (str): Theme description
            primary_color (str): Primary color (hex)
            secondary_color (str): Secondary color (hex)
            reseller_id (int, optional): Reseller ID (None for global)
            **kwargs: Additional theme properties
            
        Returns:
            ResellerTheme: The created theme
        """
        # Check if reseller exists if ID provided
        if reseller_id:
            reseller = Reseller.query.get(reseller_id)
            if not reseller:
                raise ValueError(f"Reseller with ID {reseller_id} not found")
        
        # Create theme
        theme = ResellerTheme(
            reseller_id=reseller_id,
            theme_name=theme_name,
            description=description,
            is_public=kwargs.get('is_public', False) if reseller_id else True,
            primary_color=primary_color,
            secondary_color=secondary_color,
            accent_color=kwargs.get('accent_color'),
            font_family=kwargs.get('font_family', 'Open Sans, sans-serif'),
            background_color=kwargs.get('background_color', '#FFFFFF'),
            text_color=kwargs.get('text_color', '#333333'),
            button_style=kwargs.get('button_style', {}),
            card_style=kwargs.get('card_style', {}),
            header_style=kwargs.get('header_style', {})
        )
        
        # Add to database
        db.session.add(theme)
        db.session.commit()
        
        return theme
    
    def update_theme(self, theme_id, **kwargs):
        """
        Update a theme.
        
        Args:
            theme_id (int): Theme ID
            **kwargs: Properties to update
            
        Returns:
            ResellerTheme: The updated theme
        """
        theme = ResellerTheme.query.get(theme_id)
        if not theme:
            raise ValueError(f"Theme with ID {theme_id} not found")
        
        # Update properties
        for key, value in kwargs.items():
            if hasattr(theme, key):
                setattr(theme, key, value)
        
        db.session.commit()
        return theme
    
    def get_theme(self, theme_id):
        """
        Get a theme by ID.
        
        Args:
            theme_id (int): Theme ID
            
        Returns:
            ResellerTheme: The theme
        """
        return ResellerTheme.query.get(theme_id)
    
    def get_available_themes(self, reseller_id=None):
        """
        Get all themes available to a reseller.
        
        Args:
            reseller_id (int, optional): Reseller ID
            
        Returns:
            list: List of available themes
        """
        # Get public global themes
        query = ResellerTheme.query.filter(ResellerTheme.reseller_id.is_(None), ResellerTheme.is_public.is_(True))
        
        # If reseller ID provided, include their custom themes
        if reseller_id:
            query = query.union(ResellerTheme.query.filter_by(reseller_id=reseller_id))
        
        return query.all()
    
    def apply_theme_to_reseller(self, theme_id, reseller_id):
        """
        Apply a theme to a reseller's branding.
        
        Args:
            theme_id (int): Theme ID
            reseller_id (int): Reseller ID
            
        Returns:
            ResellerBranding: The updated branding
        """
        theme = self.get_theme(theme_id)
        if not theme:
            raise ValueError(f"Theme with ID {theme_id} not found")
        
        branding = ResellerBranding.query.filter_by(reseller_id=reseller_id).first()
        if not branding:
            branding = ResellerBranding(reseller_id=reseller_id)
            db.session.add(branding)
        
        # Apply theme properties
        branding.primary_color = theme.primary_color
        branding.secondary_color = theme.secondary_color
        branding.accent_color = theme.accent_color
        branding.font_family = theme.font_family
        
        # Apply custom CSS based on theme
        css = self._generate_css_from_theme(theme)
        branding.custom_css = css
        
        db.session.commit()
        return branding
    
    def apply_theme_to_sub_reseller(self, theme_id, sub_reseller_id):
        """
        Apply a theme to a sub-reseller's branding.
        
        Args:
            theme_id (int): Theme ID
            sub_reseller_id (int): Sub-reseller ID
            
        Returns:
            SubResellerBranding: The updated branding
        """
        theme = self.get_theme(theme_id)
        if not theme:
            raise ValueError(f"Theme with ID {theme_id} not found")
        
        branding = SubResellerBranding.query.filter_by(sub_reseller_id=sub_reseller_id).first()
        if not branding:
            branding = SubResellerBranding(sub_reseller_id=sub_reseller_id)
            db.session.add(branding)
        
        # Apply theme properties
        branding.primary_color = theme.primary_color
        branding.secondary_color = theme.secondary_color
        
        db.session.commit()
        return branding
    
    def apply_theme_to_licensee(self, theme_id, licensee_id):
        """
        Apply a theme to a licensee's branding.
        
        Args:
            theme_id (int): Theme ID
            licensee_id (int): Licensee ID
            
        Returns:
            LicenseeBranding: The updated branding
        """
        theme = self.get_theme(theme_id)
        if not theme:
            raise ValueError(f"Theme with ID {theme_id} not found")
        
        branding = LicenseeBranding.query.filter_by(licensee_id=licensee_id).first()
        if not branding:
            branding = LicenseeBranding(licensee_id=licensee_id)
            db.session.add(branding)
        
        # Apply theme properties
        branding.primary_color = theme.primary_color
        branding.secondary_color = theme.secondary_color
        branding.accent_color = theme.accent_color
        branding.font_family = theme.font_family
        
        # Apply custom CSS based on theme
        css = self._generate_css_from_theme(theme)
        branding.custom_css = css
        
        db.session.commit()
        return branding
    
    def get_theme_preview(self, theme_id):
        """
        Get HTML and CSS for a theme preview.
        
        Args:
            theme_id (int): Theme ID
            
        Returns:
            dict: Preview HTML and CSS
        """
        theme = self.get_theme(theme_id)
        if not theme:
            raise ValueError(f"Theme with ID {theme_id} not found")
        
        # Generate CSS
        css = self._generate_css_from_theme(theme)
        
        # Generate preview HTML
        html = self._generate_preview_html(theme)
        
        return {
            "css": css,
            "html": html,
            "theme": {
                "id": theme.id,
                "name": theme.theme_name,
                "description": theme.description,
                "primary_color": theme.primary_color,
                "secondary_color": theme.secondary_color,
                "accent_color": theme.accent_color,
                "font_family": theme.font_family,
                "background_color": theme.background_color,
                "text_color": theme.text_color
            }
        }
    
    def create_theme_from_reseller(self, reseller_id, theme_name, description, is_public=False):
        """
        Create a theme based on a reseller's current branding.
        
        Args:
            reseller_id (int): Reseller ID
            theme_name (str): Theme name
            description (str): Theme description
            is_public (bool): Whether theme is public
            
        Returns:
            ResellerTheme: The created theme
        """
        branding = ResellerBranding.query.filter_by(reseller_id=reseller_id).first()
        if not branding:
            raise ValueError(f"No branding found for reseller ID {reseller_id}")
        
        # Create theme with branding properties
        theme = ResellerTheme(
            reseller_id=reseller_id,
            theme_name=theme_name,
            description=description,
            is_public=is_public,
            primary_color=branding.primary_color,
            secondary_color=branding.secondary_color,
            accent_color=branding.accent_color,
            font_family=branding.font_family,
            background_color="#FFFFFF",  # Default
            text_color="#333333",  # Default
            button_style={},  # Default
            card_style={},  # Default
            header_style={}  # Default
        )
        
        # Add to database
        db.session.add(theme)
        db.session.commit()
        
        return theme
    
    def _generate_css_from_theme(self, theme):
        """Generate CSS from theme properties."""
        css = f"""
        :root {{
            --brand-primary: {theme.primary_color};
            --brand-secondary: {theme.secondary_color};
            --brand-accent: {theme.accent_color or '#FF5500'};
            --brand-background: {theme.background_color or '#FFFFFF'};
            --brand-text: {theme.text_color or '#333333'};
        }}
        
        body {{
            font-family: {theme.font_family or 'Open Sans, sans-serif'};
            background-color: var(--brand-background);
            color: var(--brand-text);
        }}
        
        .btn-primary {{
            background-color: var(--brand-primary);
            border-color: var(--brand-primary);
        }}
        
        .btn-primary:hover, .btn-primary:focus, .btn-primary:active {{
            background-color: {self._adjust_color(theme.primary_color, -20)};
            border-color: {self._adjust_color(theme.primary_color, -20)};
        }}
        
        .btn-secondary {{
            background-color: var(--brand-secondary);
            border-color: var(--brand-secondary);
        }}
        
        .btn-secondary:hover, .btn-secondary:focus, .btn-secondary:active {{
            background-color: {self._adjust_color(theme.secondary_color, -20)};
            border-color: {self._adjust_color(theme.secondary_color, -20)};
        }}
        
        a {{
            color: var(--brand-primary);
        }}
        
        a:hover {{
            color: {self._adjust_color(theme.primary_color, -20)};
        }}
        
        .bg-primary {{
            background-color: var(--brand-primary) !important;
        }}
        
        .bg-secondary {{
            background-color: var(--brand-secondary) !important;
        }}
        
        .text-primary {{
            color: var(--brand-primary) !important;
        }}
        
        .text-secondary {{
            color: var(--brand-secondary) !important;
        }}
        
        .border-primary {{
            border-color: var(--brand-primary) !important;
        }}
        
        .border-secondary {{
            border-color: var(--brand-secondary) !important;
        }}
        """
        
        # Add button styling if provided
        if theme.button_style:
            button_style = theme.button_style
            css += f"""
            .btn {{
                border-radius: {button_style.get('border_radius', '4px')};
                box-shadow: {button_style.get('shadow', '0 2px 4px rgba(0,0,0,0.1)')};
                padding: {button_style.get('padding', '0.5rem 1rem')};
            }}
            """
        
        # Add card styling if provided
        if theme.card_style:
            card_style = theme.card_style
            css += f"""
            .card {{
                border-radius: {card_style.get('border_radius', '8px')};
                box-shadow: {card_style.get('shadow', '0 4px 6px rgba(0,0,0,0.1)')};
                border: {card_style.get('border', 'none')};
            }}
            """
        
        # Add header styling if provided
        if theme.header_style:
            header_style = theme.header_style
            css += f"""
            .navbar, .header, .jumbotron {{
                background: {header_style.get('background', 'var(--brand-primary)')};
                box-shadow: {header_style.get('shadow', '0 2px 4px rgba(0,0,0,0.1)')};
                color: {header_style.get('text_color', '#FFFFFF')};
            }}
            """
        
        return css
    
    def _generate_preview_html(self, theme):
        """Generate preview HTML for a theme."""
        html = f"""
        <div class="theme-preview">
            <div class="card">
                <div class="card-header bg-primary text-white">
                    <h4>Theme Preview: {theme.theme_name}</h4>
                </div>
                <div class="card-body">
                    <div class="row mb-4">
                        <div class="col-md-6">
                            <h5>Buttons</h5>
                            <button class="btn btn-primary mb-2 me-2">Primary Button</button>
                            <button class="btn btn-secondary mb-2 me-2">Secondary Button</button>
                            <button class="btn btn-outline-primary mb-2 me-2">Outline Primary</button>
                            <button class="btn btn-outline-secondary mb-2">Outline Secondary</button>
                        </div>
                        <div class="col-md-6">
                            <h5>Colors</h5>
                            <div class="d-flex mb-2">
                                <div class="me-2 p-2 rounded" style="background-color: {theme.primary_color}; color: white;">Primary</div>
                                <div class="me-2 p-2 rounded" style="background-color: {theme.secondary_color}; color: white;">Secondary</div>
                                <div class="p-2 rounded" style="background-color: {theme.accent_color or '#FF5500'}; color: white;">Accent</div>
                            </div>
                            <div class="d-flex">
                                <div class="me-2 p-2 rounded" style="background-color: {theme.background_color or '#FFFFFF'}; border: 1px solid #ddd;">Background</div>
                                <div class="p-2 rounded" style="background-color: {theme.text_color or '#333333'}; color: white;">Text</div>
                            </div>
                        </div>
                    </div>
                    
                    <div class="row mb-4">
                        <div class="col-md-6">
                            <h5>Typography</h5>
                            <p>Body text in <span style="font-family: {theme.font_family or 'Open Sans, sans-serif'};">{theme.font_family or 'Open Sans, sans-serif'}</span></p>
                            <p class="text-primary">Primary text color</p>
                            <p class="text-secondary">Secondary text color</p>
                            <a href="#">Link style</a>
                        </div>
                        <div class="col-md-6">
                            <h5>Card Example</h5>
                            <div class="card">
                                <div class="card-body">
                                    <h5 class="card-title">Card Title</h5>
                                    <p class="card-text">This is an example card with the theme styling applied.</p>
                                    <a href="#" class="btn btn-primary btn-sm">Action</a>
                                </div>
                            </div>
                        </div>
                    </div>
                    
                    <div class="alert alert-primary" role="alert">
                        This is a primary alert with theme colors.
                    </div>
                </div>
                <div class="card-footer">
                    <span class="text-muted">Theme ID: {theme.id}</span>
                </div>
            </div>
        </div>
        """
        
        return html
    
    def _adjust_color(self, hex_color, amount):
        """Adjust a hex color by the given amount."""
        if not hex_color:
            return hex_color
            
        # Remove # if present
        hex_color = hex_color.lstrip('#')
        
        # Convert to RGB
        r = int(hex_color[0:2], 16)
        g = int(hex_color[2:4], 16)
        b = int(hex_color[4:6], 16)
        
        # Adjust
        r = max(0, min(255, r + amount))
        g = max(0, min(255, g + amount))
        b = max(0, min(255, b + amount))
        
        # Convert back to hex
        return f"#{r:02x}{g:02x}{b:02x}"

# Initialize a single instance to be used application-wide
theme_management_service = ThemeManagementService()