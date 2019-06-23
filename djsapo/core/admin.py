from django.contrib import admin

from djsapo.core.models import Alert, GenericChoice


class GenericChoiceAdmin(admin.ModelAdmin):
    list_display = ('name','value','rank','active','admin')


class AlertAdmin(admin.ModelAdmin):
    raw_id_fields = ('created_by','updated_by','student')


admin.site.register(GenericChoice, GenericChoiceAdmin)
admin.site.register(Alert, AlertAdmin)
