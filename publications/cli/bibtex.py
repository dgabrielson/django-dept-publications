"""
Generate BibTeX text for Publications.

If no reference keys are given, then the result is the same behaviour
as seen in the main publication view (Publication_ListView)
"""
#######################
from __future__ import print_function, unicode_literals

import codecs

# set unicode piping:
import sys

from ..models import Publication
from ..views import Publication_ListView

#######################
#######################################################################

HELP_TEXT = __doc__.strip()
DJANGO_COMMAND = "main"
OPTION_LIST = ()
ARGS_USAGE = "[reference-key] [...]"

#######################################################################

sys.stdout = codecs.getwriter("utf-8")(sys.stdout)

#######################################################################


def main(options, args):

    if args:
        queryset = Publication.objects.filter(pk__in=args)
    else:
        queryset = Publication_ListView().get_queryset()

    print("\n\n".join(queryset.as_bibtex()))


#######################################################################
