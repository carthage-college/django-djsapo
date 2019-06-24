# -*- coding: utf-8 -*-
from django.conf import settings
from django.db import models, connection
from django.contrib.auth.models import Group, User
from django.core.validators import FileExtensionValidator

from djtools.utils.users import in_group
from djtools.fields import BINARY_CHOICES
from djtools.fields.helpers import upload_to_path

from taggit.managers import TaggableManager

ALLOWED_EXTENSIONS = [
    'xls','xlsx','doc','docx','pdf','txt','png','jpg','jpeg'
]

FILE_VALIDATORS = [
    FileExtensionValidator(allowed_extensions=ALLOWED_EXTENSIONS)
]

RELATIONSHIP_CHOICES = (
    ("Academic Support Services", "Academic Support Services"),
    ("Admissions", "Admissions"),
    ("Aspire", "Aspire"),
    ("Athletics", "Athletics"),
    ("Faculty", "Faculty"),
    ("Health and Counseling", "Health and Counseling"),
    ("Residential Life", "Residential Life"),
    ("Staff", "Staff"),
    ("Student", "Student"),
    ("Student Financial Planning", "Student Financial Planning"),
    ("Student Involvement", "Student Involvement"),
    ("Student Success", "Student Success"),
    ("Other", "Other"),
)

SEVERITY_CHOICES = (
    ("High", "High"),
    ("Moderate", "Moderate"),
    ("Low", "Low"),
    ("Uncertain", "Uncertain"),
)

OUTCOME_CHOICES = (
    ("No resolution required", "No resolution required"),
    ("Next steps discussed", "Next steps discussed"),
    ("Resolved", "Resolved"),
    ("Duplicate concern", "Duplicate concern"),
    ("Unresponsive", "Unresponsive"),
)
# the name/value pairs have to be on one long line otherwise the django
# forms validation does not recognize them as valid choices
INTERACTION_CHOICES = (
    (
        "I have reached out to the student and am awaiting a response.",
        "I have reached out to the student and am awaiting a response."
    ),
    (
        "I have reached out to the student several times, but was unsuccessful and/or did not get a response.",
        "I have reached out to the student several times, but was unsuccessful and/or did not get a response."
    ),
    (
        "The student has acknowledged the issue, and next steps have been discussed.",
        "The student has acknowledged the issue, and next steps have been discussed."
    ),
    (
        "I have communicated my concern to the student, but they did not agree it was an issue.",
        "I have communicated my concern to the student, but they did not agree it was an issue."
    ),
    ("Other", "Other")
)

def limit_category():
    ids = [
        g.id for g in GenericChoice.objects.filter(
            tags__name__in=['Category']
        ).order_by('name')
    ]
    return {'id__in':ids}

def limit_action():
    ids = [
        g.id for g in GenericChoice.objects.filter(
            tags__name__in=['Action Taken']
        ).order_by('name')
    ]
    return {'id__in':ids}


class GenericChoice(models.Model):
    """
    Choices for model and form fields that accept for multiple values
    """
    name = models.CharField(
        max_length=255
    )
    value = models.CharField(
        unique=True, max_length=255
    )
    rank = models.IntegerField(
        verbose_name="Ranking",
        null=True, blank=True, default=0,
        help_text="""
            A number that determines this object's position in a list.
        """
    )
    active = models.BooleanField(
        help_text="""
            Do you want the field to be visable on your form?
        """,
        verbose_name="Is active?", default=True
    )
    admin = models.BooleanField(
        verbose_name="Administrative only", default=False
    )
    group = models.ManyToManyField(Group, null=True, blank=True)
    tags = TaggableManager()

    class Meta:
        ordering = ['rank']

    def __str__(self):
        """
        Default data for display
        """
        return self.name


class Profile(models.Model):
    user = models.OneToOneField(
        User, on_delete=models.PROTECT,
    )
    category = models.ManyToManyField(
        GenericChoice, verbose_name="Type of Concern",
        limit_choices_to=limit_category,
        help_text = "Check all that apply"
    )

    def __str__(self):
        return "{}, {}".format(
            self.user.last_name, self.user.first_name
        )


