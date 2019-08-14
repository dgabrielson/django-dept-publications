"""
Views for the publications app.

Much of this is really, really dated (& written when I was new to
Django as well), and should be rewritten.
"""
import datetime

from django.http import Http404, HttpResponse, HttpResponseRedirect
from django.shortcuts import get_object_or_404, render
from django.template import RequestContext
from django.urls import reverse
from django.views.generic.edit import DeleteView, FormView
from django.views.generic.list import ListView
from people.models import Person
from uofm import auth

from . import conf
from .forms import BibtexUploadForm, PublicationForm
from .models import Publication


def publication_auth_test(user):
    """
    This is the test to see if someone is authorized to add/edit publications
    (It does *not* check ownership.)
    """
    if user.is_superuser:
        return True
    if not user.is_active:
        return False
    try:
        person = Person.objects.get_by_user(user, active=True)
    except Person.DoesNotExist:
        return False
    else:
        return person.flags.filter(slug="publications").count() != 0


publication_auth = auth.user_passes_test_with_403(
    publication_auth_test, test_fail_msg="You do not have access to publications"
)


class PublicationForPersonListView(ListView):
    """
    Pulls a publication list for a particular owner, but viewable by all.
    """

    def get_queryset(self, *args, **kwargs):
        """
        get the queryset.

        Non-active publications are shown and marked to their owner (only).
        """
        slug = self.kwargs["slug"]
        # show non-active publications to the owner when logged in.
        try:
            owner = Person.objects.get(active=True, slug=slug)
        except Person.DoesNotExist:
            raise Http404
        if not owner.active:
            raise Http404
        self.person = owner

        show_all = owner.username == self.request.user.username

        qs = (
            Publication.objects.filter(Owner=owner)
            .most_recent_order_with_key()
            .select_related("Type", "Owner")
        )
        if not show_all:
            qs = qs.active()
        return qs

    def get_context_data(self, **kwargs):
        """
        Call the base implementation first to get a context
        """
        context = super().get_context_data(**kwargs)
        # Add in local context
        context["person"] = self.person  # fetched during get_queryset()
        return context


list_for_person = PublicationForPersonListView.as_view()
bibtex_for_person = PublicationForPersonListView.as_view(
    template_name="publications/bibtex_list.html"
)


class PublicationListView(ListView):
    """
    Pulls all publications, but restricts to the last few years.
    """

    def since_year(self):
        this_year = datetime.date.today().year
        return this_year - conf.get("recent_years")

    def get_queryset(self, *args, **kwargs):
        return (
            Publication.objects.active()
            .filter(Owner__active=True, year__gte=self.since_year())
            .most_recent_order()
            .public()
            .select_related("Type", "Owner")
        )

    def get_context_data(self, **kwargs):
        """
        Call the base implementation first to get a context
        """
        context = super().get_context_data(**kwargs)
        # Add in local context
        context["since_year"] = self.since_year()
        return context

    ###


list_for_all = PublicationListView.as_view()

list_people_with_pubs = ListView.as_view(
    queryset=Person.objects.filter(
        active=True, slug__isnull=False, flags__slug="publications"
    ),
    template_name="publications/person_list.html",
)


@publication_auth
def add(request):
    """
    Add a new publication
    """
    person = Person.objects.get_by_user(request.user)

    if request.method == "POST":  # form submission
        form = PublicationForm(request.POST)
        if form.is_valid():
            # make model
            pub = Publication(**form.for_model())
            pub.Owner = person
            pub.save()
            return HttpResponseRedirect(
                reverse("publications-personal-list", kwargs={"slug": person.slug})
            )
        else:
            try:
                form_errors = form.errors["__all__"]
            except KeyError:
                pass
    else:
        form = PublicationForm()

    return render(
        request, "publications/add.html", locals()
    )  # warning: template does not exist!


