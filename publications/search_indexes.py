"""
Haystack search indexes for Publications application.
"""
###############################################################

from haystack import indexes

from .models import Publication

###############################################################


class PublicationIndex(indexes.SearchIndex, indexes.Indexable):
    text = indexes.CharField(document=True, use_template=True)
    pub_date = indexes.DateTimeField(model_attr="Last_Updated")

    # author = indexes.CharField(model_attr='Owner')
    # NOTE: including the author greatly increases the score
    #   when the author's name is searched for.

    def get_model(self):
        return Publication

    def index_queryset(self, using=None):
        """Used when the entire index for model is updated."""
        return self.get_model().objects.active()


###############################################################
