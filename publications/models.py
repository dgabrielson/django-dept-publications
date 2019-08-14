# -*- coding: utf-8 -*-
###############
from __future__ import print_function, unicode_literals

import sys

from django.conf import settings
from django.db import models
from django.template import Context, Template

###############
from django.utils import six
from django.utils.encoding import python_2_unicode_compatible
from django.utils.html import escape
from django.utils.safestring import mark_safe
from people.models import Person

from . import conf
from .utils import fix_reference_key, latex_unicode_fixes

# Publication Database
# See http://en.wikipedia.org/wiki/BibTeX for the underlying idea.

# required for as_html() and friends

DOCUTILS_SETTINGS = getattr(settings, "RESTRUCTUREDTEXT_FILTER_SETTINGS", {})

RECENT_COUNT = conf.get("recent_count")

############################################################################


@python_2_unicode_compatible
class Entry_Type(models.Model):

    Active = models.BooleanField(default=True)
    Last_Updated = models.DateTimeField(auto_now=True, editable=False)

    Name = models.SlugField(primary_key=True)
    Description = models.CharField(max_length=512)
    Required_Fields = models.CharField(max_length=512)
    Optional_Fields = models.CharField(max_length=512)

    html_Template = models.TextField(blank=True, null=True)
    latex_Template = models.TextField(blank=True, null=True)
    rtf_Template = models.TextField(blank=True, null=True)

    # there are (at least) 2 significant roadblocks to resolving the templates:
    #   1. Each field MAY have restructuredtext mark up, for e.g., italics
    #           http://docutils.sourceforge.net/docs/ref/rst/restructuredtext.html
    #   2. Each field MAY have unicode, for e.g., math symbols
    #           LaTeX may need: \usepackage[utf8]{inputenc}
    #   3. I don't know squat about RTF
    #           Start at: http://en.wikipedia.org/wiki/Rich_Text_Format

    # Find a way to Cache the compiled templates!

    def __str__(self):
        return self.Name

    class Meta:
        ordering = ["Name"]
        verbose_name = "Entry Type"

    def get_only_required_list(self):
        """
        return a list of the required fields.  No slash processing.
        """
        if not self.Required_Fields:
            return []
        return self.Required_Fields.split(",")

    def get_required_field_list(self):
        """
        returns a list of any required fields (including slash fields)
        """
        L = self.get_only_required_list()
        M = []
        for l in L:
            M += l.split("/")
        return list(set(M))

    def is_required(self, field_name):
        """
        returns True only if field_name is required BY ITSELF (not a /)
        """
        return field_name in self.get_only_required_list()

    def get_optional_field_list(self):
        if not self.Optional_Fields:
            return []
        L = self.Optional_Fields.split(",")
        M = []
        for l in L:
            M += l.split("/")
        return list(set(M))

    def get_field_list(self):
        return list(
            set(self.get_required_field_list() + self.get_optional_field_list())
        )

    _Entry_Type__compiledTemplates = {}  # for caching.

    def get_template(self, target):
        """
        returns the compiled template for the given target.
        """
        try:
            return self.__compiledTemplates[target]
        except KeyError:
            if target not in ["html", "latex", "rtf"]:
                return None
            tmpl_src = getattr(self, "%s_Template" % target)
            #   do not cache: uncomment next line:
            return Template(tmpl_src)
            # CACHE:
            self.__compiledTemplates[target] = Template(tmpl_src)
            return self.__compiledTemplates[target]


############################################################################

