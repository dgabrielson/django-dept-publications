"""
Forms for the publications app.
"""
#######################
from __future__ import print_function, unicode_literals

#######################
from collections import OrderedDict

from django import forms
from django.conf import settings
from django.forms import widgets
from django.utils.html import escape
from django.utils.safestring import mark_safe
from people.models import Person

from .models import HELP_TEXT, Entry_Type, Publication

# NOTE: The generated javascript defies the regular expectation:
#   when an Entry_Type is changed, the errors don't go away
#   which is the expected behaviour when trying to correct
#   your mistakes.
#   Error messages (id="errors-field-name") should be hidden
#   on actual changes (but not form loads)


class Entry_Type_Choice(forms.ModelChoiceField):
    def __init__(self):
        forms.ModelChoiceField.__init__(
            self,
            Entry_Type.objects.filter(Active=True),
            help_text=HELP_TEXT["Type"],
            widget=widgets.Select(attrs={"onChange": "onTypeChange();"}),
        )


class PublicationForm(forms.Form):
    """
    The main publication form.
    """

    SIZE_LONG = 43
    SIZE_TEXTAREA = SIZE_LONG * 7 / 8
    # SIZE_VERYLONG = '50'
    Entry_Type = Entry_Type_Choice()

    # BibTeX fields:
    #   which of these get displayed depends on the Entry_Type!
    title = forms.CharField(
        required=False,
        widget=widgets.TextInput(attrs={"size": SIZE_LONG}),
        help_text=HELP_TEXT["title"],
    )
    author = forms.CharField(
        required=False,
        widget=widgets.TextInput(attrs={"size": SIZE_LONG}),
        help_text=HELP_TEXT["author"],
    )
    year = forms.CharField(required=False, help_text=HELP_TEXT["year"])
    month = forms.CharField(required=False, help_text=HELP_TEXT["month"])
    journal = forms.CharField(
        required=False,
        widget=widgets.TextInput(attrs={"size": SIZE_LONG}),
        help_text=HELP_TEXT["journal"],
    )
    booktitle = forms.CharField(
        required=False,
        widget=widgets.TextInput(attrs={"size": SIZE_LONG}),
        help_text=HELP_TEXT["booktitle"],
    )
    school = forms.CharField(
        required=False,
        widget=widgets.TextInput(attrs={"size": SIZE_LONG}),
        help_text=HELP_TEXT["school"],
    )
    editor = forms.CharField(
        required=False,
        widget=widgets.TextInput(attrs={"size": SIZE_LONG}),
        help_text=HELP_TEXT["editor"],
    )
    publisher = forms.CharField(
        required=False,
        widget=widgets.TextInput(attrs={"size": SIZE_LONG}),
        help_text=HELP_TEXT["publisher"],
    )
    pages = forms.CharField(required=False, help_text=HELP_TEXT["pages"])
    chapter = forms.CharField(required=False, help_text=HELP_TEXT["chapter"])
    institution = forms.CharField(
        required=False,
        widget=widgets.TextInput(attrs={"size": SIZE_LONG}),
        help_text=HELP_TEXT["institution"],
    )
    address = forms.CharField(
        required=False,
        widget=widgets.Textarea(attrs={"rows": 3, "cols": SIZE_TEXTAREA}),
        help_text=HELP_TEXT["address"],
    )  # text
    organization = forms.CharField(
        required=False,
        widget=widgets.TextInput(attrs={"size": SIZE_LONG}),
        help_text=HELP_TEXT["organization"],
    )
    edition = forms.CharField(required=False, help_text=HELP_TEXT["edition"])
    series = forms.CharField(
        required=False,
        widget=widgets.TextInput(attrs={"size": SIZE_LONG}),
        help_text=HELP_TEXT["series"],
    )
    volume = forms.CharField(required=False, help_text=HELP_TEXT["volume"])
    number = forms.CharField(required=False, help_text=HELP_TEXT["number"])
    howpublished = forms.CharField(required=False, help_text=HELP_TEXT["howpublished"])
    type = forms.CharField(required=False, help_text=HELP_TEXT["type"])
    note = forms.CharField(
        required=False,
        widget=widgets.Textarea(attrs={"rows": 3, "cols": SIZE_TEXTAREA}),
        help_text=HELP_TEXT["note"],
    )  # text
    key = forms.CharField(required=False, help_text=HELP_TEXT["key"])

    URL = forms.URLField(
        required=False,
        help_text=HELP_TEXT["URL"],
        widget=widgets.TextInput(attrs={"size": SIZE_LONG}),
    )
    # optional link to the Item

    Active = forms.BooleanField(required=False, help_text=HELP_TEXT["Active"])
    public = forms.BooleanField(required=False, help_text=HELP_TEXT["public"])

    initial_hide_list = [
        "address",
        "author",
        "booktitle",
        "chapter",
        "edition",
        "editor",
        "howpublished",
        "institution",
        "journal",
        "key",
        "month",
        "note",
        "number",
        "organization",
        "pages",
        "publisher",
        "school",
        "series",
        "title",
        "type",
        "volume",
        "year",
        "URL",
        "Active",
        "public",
    ]

    class Media:
        """
        Use {{ form.media }} in templates to include this.
        """

        css = {"all": ("css/forms.css",)}

    class clean_bibtex_field:
        def __init__(self, name, form, is_uint=False):
            self.name = name
            self.form = form
            self.is_uint = is_uint

        def __call__(self):
            if self.form.entry_type is None:
                try:
                    self.form.clean_Entry_Type()
                except forms.ValidationError:
                    return self.form.data[self.name]  # don't make noisy errors
            if self.form.entry_type.is_required(self.name):
                if not self.form.data[self.name]:
                    raise forms.ValidationError(
                        "This is a required field for this entry type."
                    )
                if self.is_uint:
                    try:
                        n = int(self.form.data[self.name])
                        if n < 0:
                            raise forms.ValidationError(
                                "This should be a non-negative integer."
                            )
                        return n
                    except ValueError:
                        raise forms.ValidationError(
                            "This should be a non-negative integer."
                        )

            return self.form.data[self.name]

    def __init__(self, data=None, initial=None):
        if initial is None:
            initial = {}
        forms.Form.__init__(self, data=data, initial=initial)
        self.entry_type = None

        for field in self.initial_hide_list:
            if field in ["Active", "public"]:
                pass  # do nothing
            elif field in ["chapter", "volume", "year"]:
                cleaner = self.clean_bibtex_field(field, self, True)
            else:
                cleaner = self.clean_bibtex_field(field, self)
            setattr(self, "clean_%s" % field, cleaner)

    def clean_Entry_Type(self):
        name = self.data["Entry_Type"]
        try:
            self.entry_type = Entry_Type.objects.get(Active=True, Name=name)
        except Entry_Type.DoesNotExist:
            self.entry_type = None
            raise forms.ValidationError("This is an invalid entry type.")

        return self.data["Entry_Type"]

    def clean(self, *args, **kwargs):
        # check for OR required conditionals:
        return super(self.__class__, self).clean(*args, **kwargs)

    def for_model(self):
        boolean_fields = ("Active", "public")
        # assumptions: is_valid() has been called and is True
        assert self.is_valid()
        data = {"Type": self.entry_type}
        data.update(self.cleaned_data)
        del data["Entry_Type"]
        keys = data.keys()
        for k in keys:
            if (k not in boolean_fields) and (not data[k]):
                # del data[k]# this seems like a good idea, but does
                # not allow for blanking values!
                data[k] = None
        for b in boolean_fields:
            data[b] = (b in self.data) and bool(self.data[b])
        return data

    def javascript(self):
        result = ""
        result += """function set_row_display(name, show)
{
    var elem_input = document.getElementById('id_' + name);
    var elem = elem_input.parentNode.parentNode;
    if (elem)
    {
        if (show)
        {
            elem.style.display = '';
        }
        else
        {
            elem.style.display = 'none';
        }
    }
}

"""
        result += "function set_help_text(name, text)\n{\n"
        result += "    var obj = document.getElementById('help-text-' + name);\n"
        result += "    if (obj) {\n"
        result += "        obj.innerHTML = text;\n"
        result += "    }\n"
        result += "}\n\n"

        result += "function hideAll()\n{\n"
        result += "\n".join(
            ["    set_row_display('%s', false);" % e for e in self.initial_hide_list]
        )
        result += "\n"
        result += "}\n\n"

        result += "function onTypeChange()\n{\n"
        result += "    set_help_text('Entry_Type', '%s');\n" % escape(HELP_TEXT["Type"])
        result += "    hideAll();\n"
        result += """    var type_selector = document.getElementById('id_Entry_Type');
    type_selector_index = type_selector.selectedIndex;
    type_id = -1;
    for (var i = 0; i < type_selector.options.length; i++) {
        if (type_selector.options[i].selected == true) {
            type_id = type_selector.options[i].value;
            break
        }
    }
"""
        # note: the "type_id" is the primary_key (a slug), to the Entry_Type object.
        for et in Entry_Type.objects.filter(Active=True):
            result += "    if (type_id == '%s') {\n" % et.Name
            result += "        set_help_text('%s', '%s');\n" % (
                "Entry_Type",
                escape(et.Description),
            )
            for field in et.get_optional_field_list():
                result += "        set_row_display('%s', true);\n" % field
                result += "        set_help_text('%s', '%s');\n" % (
                    field,
                    "(Optional) " + HELP_TEXT[field],
                )
            for field in et.get_required_field_list():
                result += "        set_row_display('%s', true);\n" % field
                result += "        set_help_text('%s', '%s');\n" % (
                    field,
                    "(Required) " + HELP_TEXT[field],
                )
            for name in ["URL", "Active", "public"]:
                result += "        set_row_display('%s', true);\n" % name
            result += "    }\n"
        result += "\n}\n\n"

        result += "function publicationsOnLoad()\n{\n"
        result += "    hideAll();\n"
        result += "    onTypeChange();\n"
        result += "}\n\n"
        return mark_safe(result)


