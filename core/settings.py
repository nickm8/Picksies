"""
Django settings for core project.

This file imports settings from the new modular settings structure.
For Docker setup, use DJANGO_SETTINGS_MODULE environment variable.
"""

# Import settings based on environment
import os

# Use environment variable or default to development
settings_module = os.getenv('DJANGO_SETTINGS_MODULE', 'core.settings.development')

if 'production' in settings_module:
    from .settings.production import *
elif 'development' in settings_module:
    from .settings.development import *
else:
    # Fallback to base settings
    from .settings.base import *

# Legacy compatibility - keep the TODO list for reference
#DONE: Create whole app models
#DONE: Homepage
#DONE:Sidebar
    #DONE: Homepage Pagination
#DONE: Most Popular Movies
    #DONE: Most Popular Movies Pagination
#DONE:Category detail pages
    #DONE: Category Pagination
#DONE:Movie Detail
#DONE:Movie Detail Comment Section (if user is authenticated)
#DONE:Movie Detail Comment Pagination
#DONE:Signup, Login
#DONE:Navbar Profile Operations
#DONE:Change password page
#DONE:Profile Page
#DONE:Make messages a component
#DONE:Clickable Comment Profiles
#DONE:Sitemap
#DONE: Search
#DONE:Paginated Search
#DONE:List all USER comments on User Profile
#DONE: Docker setup with environment-based configuration