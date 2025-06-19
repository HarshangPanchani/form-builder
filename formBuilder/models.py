from email.policy import default
from enum import unique
from tabnanny import verbose
from django.db import models
from django.utils.translation import gettext_lazy as _
from jsonfield.fields import JSONField
from multiselectfield import MultiSelectField
from applicationModule.models import allowed_group_choice, Application

# Create your models here.
class JsonSchema(models.Model):
    app_name = models.ForeignKey(Application,on_delete=models.CASCADE,null=True) 
    schema_name = models.CharField(max_length=50,null=True,verbose_name=_("Name"))
    schema = JSONField(verbose_name=_('Json Schema'))
    db_ref = JSONField(verbose_name=_('Database Reference'))
    formScript = models.TextField(verbose_name=_('Script'),null=True)

    class Meta:
        unique_together = ('schema_name', 'app_name')

    def __str__(self):
        return str(self.schema_name)

STATUS_CHOICES = [
    ('active', _("Active")),
    ('draft', _("Draft")),
    ('disabled', _("Disabled")),
]

class Form_Defination(models.Model):
    
    FORM_TYPE_CHOICES = [
        ('single', _("Single")),
        ('wizard', _("Wizard")),
    ]
    DSTYPE = [
        ('appdb','AppDB'),
        ('externalapi','External API'),
        ('externalDB','External DB'),
    ]
    DASHBOARD_VISIBILITY_CHOICES = [
        ('enabled', _("Enabled")),
        ('disabled', _("Disabled")),
    ]
    app_name = models.ForeignKey(Application,on_delete=models.CASCADE,null=True)   
    title = models.CharField(max_length=50,null=True,verbose_name=_("Title"))
    name = models.CharField(max_length=50,null=True,verbose_name=_("Name"))
    table_name = models.CharField(max_length=100,null=True, blank=True,choices=[], verbose_name=_("Table Name"))
    intro = models.TextField(max_length=500,null=True,blank=True,verbose_name=_("Intro"))
    button_text = models.CharField(verbose_name=_("Button text"), max_length=50,default=_("Submit"))
    response = models.TextField(max_length=50,verbose_name=_("Response"), blank=True)
    parentId = models.ForeignKey('self',null=True, on_delete=models.CASCADE, verbose_name=('Parent Page'))
    status = models.CharField(max_length=50,verbose_name=_("Status"), choices=STATUS_CHOICES,default='active')
    allowed_user_group = MultiSelectField(max_length=255,null=True,choices=allowed_group_choice,verbose_name=_('Allowed User Groups'))
    field_list = JSONField()
    total_entries = models.IntegerField(default=0,null=True,verbose_name=_('Total Entries'))
    data_view_url = models.URLField(null=True,blank=True)
    schema_obj = models.ForeignKey(JsonSchema, on_delete=models.CASCADE,null=True, verbose_name=_('Json Schema'))
    action_script = models.TextField(null=True,blank=True,verbose_name=_("After Action Scripts"))
    ttl = models.IntegerField(default=365, null=True, verbose_name=("TTL (Days)"))
    before_script = models.TextField(null=True,blank=True,verbose_name=_("Before Action Scripts"))
    ds_type = models.CharField(max_length=255,null=True,choices=DSTYPE,default='postgres',verbose_name=_('DataSource Type'))
    dashboard_visibility = models.CharField(max_length=50,verbose_name=_("Dashboad Visibility"), choices=DASHBOARD_VISIBILITY_CHOICES,default='enabled')

    class Meta:
        verbose_name = _("Page Defination")
        verbose_name_plural = _("Page Definations")
        unique_together = ('name', 'app_name')
    
    def __str__(self):
        return str(self.title)