class BibtexUploadForm(forms.Form):
    """
    Handle BibTeX file uploads.

    Note that file transfers require
    <form enctype="multipart/form-data"  ... >
    """

    file = forms.FileField(label="BibTeX File")
    overwrite = forms.BooleanField(
        label="Overwrite entries",
        required=False,
        initial=True,
        help_text="Select this to resave entries with the same key as the key used in the BibTeX file",
    )

    class Media:
        """
        Use {{ form.media }} in templates to include this.
        """

        css = {"all": ("css/forms.css",)}

    def __init__(self, *args, **kwargs):
        """
        Initialize the form
        """
        owner = kwargs.pop("owner", None)
        is_superuser = kwargs.pop("is_superuser", False)
        result = super(self.__class__, self).__init__(*args, **kwargs)
        self.owner = owner
        self.initial["owner"] = owner
        if self.owner is not None and is_superuser:
            # inject an owner select widget.  Otherwise, *this* user
            # will be the owner.
            f = forms.ModelChoiceField(
                Person.objects.filter(active=True, flags__slug="publications")
            )
            fields = OrderedDict([("owner", f)])
            for f in self.fields:
                fields[f] = self.fields[f]
            self.fields = fields
        return result

    def save_bibtex(self, owner):
        """
        Worker function for actually processing the BibTeX file.

        Returns True if successful and False if the processing fails.
        """

        def error(message):
            """set the error message and return False
            """
            self._errors[forms.forms.NON_FIELD_ERRORS] = self.error_class([message])
            return False

        def _safe_int_uniq(v):
            try:
                v = int(v)
            except ValueError:
                v = 0
            return v

        overwrite = "overwrite" in self.data

        pub_list = Publication.objects.load_from_bibtex(self.files["file"].read())
        if not pub_list:
            return error("No entries found.  Is this a BibTeX file?")

        for pub in pub_list:
            refkey = pub.Reference_Key
            try:
                original = Publication.objects.get(Reference_Key=refkey, Owner=owner)
            except Publication.DoesNotExist:
                # no prior publication with this key for this owner.
                pub.Owner = owner
                pub.save()
            else:
                # original exists; overwrite values?
                if overwrite:
                    values = pub.__dict__
                    for key in values:
                        if key != "id":
                            setattr(original, key, values[key])
                    original.Owner = owner
                    original.save()

        return True


#