HELP_TEXT = {
    "Type": escape("Begin by selecting the type of publication"),
    "URL": escape("(Optional) A link to an online version or further information"),
    "Active": escape(conf.get("active_help")),
    "public": escape(conf.get("public_help")),
    "address": escape(
        "Publisher's address (usually just the city, but can be the full address for lesser-known publishers)"
    ),
    "author": escape(
        'The name(s) of the author(s) (in the case of more than one author, separated by "and", very long lists can be truncated with "and others"), in the format "Familyname, G." or "Familyname, Given"'
    ),
    "booktitle": escape("The title of the book, if only part of it is being cited"),
    "chapter": escape("The chapter number"),
    "edition": escape('The edition of a book, long form (such as "first" or "second")'),
    "editor": escape("The name(s) of the editor(s)"),
    "howpublished": escape(
        "How it was published, if the publishing method is nonstandard"
    ),
    "institution": escape(
        "The institution that was involved in the publishing, but not necessarily the publisher"
    ),
    "journal": escape("The journal or magazine the work was published in"),
    "key": escape(
        'A hidden field used for specifying or overriding the alphabetical order of entries (when the "author" and "editor" fields are missing). Note that this is very different from the Reference_Key that is used to cite or cross-reference the entry.'
    ),
    "month": escape(
        "The month of publication (or, if unpublished, the month of creation)"
    ),
    "note": escape("Miscellaneous extra information"),
    "number": escape(
        'The "number" of a journal, magazine, or tech-report, if applicable. (Most publications have a "volume", but no "number" field.)'
    ),
    "organization": escape("The conference sponsor"),
    "pages": escape(
        "Page numbers, separated either by commas or double-hyphens. For books, the total number of pages."
    ),
    "publisher": escape("The publisher's name"),
    "school": escape("The school where the thesis was written"),
    "series": escape(
        'The series of books the book was published in (e.g. "The Hardy Boys" or "Lecture Notes in Computer Science")'
    ),
    "title": escape(
        "The title of the work.  Use *asterisks* for italics and unicode for symbols."
    ),
    "type": escape('The type of tech-report, for example, "Research Note"'),
    "volume": escape("The volume of a journal or multi-volume book"),
    "year": escape(
        "The year of publication (or, if unpublished, the year of creation)"
    ),
}

############################################################################


class PublicationQuerySet(models.query.QuerySet):
    """
    Custom query set for publications.
    """

    def active(self):
        """
        Returns only active items in this queryset
        """
        return self.filter(Active=True)

    def recent(self):
        """
        Limits the number returned, also applies the active() filter.
        """
        return self.most_recent_order_with_key()[:RECENT_COUNT]

    def as_bibtex(self, flat=False, include_url=False):
        """
        Returns a list of text strings representing the current query set
        as bibtex entries.

        If ``flat == True``, then this list is joined into a single text
        string.
        """
        result = []
        for e in self:
            result.append(e.as_bibtex())
        if flat:
            result = "\n\n".join(result)
        return result

    def public(self):
        """
        Filters out those publications which are not public.
        """
        return self.filter(public=True)

    def set_owner(self, owner):
        """
        Sets the owner on all Publications.
        """
        for e in self:
            e.Owner = owner

    def save_all(self):
        """
        Save all publications
        (Make this a transaciton, somehow?)
        """
        for e in self:
            e.save()

    def most_recent_order(self):
        """
        Sort this query set into chronolgical order (most recent first).
        Note that the sort key is ignored here.
        """
        return self.order_by("-year", "-month", "author", "editor", "title")

    def most_recent_order_with_key(self):
        """
        Sort this query set into chronolgical order (most recent first).
        Note that the sort key is *not* ignored here.
        """
        return self.order_by("key", "-year", "-month", "author", "editor", "title")

    def bibliography_order(self):
        """
        Sort this query set into alphabetical order (typical
        bibliographic ordering).
        """
        return self.order_by("key", "author", "editor", "year", "month", "title")


class PublicationManager(models.Manager):
    """
    Custom Manager for Publications, just a wrapper for returning the
    PublicationQuerySet
    """

    def get_queryset(self):
        """
        Return the custom QuerySet
        """
        return PublicationQuerySet(self.model)

    def load_from_bibtex(self, text, is_stream=False):
        """
        Take a stream of text, process it as BibTeX, and return
        a list of (unsaved) Publication objects.

        ** Note that the publication Owner is *not set* by this method. **
        """
        import bibtexparser
        from bibtexparser.latexenc import latex_to_unicode
        from bibtexparser.customization import convert_to_unicode
        from io import StringIO

        def _field_map(field):
            """
            Map bibtexparser entry field name to Publication field
            """
            if field == "ID":
                return "Reference_Key"
            if field == "ENTRYTYPE":
                return None
            if field == "url":
                return "URL"
            if hasattr(Publication, field):
                return field
            f = field.lower()
            if hasattr(Publication, f):
                return f
            f = field.upper()
            if hasattr(Publication, f):
                return f
            return None

        def _value_map(attrname, value):
            # fix unicode em-dash and en-dash
            if attrname == "Reference_Key":
                return fix_reference_key(value)
            if attrname == "URL":
                # do not mangle urls
                return value
            for fixer in [latex_unicode_fixes]:
                value = fixer(value)
            return value

        def _pub_from_entry(entry):
            key = entry.get("ID", None)
            entry_type = entry.get("ENTRYTYPE", None)
            pub = Publication()
            pub.Reference_Key = key
            pub.Type = Entry_Type.objects.get(Name=entry_type)
            for field in entry:
                attrname = _field_map(field)
                if attrname is None:
                    continue
                value = _value_map(attrname, entry[field])
                setattr(pub, attrname, value)
            return pub

        if not is_stream and isinstance(text, bytes):
            text = text.decode("utf-8")

        bibloader = bibtexparser.load if is_stream else bibtexparser.loads
        data = bibloader(text)
        return [_pub_from_entry(entry) for entry in data.entries]


