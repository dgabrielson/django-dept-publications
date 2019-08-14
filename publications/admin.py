from django.contrib import admin
from publications.models import Entry_Type, Publication

##################################################################


class Entry_TypeOptions(admin.ModelAdmin):
    list_display = ["Name", "Description", "Required_Fields", "Optional_Fields"]
    # list_filter = ['Active', 'Account_Created', 'Sections', ]
    search_fields = ["Name", "Description"]
    ordering = ["Name"]


admin.site.register(Entry_Type, Entry_TypeOptions)

##################################################################


class PublicationOptions(admin.ModelAdmin):
    list_display = ["Reference_Key", "Owner", "Type", "title", "URL"]
    list_filter = ["Owner", "Type"]
    search_fields = ["Reference_Key", "Owner__cn", "Type__Name", "title", "journal"]
    ordering = ["key", "author", "editor"]

    def get_queryset(self, request):
        """
        This function restricts the default queryset in the
        admin list view.
        """
        # If super-user, show all
        if request.user.is_superuser:
            return Publication.objects.all()
        # else restrict!
        return Publication.objects.filter(Owner__username=request.user.username)


admin.site.register(Publication, PublicationOptions)

##################################################################
