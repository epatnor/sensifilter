# sensifilter/__init__.py

# Init-fil för sensifilter-paketet
# Gör endast analyze_image tillgänglig publikt

from .analyze import analyze_image

__all__ = ["analyze_image"]
