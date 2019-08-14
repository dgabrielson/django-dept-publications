"""
Sitemap for publications application
"""
import datetime

from django.contrib.sitemaps import Sitemap
from django.db.models import Max
from django.urls import reverse
from django.utils.timezone import now
from people.models import Person


class Publication_Sitemap(Sitemap):
    """
    Sitemap for Page objects
    """

    #    priority = 0.5
    #    changefreq = 'monthly'

    def items(self):
        """
        Return the items for this map
        """
        return Person.objects.filter(
            active=True, slug__isnull=False, flags__slug="publications"
        )

    def location(self, item):
        return reverse("publications-personal-list", kwargs={"slug": item.slug})

    def lastmod(self, item):
        """
        Last Modification datetime.
        """
        publication_list = item.publication_set.active()
        if publication_list:
            return publication_list.aggregate(dt=Max("Last_Updated"))["dt"]
        else:
            return now()