PublicationManager = PublicationManager.from_queryset(PublicationQuerySet)


@python_2_unicode_compatible
class Publication(models.Model):

    Active = models.BooleanField(default=True, help_text=HELP_TEXT["Active"])
    public = models.BooleanField(default=True, help_text=HELP_TEXT["public"])
    Last_Updated = models.DateTimeField(auto_now=True, editable=False)

    Reference_Key = models.SlugField()
    Owner = models.ForeignKey(
        Person,
        on_delete=models.CASCADE,
        limit_choices_to={"active": True, "flags__slug": "publications"},
        help_text='Only people with the "publications" flag are shown',
    )
    Type = models.ForeignKey(
        Entry_Type, on_delete=models.PROTECT, help_text=HELP_TEXT["Type"]
    )
    URL = models.URLField(
        blank=True,
        null=True,
        help_text=HELP_TEXT["URL"],
        verbose_name="URL",
        max_length=512,
    )  # optional link to the Item

    # BibTeX fields:
    address = models.TextField(null=True, blank=True, help_text=HELP_TEXT["address"])
    author = models.CharField(
        null=True, blank=True, max_length=512, help_text=HELP_TEXT["author"]
    )
    booktitle = models.CharField(
        null=True, blank=True, max_length=256, help_text=HELP_TEXT["booktitle"]
    )
    chapter = models.CharField(
        null=True, blank=True, max_length=128, help_text=HELP_TEXT["chapter"]
    )
    edition = models.CharField(
        null=True, blank=True, max_length=128, help_text=HELP_TEXT["edition"]
    )
    editor = models.CharField(
        null=True, blank=True, max_length=256, help_text=HELP_TEXT["editor"]
    )
    howpublished = models.CharField(
        null=True, blank=True, max_length=256, help_text=HELP_TEXT["howpublished"]
    )
    institution = models.CharField(
        null=True, blank=True, max_length=256, help_text=HELP_TEXT["institution"]
    )
    journal = models.CharField(
        null=True, blank=True, max_length=256, help_text=HELP_TEXT["journal"]
    )
    key = models.CharField(
        null=True, blank=True, max_length=256, help_text=HELP_TEXT["key"]
    )
    month = models.CharField(
        null=True, blank=True, max_length=32, help_text=HELP_TEXT["month"]
    )
    note = models.TextField(null=True, blank=True, help_text=HELP_TEXT["note"])
    number = models.CharField(
        null=True, blank=True, max_length=32, help_text=HELP_TEXT["number"]
    )
    organization = models.CharField(
        null=True, blank=True, max_length=256, help_text=HELP_TEXT["organization"]
    )
    pages = models.CharField(
        null=True, blank=True, max_length=64, help_text=HELP_TEXT["pages"]
    )
    publisher = models.CharField(
        null=True, blank=True, max_length=256, help_text=HELP_TEXT["publisher"]
    )
    school = models.CharField(
        null=True, blank=True, max_length=256, help_text=HELP_TEXT["school"]
    )
    series = models.CharField(
        null=True, blank=True, max_length=256, help_text=HELP_TEXT["series"]
    )
    title = models.CharField(
        null=True, blank=True, max_length=512, help_text=HELP_TEXT["title"]
    )
    type = models.CharField(
        null=True, blank=True, max_length=256, help_text=HELP_TEXT["type"]
    )
    volume = models.CharField(
        null=True, blank=True, max_length=32, help_text=HELP_TEXT["volume"]
    )
    year = models.CharField(
        null=True, blank=True, max_length=32, help_text=HELP_TEXT["year"]
    )

    objects = PublicationManager()

    class Meta:
        unique_together = (("Owner", "Reference_Key"),)

    def sort_key(self):
        if self.key:
            return self.key
        if self.author:
            return self.author
        if self.editor:
            return self.editor
        return self.Reference_Key  # not a good fallback!

    def __str__(self):
        return self.Reference_Key

    def save(self):
        """
        This bit of magic is to allow auto-incremening (ish) Reference Keys
        """
        if not self.Reference_Key:
            refkey = self.guess_Reference_Key()
        super(Publication, self).save()
        # should check for failure, in which case back off and retry...
        """
from django.core.db import dbmod
try:
u2.save()
except dbmod.Database.IntegrityError:
//handle error
pass        """

    class Meta:
        ordering = ["-year", "author", "title"]

    def guess_Reference_Key(self):
        def __next_sequence(seq):
            begin = seq[:-1]
            last = seq[-1]
            k = ord(last)
            k += 1
            if k > ord("z"):
                return begin + "aa"
            return begin + chr(k)

        if self.Reference_Key:
            return self.Reference_Key
        # else: guess!
        guess = self.Owner.slug + "-"
        if self.year:
            guess += str(self.year) + "-"
        # check:
        others = list(Publication.objects.filter(Reference_Key__istartswith=guess))
        others.sort(key=lambda e: e.Reference_Key.lower())
        if not others:
            guess += "a"
            self.Reference_Key = guess
            return guess
        last = others[-1]
        sequence = last.Reference_Key.split("-")[-1]
        guess += __next_sequence(sequence)
        self.Reference_Key = guess
        return guess

    def check_field(self, field_name):
        if hasattr(self, field_name):
            return bool(getattr(self, field_name))
        return False

    def check_required(self):
        """
        publication.check_required() -> <list>

        The list contains the required fields that were not present.
        if not list, then check passed.
        """
        names = self.Type.Required_Fields.split(",")
        # note that a name MAY contain a slash, which indicates that AT LEAST ONE of the
        #   field in that group is required.
        results = []
        for name in names:
            if "/" in name:
                # check OR conditional
                flag = bool(sum([self.check_field(sub) for sub in name.split("/")]))
            else:
                flag = self.check_field(name)
            if not flag:
                results.append(name)
        return results

    def validate(self):
        errors = super(Publication, self).validate()
        msg = "This field is required."
        for field in self.check_required():
            try:
                errors[field].append(msg)
            except KeyError:
                errors[field] = [msg]
        return errors

    def __next_state(self, c, state, math_mode):

        if state == "?ESCAPE?":
            if c in ["*", "{", "}", "\\"]:
                return "ESCAPE"
            if c in ["(", ")", "[", "]"]:
                return "MATH-DELIM"
            return

        if c == "\\":
            return "?ESCAPE?"

        if c == "$":
            return "MATH-DELIM"

        if c == "{" and state != "protect_case":
            if math_mode:
                return "brace_match"
            return "protect_case"
        if c == "}":
            if math_mode:
                return "STOP:brace_match"
            if state == "protect_case":
                return "STOP:protect_case"
            else:
                return "SKIP"

        if state == "?italic?":
            if c == "*":
                return "bold"
            else:
                return "italic"

        if state == "bold":
            if c == "*":
                return "?not-bold?"
            # else no change

        if state == "?not-bold?":
            if c == "*":
                return "STOP:bold"
            else:
                return "italic"

        if state == "italic":
            if c == "*":
                return "STOP:italic"
            # else no change

        # default case:
        if c == "*":
            return "?italic?"
        if c == "{":
            return "protect_case"

        # default: no change

    def __build_parse_tree(
        self, string, pos=0, current_state="normal", in_math_mode=False
    ):
        """
        Returns a list of dictionaries, which map a state to a subobject.
        A state can be:
            'normal', 'italic', 'bold', 'protect_case'
        A subobject can be:
            another list of state maps, or a string.
        Ultimately, all state maps have string values.

        TODO: ~ or similar for non-breaking spaces
        """
        result = []
        fragment = ""
        preserve_math_mode = conf.get("preserve-math-mode")
        # print('START build parse tree:', string,'; pos =', pos)
        # print('    partial:', string[pos:])
        # print('  math mode:', in_math_mode)
        # print('      state:', current_state)

        while pos < len(string):
            c = string[pos]
            new_state = self.__next_state(c, current_state, in_math_mode)
            if new_state is not None:
                if new_state.startswith("?"):
                    if pos + 1 == len(string):
                        break
                    # print('next state look-ahead math_mode=', in_math_mode)
                    # print('now:', new_state)
                    new_state = self.__next_state(
                        string[pos + 1], new_state, in_math_mode
                    )  # peek
                    # print('peek:', new_state)
                    if new_state is None and in_math_mode and preserve_math_mode:
                        # not escaping...
                        # print('not escaping b/c math mode preservation')
                        fragment += "\\"
                    if new_state is None:
                        new_state = current_state  # rewind
                    if new_state in ["bold", "STOP:bold", "ESCAPE"]:
                        pos += 1
                    if new_state == "ESCAPE":
                        # print('ESCAPE: math_mode=', in_math_mode)
                        fragment += string[pos]
                    if new_state == "MATH-DELIM":
                        fragment += string[pos]
                        in_math_mode = not in_math_mode
                        # print('in_math_mode', in_math_mode)

                if new_state in ["bold", "italic", "protect_case"]:
                    # actual state transition
                    if fragment:
                        result.append(fragment)
                        fragment = ""
                    pos, subobj, in_math_mode = self.__build_parse_tree(
                        string, pos + 1, new_state, in_math_mode
                    )
                    result.append([new_state, subobj])

                if new_state == "MATH-DELIM":
                    fragment += string[pos]
                    in_math_mode = not in_math_mode
                    # print('in_math_mode', in_math_mode)

                if new_state == "SKIP":
                    pass  # do nothing

                if new_state == "brace_match":
                    fragment += string[pos]
                if new_state == "STOP:brace_match":
                    fragment += string[pos]
                    new_state = "normal"
                if new_state.startswith("STOP:"):
                    break
            else:
                fragment += c
            pos += 1

        if fragment:
            result.append(fragment)
        return pos, result, in_math_mode

    def __render_tree(self, tree, target, text_transform=None):
        """
        """

        def __escape_latex_specials(s):
            for c in ["&", "#"]:
                s = s.replace(c, "\\" + c)
            return s

        # end __escape_latex_specials

        def __fix_inline_math(s):
            # TODO: fix this to deal with '\\$'
            vm = ""
            state = False
            for c in s:
                if c == "$":
                    if not state:
                        vm += "\\("
                    else:
                        vm += "\\)"
                    state = not state
                else:
                    vm += c
            return vm

        # end __fix_inline_math

        # __render_tree() proper begins
        if isinstance(tree, six.string_types):
            if target == "latex":
                return __escape_latex_specials(tree)
            return tree
        result = ""
        for item in tree:
            if isinstance(item, six.string_types):
                result += item
            else:
                state, subobj = item
                if state == "normal":
                    result += self.__render_tree(subobj, target)
                elif state == "italic":
                    if target == "html":
                        result += "<i>%s</i>" % self.__render_tree(subobj, target)
                    elif target == "latex":
                        result += "\\textit{%s}" % self.__render_tree(subobj, target)
                    else:
                        assert False  # don't know how to render italics for this target
                elif state == "bold":
                    if target == "html":
                        result += "<b>%s</b>" % self.__render_tree(subobj, target)
                    elif target == "latex":
                        result += "\\textbf{%s}" % self.__render_tree(subobj, target)
                    else:
                        assert False  # don't know how to render bold for this target
                elif state == "protect_case":
                    if text_transform is None:
                        result += self.__render_tree(subobj, target)
                    else:
                        assert False  # can't deal with text transforms yet.
        if target == "latex":
            result = __escape_latex_specials(result)
        if conf.get("inline-math-mode-rewrite") and result.count("$") % 2 == 0:
            result = __fix_inline_math(result)
        return result

    def proc_for_target(self, field, value, target):
        """
        Using docutils is not sufficient here, as it wants to wrap every value
        as a paragraph.  Since the synxtax is quite simplified, its probably
        best to roll my own:

        \* \{ \}    - escaped literals
        *italics*
        **bold**
        {Protect} {C}ase    - from BibTeX

        NOTE: value MUST be a string when this is called
        """
        if not value:  # nothing to do!
            return ""

        # special field processing here, i.e., for Authors
        if field == "author" and target in ["html", "rtf"]:
            # deal with AND in any case...
            for a in [" AND ", " ANd ", " AnD ", " aND ", " And ", " aNd ", " anD "]:
                value = value.replace(a, " and ")
            authors = value.split(" and ")
            if len(authors) > 1:
                if authors[-1] == "others":
                    # last = 'et~al.'
                    last = "et al."
                else:
                    last = authors[-1]
                # TODO: make both semicolon and the joining word "and" cfg opts.
                value = "; ".join(authors[:-1]) + " and " + last
                # if target != 'latex':
                # value.replace('~', ' ')

        if target not in [
            "html",
            "latex",
            "rtf",
        ]:  # Note: this will catch: target is None
            return value  # don't know what to do, so do nothing!

        if target in ["html", "rtf"]:
            # LaTeX isms to Unicode
            value = value.replace("---", "\u2014")  # em-dash
            value = value.replace("--", "\u2013")  # en-dash

        # syntax processing here, i.e., '*', '**', '{}'
        n, tree, mathmode = self.__build_parse_tree(value)
        return mark_safe(self.__render_tree(tree, target))

    def get_dictionary(self, target=None):
        """
        Get a dictionary of the BibTeX fields for this publication.
        Optionally restrict the fields.
        Additionally process values based on target.
        """
        fields = self.Type.get_field_list()
        result = {}
        for field in fields:
            if hasattr(self, field):
                value = getattr(self, field)
                if value is not None:
                    value = "{}".format(value)
                #                     if not isinstance(value, unicode):
                #                         t = type(value)
                #                         if isinstance(value, six.string_types):
                #                             value = value.decode('utf-8')
                #                         #elif isinstance(value, int):
                #                             #value = '%d' % value
                #                         else:
                #                             value = '%d' % value
                #                             #assert False    # what to do with this type!?!
                result[field] = self.proc_for_target(field, value, target)
        if self.URL:
            result["URL"] = self.URL
        result["Entry_Type"] = self.Type.Name
        result["Active"] = self.Active
        result["public"] = self.public
        return result

    def as_html(self):
        if not self.Type.html_Template:
            return mark_safe(
                '<tt class="error" style="color:red;">[!] NO TEMPLATE for publication entry type: "%s" [!]</tt>'
                % "{}".format(self.Type)
            )
        t = self.Type.get_template("html")
        d = self.get_dictionary(target="html")
        return t.render(Context(d))
        # return 'HTML for ' + str(self)

    def as_LaTeX(self, template=None):
        """
        Note that this method allows for template overrides.
        """
        if template is None:
            if not self.Type.html_Template:
                return (
                    '\\texttt{[!] NO TEMPLATE for publication entry type: "%s" [!]}'
                    % "{}".format(self.Type)
                )
            t = self.Type.get_template("latex")
        else:
            t = Template(template)
        d = self.get_dictionary(target="latex")
        return t.render(Context(d))
        # return 'LaTeX for ' + str(self)

    def as_rtf(self):
        assert False  # not implemented
        return "RTF for " + str(self)

    def as_bibtex(self, include_url=False):
        """
        Serialize this entry as a BibTeX text item.
        """
        data = {}
        fields = self.Type.get_field_list()
        for field in fields:
            if hasattr(self, field):
                value = getattr(self, field)
                if value:
                    t = type(value)
                    if isinstance(value, six.string_types):
                        value = '"%s"' % value
                    else:
                        value = "%d" % value
                    data[field] = self.proc_for_target(field, value, "latex")
        if self.URL and include_url:
            data["url"] = self.URL
        field_list = ["    %s = %s" % (key, value) for key, value in data.items()]
        field_text = ",\n".join(field_list)
        typename = self.Type.Name
        key = self.Reference_Key
        return "@" + typename + "{" + key + ",\n" + field_text + "\n}"


############################################################################
#