@publication_auth
def update(request, refkey):
    """
    Update the given publication
    """
    person = Person.objects.get_by_user(request.user)
    update_pub = get_object_or_404(Publication, Reference_Key=refkey, Owner=person)

    if request.method == "POST":  # form submission
        form = PublicationForm(request.POST)
        if form.is_valid():
            # make model
            updated_data = form.for_model()
            for (
                key,
                value,
            ) in updated_data.items():  # warning: only returns things with values!
                setattr(update_pub, key, value)
            update_pub.save()
            # assert False, 'after save'
            # update_msg = "Your changes have been saved."
            # return HttpResponseRedirect( reverse('publications.views.update', args=[update_pub.Reference_Key, ]) )    # add another
            return HttpResponseRedirect(
                reverse("publications-personal-list", kwargs={"slug": person.slug})
            )
        else:
            try:
                form_errors = form.errors["__all__"]
            except KeyError:
                pass
    else:
        form = PublicationForm(initial=update_pub.get_dictionary())

    object = update_pub
    publication = update_pub

    return render(
        request, "publications/update.html", locals()
    )  # warning: template does not exist!


class PublicationDeleteView(DeleteView):
    def get_person(self):
        if not hasattr(self, "person"):
            self.person = Person.objects.get_by_user(self.request.user)
        return self.person

    def get_object(self, *args, **kwargs):

        return get_object_or_404(
            Publication,
            Reference_Key=self.kwargs.get("refkey", None),
            Owner=self.get_person(),
        )

    def get_context_data(self, **kwargs):
        """
        Call the base implementation first to get a context
        """
        context = super().get_context_data(**kwargs)
        # Add in local context
        context["person"] = self.get_person()
        return context

    def get_success_url(self):
        return reverse(
            "publications-personal-list", kwargs={"slug": self.get_person().slug}
        )


delete_view = publication_auth(PublicationDeleteView.as_view())


class BibtexUploadFormView(FormView):
    """
    Class for processing BibTeX uploads.
    """

    form_class = BibtexUploadForm
    template_name = "publications/bibtex_upload.html"

    def get_person(self):
        try:
            return Person.objects.get_by_user(self.request.user)
        except Person.DoesNotExist:
            raise Http404("person does not exist")

    def get_form_kwargs(self, *args, **kwargs):
        """
        Returns the keyword arguments for instanciating the form.
        """
        # initialize defaults
        kwargs = super(BibtexUploadFormView, self).get_form_kwargs(*args, **kwargs)
        # special kwargs for this form class
        kwargs["owner"] = self.get_person()
        kwargs["is_superuser"] = self.request.user.is_superuser
        return kwargs

    def get_success_url(self):
        """
        Called when everything works properly.
        Redirect to a personal list, if one exists.
        """
        person = self.get_person()
        # try:
        #     person = Person.objects.get_by_user(self.request.user)
        # except Person.DoesNotExist:
        #     url = reverse('publications-main')
        # else:
        if person.slug:
            url = reverse("publications-personal-list", kwargs={"slug": person.slug})
        else:
            url = reverse("publications-main")
        return url

    def form_valid(self, form):
        """
        Called when the form is valid: Do an action.
        """
        if form.save_bibtex(self.get_person()):
            return super(BibtexUploadFormView, self).form_valid(form)
        else:
            return super(BibtexUploadFormView, self).form_invalid(form)

    def get_context_data(self, **kwargs):
        """
        Call the base implementation first to get a context
        """
        context = super().get_context_data(**kwargs)
        # Add in local context
        context["person"] = self.get_person()
        return context


bibtex_upload = publication_auth(BibtexUploadFormView.as_view())


class BibtexUploadForPersonFormView(BibtexUploadFormView):
    """
    Like above, but the person is identified by a url slug.
    """

    def get_person(self):
        slug = self.kwargs.get("slug", None)
        if slug is None:
            raise Http404("No person to find")
        return get_object_or_404(Person, active=True, slug=slug)


#

bibtex_upload_for_person = publication_auth(BibtexUploadForPersonFormView.as_view())
