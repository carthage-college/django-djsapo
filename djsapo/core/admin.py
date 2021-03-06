from django.db import models
from django.contrib import admin
from django.forms import CheckboxSelectMultiple

from djsapo.core.models import (
    Alert,Annotation,Document,GenericChoice,Member,Message,Profile
)


class GenericChoiceAdmin(admin.ModelAdmin):
    list_display = ('name','value','rank','active','admin')
    list_editable = ('active','admin')
    formfield_overrides = {
        models.ManyToManyField: {'widget': CheckboxSelectMultiple},
    }


class AlertAdmin(admin.ModelAdmin):
    list_display = ('student_name','cid','creator_name','created_at')
    search_fields = ('created_by__username','student__username')
    raw_id_fields = ('created_by','updated_by','student')

    def creator_name(self, obj):
        return "{}, {}".format(obj.created_by.last_name, obj.created_by.first_name)
    creator_name.admin_order_field  = 'created_by'
    creator_name.short_description = "Submitted by"

    def student_name(self, obj):
        return "{}, {}".format(obj.student.last_name, obj.student.first_name)
    student_name.admin_order_field  = 'student__last_name'
    student_name.short_description = "Student"

    def cid(self, obj):
        return obj.student.id
    cid.admin_order_field  = 'student_id'
    cid.short_description = "College ID"


class MemberAdmin(admin.ModelAdmin):
    list_display = ('user_name','alert','status')
    raw_id_fields = ('user','alert')
    list_editable = ('status','case_manager')
    list_editable = ('status',)

    def user_name(self, obj):
        return "{}, {}".format(obj.user.last_name, obj.user.first_name)
    user_name.admin_order_field  = 'user__last_name'
    user_name.short_description = "Member"


class AnnotationAdmin(admin.ModelAdmin):
    list_display = ('__str__','alert','creator_name','created_at','tags','status')
    raw_id_fields = ('created_by','alert')
    list_editable = ('status',)

    def creator_name(self, obj):
        return "{}, {}".format(obj.created_by.last_name,obj.created_by.first_name)
    creator_name.admin_order_field  = 'created_by'
    creator_name.short_description = "Submitted by"


class DocumentAdmin(admin.ModelAdmin):
    raw_id_fields = ('alert','created_by','updated_by')
    list_display = (
        '__str__','name','alert','creator_name','created_at','tags'
    )

    def creator_name(self, obj):
        return "{}, {}".format(obj.created_by.last_name,obj.created_by.first_name)
    creator_name.admin_order_field  = 'created_by'
    creator_name.short_description = "Submitted by"


class MessageAdmin(admin.ModelAdmin):
    list_display = ('name','slug','status')
    list_editable = ('status',)


class ProfileAdmin(admin.ModelAdmin):
    search_fields = (
        'user__username','user__last_name','user__first_name'
    )
    list_display = ('user_name','get_categories','case_manager')
    raw_id_fields = ('user',)
    list_editable = ('case_manager',)
    list_max_show_all   = 250
    list_per_page       = 250

    def user_name(self, obj):
        return "{}, {}".format(obj.user.last_name, obj.user.first_name)
    user_name.admin_order_field  = 'user__last_name'
    user_name.short_description = "Profile"

    def get_categories(self, obj):
        return "; ".join([c.name for c in obj.category.all()])
    get_categories.allow_tags = True
    get_categories.short_description = "Categories"


admin.site.register(GenericChoice, GenericChoiceAdmin)
admin.site.register(Alert, AlertAdmin)
admin.site.register(Annotation, AnnotationAdmin)
admin.site.register(Document, DocumentAdmin)
admin.site.register(Member, MemberAdmin)
admin.site.register(Message, MessageAdmin)
admin.site.register(Profile, ProfileAdmin)
