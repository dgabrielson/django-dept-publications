"""
List the Publications available.
"""
#######################
from __future__ import print_function, unicode_literals

import sys

#######################
#######################################################################
from optparse import make_option

from ..models import Publication

ORDER_MAP = {
    "most-recent": "most_recent_order",
    "most-recent-key": "most_recent_order_with_key",
    "bibliography": "bibliography_order",
}

VALID_ORDERINGS = "Valid orderings are: " + ", ".join(ORDER_MAP.keys())

HELP_TEXT = __doc__.strip()
DJANGO_COMMAND = "main"
OPTION_LIST = (
    make_option(
        "--public",
        action="store_true",
        default=False,
        help="Restrict the queryset to public entries only",
    ),
    make_option("--order", help="Specify a queryset ordering. " + VALID_ORDERINGS),
    make_option("--owner", help="Restrict queryset to a particular owner (slug). "),
    make_option(
        "--head", type="int", default=0, help="Restrict the results to the top N"
    ),
    make_option(
        "--tail", type="int", default=0, help="Restrict the results to the bottom N"
    ),
)

# ARGS_USAGE = '...'

#######################################################################

#######################################################################


def main(options, args):
    qs = Publication.objects.active()

    if options["public"]:
        qs = qs.public()

    if options["order"]:
        if options["order"] not in ORDER_MAP:
            print(
                "The order {0!r} is not valid. ".format(options["order"])
                + VALID_ORDERINGS,
                file=sys.stderr,
            )
            return
        ordering_f = getattr(qs, ORDER_MAP[options["order"]])
        qs = ordering_f()

    if options["owner"]:
        if "," in options["owner"]:
            qs = qs.filter(Owner__slug__in=options["owner"].split(","))
        else:
            qs = qs.filter(Owner__slug=options["owner"])

    if options["head"]:
        qs = qs[: int(options["head"])]

    if options["tail"]:
        qs = qs[int(options["tail"]) :]

    for item in qs:
        print("{item.pk}".format(item=item))


#######################################################################