class Alert(models.Model):
    """
    Data model for the early alert object
    """
    parent = models.ForeignKey(
        'self', related_name='children',
        on_delete=models.PROTECT, null=True,blank=True,
    )
    # Alert.objects.get(pk=1).children.all()
    # alert2.parent = alert1, and then alert1.children.all() will include alert2
    created_at = models.DateTimeField(
        "Date Created", auto_now_add=True
    )
    updated_at = models.DateTimeField(
        "Date Updated", auto_now=True
    )
    created_by = models.ForeignKey(
        User, verbose_name="Created by",
        on_delete=models.CASCADE, editable=False
    )
    updated_by = models.ForeignKey(
        User, verbose_name="Updated by", related_name='updated_by',
        on_delete=models.CASCADE, editable=False, null=True, blank=True
    )
    student = models.ForeignKey(
        User, verbose_name="Student", related_name='student',
        on_delete=models.PROTECT
    )
    # we will store something like 2019_RA_CSC_1100_01
    course = models.CharField(
        "Course number", max_length=64, null=True,blank=True,
        help_text = """
        If this is related to a specific course please include
        the course number.
        """
    )
    relationship = models.CharField(
        "Relationship to student", max_length=24, choices=RELATIONSHIP_CHOICES,
    )
    category = models.ManyToManyField(
        GenericChoice, verbose_name="Type of Concern",
        related_name="concern_type",
        limit_choices_to=limit_category,
        help_text="Check all that apply"
    )
    # category:
    # e.g. academic, attendance, low grades, financial, athletics, mental health
    # other categories (types) will be available to administrators
    # after the submission)
    severity = models.CharField(
        "Severity", max_length=24, choices=SEVERITY_CHOICES,
    )
    description = models.TextField(
        "Details about this concern", null=True,blank=True,
        help_text = """
            Please share any additional information you have about this concern
            that can help us in our efforts to connect with the student and
            resolve their issue.
        """,
    )
    action_taken = models.ManyToManyField(
        GenericChoice, verbose_name="Action taken",
        limit_choices_to=limit_action,
        help_text="Check all that apply"
    )
    interaction = models.CharField(
        "Have you interacted with the student regarding this concern?",
        max_length=4, choices=BINARY_CHOICES
    )
    interaction_date = models.DateField(
        "Date of the interaction",
        null=True,blank=True,
        help_text="mm/dd/yyyy"
    )
    interaction_time = models.TimeField(
        "Time of interaction",
        null=True,blank=True,
        help_text="(Format HH:MM am/pm)"
    )
    interaction_type = models.CharField(
        "How did you interact with this student?",
        max_length=128, choices=INTERACTION_CHOICES,
        null=True,blank=True,
    )
    interaction_details = models.TextField(
        "Interaction datails",
        help_text = """
            Please share any additional information about your interaction
            with the student.
        """,
        null=True,blank=True,
    )
    outcome = models.CharField(
        "Outcome", max_length=128, choices=OUTCOME_CHOICES,
    )

    class Meta:
        ordering  = ['-created_at']
        get_latest_by = 'created_at'

    def __str__(self):
        """
        Default data for display
        """
        return "{}, {}".format(
            self.student.last_name, self.student.first_name
        )

    def get_absolute_url(self):
        return ('alert_detail', [str(self.id)])

    def permissions(self, user):
        # we can move this to core.utils if we use it else where
        if user.is_superuser:
            perms = {'view':True,'update':True,'delete':True}
        else:
            perms = {'view':False,'update':False,'delete':False}
            group = in_group(user, settings.CSS_GROUP)
            if self.created_by == user or group:
                perms['view'] = True
                perms['update'] = True

        return perms


class Member(models.Model):
    """
    Alert team member
    """
    user = models.ForeignKey(
        User, verbose_name="Team member", on_delete=models.CASCADE
    )
    alert = models.ForeignKey(
        Alert, related_name='team', on_delete=models.CASCADE
    )
    status = models.BooleanField(default=False, verbose_name="Active?")
    case_manager = models.BooleanField(default=False)

    class Meta:
        # the team should not contain a member more than once for an alert
        unique_together = ['user', 'alert']

    def __str__(self):
        """
        Default data for display
        """
        return "{}, {}".format(
            self.user.last_name, self.user.first_name
        )


class Annotation(models.Model):

    alert = models.ForeignKey(
        Alert, related_name='notes', on_delete=models.PROTECT
    )
    created_by = models.ForeignKey(
        User, verbose_name="Created by",
        related_name='note_creator',
        on_delete=models.PROTECT, editable=False
    )
    created_at = models.DateTimeField(
        "Date Created", auto_now_add=True
    )
    body = models.TextField()
    status = models.BooleanField(default=False, verbose_name="Active?")
    tags = TaggableManager()

    def __str__(self):
        """
        Default data for display
        """
        return "{}, {}".format(
            self.created_by.last_name, self.created_by.first_name
        )


class Document(models.Model):
    """
    supporting documents
    """
    created_by = models.ForeignKey(
        User, verbose_name="Created by",
        related_name='doc_creator',
        on_delete=models.CASCADE, editable=False
    )
    created_at = models.DateTimeField(
        "Date Created", auto_now_add=True
    )
    alert = models.ForeignKey(
        Alert, editable=False,
        related_name='documents', on_delete=models.CASCADE
    )
    name = models.CharField(
        "Name or short description of the file",
        max_length=128, null=True,blank=True
    )
    phile = models.FileField(
        "Supporting Document",
        upload_to=upload_to_path,
        validators=FILE_VALIDATORS,
        max_length=767, null=True,blank=True,
        help_text="PDF Format Only",
    )
    tags = TaggableManager(blank=True)

    class Meta:
        ordering  = ['-created_at']
        get_latest_by = 'created_at'

    def get_slug(self):
        return 'alert-document'

    def __str__(self):
        """
        Default data for display
        """
        return "{}: {}".format(self.name, self.alert)


class Message(models.Model):
    """
    automated message content sent from the system]
    """
    name = models.CharField(
        max_length=255,
    )
    # in admin: prepopulated_fields = {"slug": ("name",)}
    slug = models.SlugField(
        max_length=255, unique=True
    )
    body = models.TextField(
        help_text="Message content in text/html"
    )
    status = models.BooleanField(default=False, verbose_name="Active?")


"""
Solutions:

27: for course, instead of fetching the student's courses, we
display a field that autocompletes based on all courses for the Term.
that is, the submitter starts to type CSC and all computer science
courses will appear as a select field from which they can choose the
relevant course.
"""