class FormWizardDefination(models.Model):
    TEMPLATE_CHOICE =  [
        ('wizard','Wizard View'),
        ('single','Single View'),
        ('tab', 'Tab View'),
        ('custom','Custom View')
    ]
    app_name = models.ForeignKey(Application,on_delete=models.CASCADE,null=True)   
    title = models.CharField(max_length=50,null=True,verbose_name=_("Title"))
    name = models.CharField(max_length=50,null=True,unique=True,verbose_name=_("Name"))
    template_type = models.CharField(max_length=100, null=True, choices=TEMPLATE_CHOICE,verbose_name=_("Template Type"))
    allowed_user_group = MultiSelectField(max_length=255,null=True,choices=allowed_group_choice,verbose_name=_('Allowed User Groups'))
    table_name = models.CharField(max_length=100,null=True,verbose_name=_("Table Name"))
    status = models.CharField(max_length=50,verbose_name=_("Status"), choices=STATUS_CHOICES,default='active')
    total_entries = models.IntegerField(default=0,null=True,verbose_name=_('Total Entries'))

    class Meta:
        verbose_name = _("Page Group Defination")
        verbose_name_plural = _("Page Group Definations")
    
    def __str__(self):
        return str(self.title)

class WizardForm(models.Model):
     
    wizard_name = models.ForeignKey(FormWizardDefination,on_delete=models.CASCADE,verbose_name=_('Wizard Name'))
    page_name = models.CharField(max_length=50,null=True,unique=True,verbose_name=_("Name"))
    level = models.IntegerField(null=True,unique=True,verbose_name=_("Wizard Level"))
    form_def = models.OneToOneField(Form_Defination, on_delete=models.CASCADE, null=True, verbose_name=_("Form"))
    
    def __str__(self):  
        return str(self.page_name)

# class AbstractForm(models.Model):
#     """
#     A user-built form.
#     """

#     sites = models.ManyToManyField(Site,
#         default=[settings.SITE_ID], related_name="%(app_label)s_%(class)s_forms")
#     title = models.CharField(_("Title"), max_length=50)
#     slug = models.SlugField(_("Slug"), editable=settings.EDITABLE_SLUGS,
#         max_length=100, unique=True)
#     intro = models.TextField(_("Intro"), blank=True)
#     button_text = models.CharField(_("Button text"), max_length=50,
#         default=_("Submit"))
#     response = models.TextField(_("Response"), blank=True)
#     redirect_url = models.CharField(_("Redirect url"), max_length=200,
#         null=True, blank=True,
#         help_text=_("An alternate URL to redirect to after form submission"))
#     status = models.IntegerField(_("Status"), choices=STATUS_CHOICES,
#         default=STATUS_PUBLISHED)
#     publish_date = models.DateTimeField(_("Published from"),
#         help_text=_("With published selected, won't be shown until this time"),
#         blank=True, null=True)
#     expiry_date = models.DateTimeField(_("Expires on"),
#         help_text=_("With published selected, won't be shown after this time"),
#         blank=True, null=True)
#     login_required = models.BooleanField(_("Login required"), default=False,
#         help_text=_("If checked, only logged in users can view the form"))
#     send_email = models.BooleanField(_("Send email"), default=True, help_text=
#         _("If checked, the person entering the form will be sent an email"))
#     email_from = models.EmailField(_("From address"), blank=True,
#         help_text=_("The address the email will be sent from"))
#     email_copies = models.CharField(_("Send copies to"), blank=True,
#         help_text=_("One or more email addresses, separated by commas"),
#         max_length=200)
#     email_subject = models.CharField(_("Subject"), max_length=200, blank=True)
#     email_message = models.TextField(_("Message"), blank=True)

#     objects = FormManager()

#     class Meta:
#         verbose_name = _("Form")
#         verbose_name_plural = _("Forms")
#         abstract = True

#     def __str__(self):
#         return str(self.title)

#     def save(self, *args, **kwargs):
#         """
#         Create a unique slug from title - append an index and increment if it
#         already exists.
#         """
#         if not self.slug:
#             slug = slugify(self)
#             self.slug = unique_slug(self.__class__.objects, "slug", slug)
#         super(AbstractForm, self).save(*args, **kwargs)

