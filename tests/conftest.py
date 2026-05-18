"""
CalcPaper test configuration.

Configures Hypothesis settings for property-based testing with a minimum
of 100 iterations per test, as specified in the design document.
"""

from __future__ import annotations

from hypothesis import settings, HealthCheck

# Register a custom Hypothesis profile for CalcPaper property tests
settings.register_profile(
    "calcpaper",
    max_examples=100,
    suppress_health_check=[HealthCheck.too_slow],
)

# Set as default profile
settings.load_profile("calcpaper")
