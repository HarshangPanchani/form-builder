from django import forms
from .models import *
from django.utils.translation import gettext as _

class FormDefinitionForm(forms.ModelForm):
    class Meta:
        model = Form_Defination
        fields = '__all__'
        exclude = ('app_name','total_entries','intro','response','button_text','field_list', 'db_ref','schema','parentId')
        widgets = {
            'allowed_user_group':forms.SelectMultiple(),
            # 'table_name':forms.ChoiceField(),
            # 'db_password': forms.PasswordInput(),
            # 'main_jrxml': forms.FileInput(),
            # 'csv_file': forms.FileInput(),
        }

    def __init__(self, *args, **kwargs):
        app_id = kwargs.pop('app_id', None)
        super(FormDefinitionForm, self).__init__(*args, **kwargs)
        table_names= Form_Defination.objects.filter(app_name=app_id).values('table_name')
        table_choice=[]
        for table_name_obj in list(table_names):
            table_choice.append((table_name_obj['table_name'],table_name_obj['table_name']))
        for visible in self.visible_fields():
            visible.field.widget.attrs['class'] = 'form-control'
            print(visible.name)
            if visible.name == 'table_name':
                visible.field.choices=table_choice
                visible.field._choices=table_choice
                visible.field.widget.choices= table_choice
        self.fields['table_name'].required=False
        self.fields['schema_obj'].required=False
                
                
        # self.fields['intro'].required = False
        # self.fields['button_text'].required = False
        self.fields['name'].required = False
        # self.fields['table_name'].widget.attrs['readonly'] = True
        # self.fields['db_ref'].required = False
        # self.fields['parentId'].required = False
        if app_id:
            self.fields['schema_obj'].queryset = self.fields['schema_obj'].queryset.filter(app_name_id=app_id)

class FormWizardDefinitionForm(forms.ModelForm):
    class Meta:
        model = FormWizardDefination
        fields = '__all__'
        widgets = {
            'allowed_user_group':forms.SelectMultiple()
        }
        exclude = ('app_name','total_entries','table_name')
     
    def __init__(self, *args, **kwargs):
        super(FormWizardDefinitionForm, self).__init__(*args, **kwargs)
        for visible in self.visible_fields():
            visible.field.widget.attrs['class'] = 'form-control'
        # self.fields['intro'].required = False
        # self.fields['button_text'].required = False
      

class WizardFormListForm(forms.ModelForm):
    class Meta:
        model = WizardForm
        fields = '__all__'
        exclude = ('wizard_name','page_name')

    def __init__(self, *args, **kwargs):
        super(WizardFormListForm, self).__init__(*args, **kwargs)
        for visible in self.visible_fields():
            visible.field.widget.attrs['class'] = 'form-control'
        # self.fields['intro'].required = False
        # self.fields['button_text'].required = False

class JsonSchemaForm(forms.ModelForm):
    assignedPages = forms.MultipleChoiceField(required=False, widget=forms.SelectMultiple,label='Select Pages')
    class Meta:
        model = JsonSchema
        fields = '__all__'
        exclude = ('app_name','db_ref')
    def __init__(self, *args, **kwargs):
        super(JsonSchemaForm, self).__init__(*args, **kwargs)
        for visible in self.visible_fields():
            visible.field.widget.attrs['class'] = 'form-control'
        instance = kwargs.get('instance')
        app_value = instance.app_name if instance else None
        id = instance.id if instance else None
        choices = Form_Defination.objects.filter(schema_obj=id, app_name=app_value).values_list('id', 'title')
        self.fields['assignedPages'].choices = choices
        self.fields['schema'].required = False
        self.fields['formScript'].required = False
        
      

