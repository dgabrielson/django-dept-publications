"""
The DEFAULT configuration is loaded when the PUBLICATIONS_CONFIG dictionary
is not present in your settings.
"""

CONFIG_NAME = "PUBLICATIONS_CONFIG"  # must be uppercase!

DEFAULT = {
    # The number of publications which show up from
    #   Publication.objects.recent()
    "recent_count": 5,
    # The number of years which show up in the main page
    "recent_years": 2,
    # The help string for the active flag
    "active_help": "If this is not set, the publication will not appear anywhere.",
    # The help string for the public flag
    "public_help": "Show this publication in the main list",
    # re-write $...$ as \(...\)
    "inline-math-mode-rewrite": False,
    "preserve-math-mode": True,
}

from django.conf import settings


def get(setting):
    """
    get(setting) -> value

    setting should be a string representing the application settings to
    retrieve.
    """
    assert setting in DEFAULT, "the setting %r has no default value" % setting
    app_settings = getattr(settings, CONFIG_NAME, DEFAULT)
    return app_settings.get(setting, DEFAULT[setting])


def get_all():
    """
    Return all current settings as a dictionary.
    """
    app_settings = getattr(settings, CONFIG_NAME, DEFAULT)
    return dict(
        [(setting, app_settings.get(setting, DEFAULT[setting])) for setting in DEFAULT]
    )
