# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [("people", "0001_initial")]

    operations = [
        migrations.CreateModel(
            name="Entry_Type",
            fields=[
                ("Active", models.BooleanField(default=True)),
                ("Last_Updated", models.DateTimeField(auto_now=True)),
                ("Name", models.SlugField(serialize=False, primary_key=True)),
                ("Description", models.CharField(max_length=512)),
                ("Required_Fields", models.CharField(max_length=512)),
                ("Optional_Fields", models.CharField(max_length=512)),
                ("html_Template", models.TextField(null=True, blank=True)),
                ("latex_Template", models.TextField(null=True, blank=True)),
                ("rtf_Template", models.TextField(null=True, blank=True)),
            ],
            options={"ordering": ["Name"], "verbose_name": "Entry Type"},
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name="Publication",
            fields=[
                (
                    "Active",
                    models.BooleanField(
                        default=True,
                        help_text="If this is not set, the publication will not appear anywhere.",
                    ),
                ),
                (
                    "public",
                    models.BooleanField(
                        default=True, help_text="Show this publication in the main list"
                    ),
                ),
                ("Last_Updated", models.DateTimeField(auto_now=True)),
                ("Reference_Key", models.SlugField(serialize=False, primary_key=True)),
                (
                    "URL",
                    models.URLField(
                        help_text="(Optional) A link to an online version or further information",
                        null=True,
                        verbose_name=b"URL",
                        blank=True,
                    ),
                ),
                (
                    "address",
                    models.TextField(
                        help_text="Publisher&#39;s address (usually just the city, but can be the full address for lesser-known publishers)",
                        null=True,
                        blank=True,
                    ),
                ),
                (
                    "author",
                    models.CharField(
                        help_text="The name(s) of the author(s) (in the case of more than one author, separated by &quot;and&quot;, very long lists can be truncated with &quot;and others&quot;), in the format &quot;Familyname, G.&quot; or &quot;Familyname, Given&quot;",
                        max_length=256,
                        null=True,
                        blank=True,
                    ),
                ),
                (
                    "booktitle",
                    models.CharField(
                        help_text="The title of the book, if only part of it is being cited",
                        max_length=256,
                        null=True,
                        blank=True,
                    ),
                ),
                (
                    "chapter",
                    models.PositiveIntegerField(
                        help_text="The chapter number", null=True, blank=True
                    ),
                ),
                (
                    "edition",
                    models.CharField(
                        help_text="The edition of a book, long form (such as &quot;first&quot; or &quot;second&quot;)",
                        max_length=64,
                        null=True,
                        blank=True,
                    ),
                ),
                (
                    "editor",
                    models.CharField(
                        help_text="The name(s) of the editor(s)",
                        max_length=256,
                        null=True,
                        blank=True,
                    ),
                ),
                (
                    "howpublished",
                    models.CharField(
                        help_text="How it was published, if the publishing method is nonstandard",
                        max_length=256,
                        null=True,
                        blank=True,
                    ),
                ),
                (
                    "institution",
                    models.CharField(
                        help_text="The institution that was involved in the publishing, but not necessarily the publisher",
                        max_length=256,
                        null=True,
                        blank=True,
                    ),
                ),
                (
                    "journal",
                    models.CharField(
                        help_text="The journal or magazine the work was published in",
                        max_length=256,
                        null=True,
                        blank=True,
                    ),
                ),
                (
                    "key",
                    models.CharField(
                        help_text="A hidden field used for specifying or overriding the alphabetical order of entries (when the &quot;author&quot; and &quot;editor&quot; fields are missing). Note that this is very different from the Reference_Key that is used to cite or cross-reference the entry.",
                        max_length=256,
                        null=True,
                        blank=True,
                    ),
                ),
                (
                    "month",
                    models.CharField(
                        help_text="The month of publication (or, if unpublished, the month of creation)",
                        max_length=32,
                        null=True,
                        blank=True,
                    ),
                ),
                (
                    "note",
                    models.TextField(
                        help_text="Miscellaneous extra information",
                        null=True,
                        blank=True,
                    ),
                ),
                (
                    "number",
                    models.CharField(
                        help_text="The &quot;number&quot; of a journal, magazine, or tech-report, if applicable. (Most publications have a &quot;volume&quot;, but no &quot;number&quot; field.)",
                        max_length=32,
                        null=True,
                        blank=True,
                    ),
                ),
                (
                    "organization",
                    models.CharField(
                        help_text="The conference sponsor",
                        max_length=256,
                        null=True,
                        blank=True,
                    ),
                ),
                (
                    "pages",
                    models.CharField(
                        help_text="Page numbers, separated either by commas or double-hyphens. For books, the total number of pages.",
                        max_length=64,
                        null=True,
                        blank=True,
                    ),
                ),
                (
                    "publisher",
                    models.CharField(
                        help_text="The publisher&#39;s name",
                        max_length=256,
                        null=True,
                        blank=True,
                    ),
                ),
                (
                    "school",
                    models.CharField(
                        help_text="The school where the thesis was written",
                        max_length=256,
                        null=True,
                        blank=True,
                    ),
                ),
                (
                    "series",
                    models.CharField(
                        help_text="The series of books the book was published in (e.g. &quot;The Hardy Boys&quot; or &quot;Lecture Notes in Computer Science&quot;)",
                        max_length=256,
                        null=True,
                        blank=True,
                    ),
                ),
                (
                    "title",
                    models.CharField(
                        help_text="The title of the work.  Use *asterisks* for italics and unicode for symbols.",
                        max_length=512,
                        null=True,
                        blank=True,
                    ),
                ),
                (
                    "type",
                    models.CharField(
                        help_text="The type of tech-report, for example, &quot;Research Note&quot;",
                        max_length=256,
                        null=True,
                        blank=True,
                    ),
                ),
                (
                    "volume",
                    models.PositiveIntegerField(
                        help_text="The volume of a journal or multi-volume book",
                        null=True,
                        blank=True,
                    ),
                ),
                (
                    "year",
                    models.PositiveIntegerField(
                        help_text="The year of publication (or, if unpublished, the year of creation)",
                        null=True,
                        blank=True,
                    ),
                ),
                (
                    "Owner",
                    models.ForeignKey(
                        on_delete=models.deletion.CASCADE,
                        help_text=b'Only people with the "publications" flag are shown',
                        to="people.Person",
                    ),
                ),
                (
                    "Type",
                    models.ForeignKey(
                        on_delete=models.deletion.CASCADE,
                        help_text="Begin by selecting the type of publication",
                        to="publications.Entry_Type",
                    ),
                ),
            ],
            options={"ordering": ["-year", "author", "title"]},
            bases=(models.Model,),
        ),
    ]
