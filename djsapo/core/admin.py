from django.contrib import admin

from djsapo.core.models import Alert, GenericChoice


class GenericChoiceAdmin(admin.ModelAdmin):
    list_display = ('name','value','rank','active','admin')


admin.site.register(GenericChoice, GenericChoiceAdmin)
admin.site.register(Alert)
