from django.contrib import admin

from djsapo.core.models import Alert,Annotation,Document,GenericChoice,Member,Message


class GenericChoiceAdmin(admin.ModelAdmin):
    list_display = ('name','value','rank','active','admin')


class AlertAdmin(admin.ModelAdmin):
    list_display = ('__unicode__','cid','creator_name')
    search_fields = ('created_by__username','student__username')
    raw_id_fields = ('created_by','updated_by','student')

    def creator_name(self, obj):
        return "{}, {}".format(obj.created_by.last_name,obj.created_by.first_name)
    creator_name.admin_order_field  = 'created_by'
    creator_name.short_description = "Submitted by"

    def cid(self, obj):
        return obj.student.id
    cid.admin_order_field  = 'student_id'
    cid.short_description = "College ID"


class MemberAdmin(admin.ModelAdmin):
    list_display = ('__unicode__','alert','case_manager','status')
    raw_id_fields = ('user','alert')


class AnnotationAdmin(admin.ModelAdmin):
    list_display = ('__unicode__','alert','creator_name','created_at','tags','status')
    raw_id_fields = ('created_by','alert')

    def creator_name(self, obj):
        return "{}, {}".format(obj.created_by.last_name,obj.created_by.first_name)
    creator_name.admin_order_field  = 'created_by'
    creator_name.short_description = "Submitted by"


class DocumentAdmin(admin.ModelAdmin):
    list_display = (
        '__unicode__','name','alert','creator_name','created_at','tags'
    )
    raw_id_fields = ('created_by','alert')

    def creator_name(self, obj):
        return "{}, {}".format(obj.created_by.last_name,obj.created_by.first_name)
    creator_name.admin_order_field  = 'created_by'
    creator_name.short_description = "Submitted by"


class MessageAdmin(admin.ModelAdmin):
    list_display = ('name','slug','status')


admin.site.register(GenericChoice, GenericChoiceAdmin)
admin.site.register(Alert, AlertAdmin)
admin.site.register(Annotation, AnnotationAdmin)
admin.site.register(Document, DocumentAdmin)
admin.site.register(Member, MemberAdmin)
admin.site.register(Message, MessageAdmin)