#     def published(self, for_user=None):
#         """
#         Mimics the queryset logic in ``FormManager.published``, so we
#         can check a form is published when it wasn't loaded via the
#         queryset's ``published`` method, and is passed to the
#         ``render_built_form`` template tag.
#         """
#         if for_user is not None and for_user.is_staff:
#             return True
#         status = self.status == STATUS_PUBLISHED
#         publish_date = self.publish_date is None or self.publish_date <= now()
#         expiry_date = self.expiry_date is None or self.expiry_date >= now()
#         authenticated = for_user is not None and for_user.is_authenticated
#         if DJANGO_VERSION <= (1, 9):
#             # Django 1.8 compatibility, is_authenticated has to be called as a method.
#             authenticated = for_user is not None and for_user.is_authenticated()
#         login_required = (not self.login_required or authenticated)
#         return status and publish_date and expiry_date and login_required

#     def total_entries(self):
#         """
#         Called by the admin list view where the queryset is annotated
#         with the number of entries.
#         """
#         return self.total_entries
#     total_entries.admin_order_field = "total_entries"

#     def get_absolute_url(self):
#         return ("form_detail", (), {"slug": self.slug})

#     def admin_links(self):
#         kw = {"args": (self.id,)}
#         links = [
#             (_("View form on site"), self.get_absolute_url()),
#             (_("Filter entries"), reverse("admin:form_entries", **kw)),
#             (_("View all entries"), reverse("admin:form_entries_show", **kw)),
#             (_("Export all entries"), reverse("admin:form_entries_export", **kw)),
#         ]
#         for i, (text, url) in enumerate(links):
#             links[i] = "<a href='%s'>%s</a>" % (url, ugettext(text))
#         return "<br>".join(links)
#     admin_links.allow_tags = True
#     admin_links.short_description = ""


# class FieldManager(models.Manager):
#     """
#     Only show visible fields when displaying actual form..
#     """
#     def visible(self):
#         return self.filter(visible=True)

# class AbstractField(models.Model):
#     """
#     A field for a user-built form.
#     """

#     label = models.CharField(_("Label"), max_length=settings.LABEL_MAX_LENGTH)
#     slug = models.SlugField(_('Slug'), max_length=100, blank=True,
#             default="")
#     field_type = models.IntegerField(_("Type"), choices=fields.NAMES)
#     required = models.BooleanField(_("Required"), default=True)
#     visible = models.BooleanField(_("Visible"), default=True)
#     choices = models.CharField(_("Choices"), max_length=settings.CHOICES_MAX_LENGTH, blank=True,
#         help_text="Comma separated options where applicable. If an option "
#             "itself contains commas, surround the option starting with the %s"
#             "character and ending with the %s character." %
#                 (settings.CHOICES_QUOTE, settings.CHOICES_UNQUOTE))
#     default = models.CharField(_("Default value"), blank=True,
#         max_length=settings.FIELD_MAX_LENGTH)
#     placeholder_text = models.CharField(_("Placeholder Text"), null=True,
#         blank=True, max_length=100, editable=settings.USE_HTML5)
#     help_text = models.CharField(_("Help text"), blank=True, max_length=settings.HELPTEXT_MAX_LENGTH)

#     objects = FieldManager()

#     class Meta:
#         verbose_name = _("Field")
#         verbose_name_plural = _("Fields")
#         abstract = True

#     def __str__(self):
#         return str(self.label)

#     def get_choices(self):
#         """
#         Parse a comma separated choice string into a list of choices taking
#         into account quoted choices using the ``settings.CHOICES_QUOTE`` and
#         ``settings.CHOICES_UNQUOTE`` settings.
#         """
#         choice = ""
#         quoted = False
#         for char in self.choices:
#             if not quoted and char == settings.CHOICES_QUOTE:
#                 quoted = True
#             elif quoted and char == settings.CHOICES_UNQUOTE:
#                 quoted = False
#             elif char == "," and not quoted:
#                 choice = choice.strip()
#                 if choice:
#                     yield choice, choice
#                 choice = ""
#             else:
#                 choice += char
#         choice = choice.strip()
#         if choice:
#             yield choice, choice

#     def is_a(self, *args):
#         """
#         Helper that returns True if the field's type is given in any arg.
#         """
#         return self.field_type in args



