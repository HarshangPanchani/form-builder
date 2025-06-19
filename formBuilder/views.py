#Basic
from email import message
import string
from django.db import connection
from django.shortcuts import get_object_or_404, render, redirect
from django.http import JsonResponse, HttpResponseRedirect
from django.views import View
from formBuilder.forms import *
from django.contrib import messages
from formBuilder.models import *
from django.contrib.auth.decorators import login_required
from django.utils.translation import gettext as _    #localization
from scheduler.views import apscheduler
from pymodbus.constants import Endian
from django.core.files.storage import FileSystemStorage
from django.conf import settings
from django.http import Http404  
from deviceAdapter.common_methods import *
from deviceAdapter.models import DataViewModel, Application
from django.utils.crypto import get_random_string
import json
#logging
import logging
logger = logging.getLogger(__name__)

#Others
from formBuilder.handler import *
from .decorators import form_module_check
from core.decorators import validate_license
from django.contrib.auth.decorators import permission_required

class FormBuilderView:

    def get_form_data(request, app_id):
        try:
            if request.method == "GET":  
                queries = request.GET.getlist('query[]') 

                results = {}
                with connection.cursor() as cursor:
                    for query in queries:
                        cursor.execute(query)
                        key = query.split('FROM')[1].strip()  
                        results[key] = [row[0] for row in cursor.fetchall()]

                return JsonResponse(results, safe=False)
        except Exception as e:
            logger.error("FormBuilderView.get_form_data ->" + str(e))

    @validate_license
    @form_module_check
    @login_required(login_url='login')
    def form_defination_list(request,app_id):
        try:
            user_group = list(request.user.groups.values_list('name',flat = True))
            schema_obj = JsonSchema.objects.filter(app_name=app_id)
            obj = None
            wizz_obj = None
            if request.user.is_superuser:
                obj=Form_Defination.objects.filter(app_name=app_id) 
                wizz_obj = FormWizardDefination.objects.filter(app_name=app_id)
            else:
                obj1=list(Form_Defination.objects.filter(app_name=app_id, status='active').values_list('allowed_user_group','id'))
                wiz_obj = list(FormWizardDefination.objects.filter(app_name=app_id, status='active').values_list('allowed_user_group','id'))
                app_id_list = []
                wiz_id_list = []
                for i in obj1:
                    for u in user_group:
                        if u in i[0]:
                            app_id_list.append(i[1])
                            break
                for j in wiz_obj:
                    for u in user_group:
                        if u in j[0]:
                            wiz_id_list.append(j[1])
                            break
                obj=Form_Defination.objects.filter(id__in=app_id_list)
                wizz_obj=FormWizardDefination.objects.filter(id__in=wiz_id_list)
            context={'form_objs':obj, 'schema_obj':schema_obj, 'page_grp_objs': wizz_obj}
            return render(request,'formBuilder/index.html',context)
        except Exception as e:
            logger.error("FormBuilderView.form_defination_list ->" + str(e))


    @form_module_check
    @login_required(login_url='login')
    @permission_required('formBuilder.add_jsonschema',raise_exception=True)
    def add_schema(request,app_id):
        try:
            form = JsonSchemaForm()
            app = Application.objects.get(id=app_id)
            if request.method == "POST":        
                form = JsonSchemaForm(request.POST)
                if form.is_valid():
                    instance = form.save(commit=False)
                    instance.app_name = app
                    instance.save()
                    return redirect('form_defination',app_id)
            context = {'form':form}
            return render(request,'formBuilder/add_schema.html',context)
        except Exception as e:
            logger.error("FormBuilderView.add_schema ->" + str(e))
        return render(request, 'formBuilder/add_schema.html', {'form': form})


    @validate_license
    @form_module_check
    @login_required(login_url='login')
    @permission_required('formBuilder.change_jsonschema',raise_exception=True)
    def edit_schema(request, pk, app_id):
        try:
            schema_obj = JsonSchema.objects.get(id=pk)
            form = JsonSchemaForm(instance=schema_obj)
            new_schema_obj = None
            schema = json.dumps(schema_obj.schema)
            oldJs = json.dumps(schema_obj.formScript)

            if request.method == 'POST':
                form = JsonSchemaForm(request.POST, instance=schema_obj)

                if form.is_valid():
                    checked_pages = form.cleaned_data['assignedPages']
                    cPages = [eval(i) for i in checked_pages]

                    if not checked_pages and Form_Defination.objects.filter(schema_obj=pk, app_name=app_id).exists():
                        messages.info(request, _('Please select at least one page'))

                    elif set(cPages) == set(Form_Defination.objects.filter(schema_obj=pk, app_name=app_id).values_list('id', flat=True)):
                        form_obj = form.save(commit=False)
                        form_obj.formScript = form_obj.formScript
                        form_obj.save()
                    else:
                        new_schema_obj = JsonSchema.objects.create(
                            app_name=schema_obj.app_name,
                            formScript=schema_obj.formScript,
                            schema=schema_obj.schema,
                            schema_name=f"{schema_obj.schema_name}_{FormBuilderView.generate_random_value()}"
                        )
                        new_schema_obj.save()

                        for i in checked_pages:
                            defObj = Form_Defination.objects.get(id=int(i))
                            defObj.schema_obj = new_schema_obj
                            defObj.save()

                    return redirect('form_defination', app_id)

            context = {'form': form, 'form_id': pk, 'schema': schema, 'oldJs': oldJs[1:-1]}
            return render(request, 'formBuilder/edit_schema.html', context)
        except Exception as e:
            logger.error("FormBuilderView.edit_schema ->" + str(e))
    
        

    def generate_random_value():
            try:
                characters = string.ascii_letters + string.digits
                random_value = ''.join(random.choice(characters) for _ in range(4))
                return random_value
            except Exception as e:
                logger.error("FormBuilderView.generate_random_value ->" + str(e))

    def delete_schema(request, pk, app_id):
        try:
            schema_obj = JsonSchema.objects.get(id=pk)
            form = JsonSchemaForm(instance=schema_obj)

            if request.method == "POST":
                schema_obj.delete()
                return redirect('form_defination', app_id)

            context = {'form':form, 'form_id':pk}
            return render(request, 'formBuilder/index.html', context)
        except Exception as e:
            logger.error("FormBuilderView.delete_schema ->" + str(e))

    @validate_license
    @form_module_check
    @login_required(login_url='login')
    @permission_required('formBuilder.add_form_defination',raise_exception=True)
    def add_form_defination(request,app_id):
        try:
            form = FormDefinitionForm(app_id=app_id)
            if request.method=='POST':        
                name = request.POST.get('title')
                name = name_builder(name)
                updated_request = request.POST.copy() 
                updated_request.update({'name': name})
                form = FormDefinitionForm(updated_request,app_id=app_id)
                if form.is_valid():
                    form_obj = form.save(commit=False)
                    app = Application.objects.get(id=app_id)
                    form_obj.app_name = app
                    table_name = f"ts_{app.name}_form_data_{form_obj.name}"
                    form_obj.table_name = table_name
                    if form_obj.parentId:
                        FormBuilderHandle.schema2databsehandler(form_obj.schema_obj.schema, app.name,table_name, form_obj.name,parent_id='parent_id')
                    else:
                        FormBuilderHandle.schema2databsehandler(form_obj.schema_obj.schema,app.name, table_name,form_obj.name)
                    old_json_schema = form_obj.schema_obj.schema
                    req_field = old_json_schema['required'] if 'required' in old_json_schema else []
                    json_schema = {}
                    if req_field:
                        json_schema['required'] = [(" ".join(i.split())).replace(' ','_').replace('-','_').lower() for i in req_field]
                    if 'title' not in old_json_schema:
                        old_json_schema['title']="no title found"
                    json_schema['title'] = old_json_schema['title']
                    json_schema['properties'] = {}
                    col_names = []
                    if form_obj.parentId:
                        col_names.append([f'{form_obj.parentId.name}_id', 'integer'])
                    for i in old_json_schema['properties']:
                        property_val = old_json_schema['properties'][i]
                        name = (" ".join(i.split())).replace(' ','_').replace('-','_').lower()
                        json_schema['properties'][name] = property_val
                        col_names.append([name, json_postgres_datatype[property_val['type']]])
                    field_list = {i[0] : i[1] for i in col_names}
                    form_obj.field_list = field_list
                    form_obj.save()
                    logger.info(_('New Form created with parameter(name: {}, allowed_user:{})').format(form_obj.name, form_obj.allowed_user_group))
                    messages.info(request,_('New Form created successfully.'))
                    return redirect('form_defination',app_id)
                    # table, msg = create_table_with_custom_field(table_name, col_names)
                    # if table:
                        # auth_token = get_random_string(length=32)
                        # current_url = f'{request.scheme}://{request.get_host()}/{request.LANGUAGE_CODE}/api/data-view/{auth_token}/'
                        # form_obj.data_view_url = current_url
                        # form_obj.save()
                        # DataViewModel.objects.create(app_name = app, name = form_obj.title, db_table_name= table_name, data_source = 'adapter', adapter_type='form_data', data_form = Form_Defination.objects.get(id=form_obj.id), end_point=current_url, auth_token=auth_token, filter_field_name='datetime',field_datatype='datetime-local')
                        # logger.info(_('New Form created with parameter(name: {}, form type: {}, allowed_user:{})').format(form_obj.name, form_obj.form_type, form_obj.allowed_user_group))
                        # messages.info(request,_('New Form created successfully.'))
                        # return redirect('form_defination',app_id)
                    # else:
                    #     messages.error(request, msg)
                else:
                    # logger.error(form.errors)
                    messages.error(request,form.errors)

            context={'form':form}
            return render(request,'formBuilder/add_defination.html',context)
        except Exception as e:
            logger.error("FormBuilderView.add_form_defination ->" + str(e))

    @validate_license
    @form_module_check
    @login_required(login_url='login')
    @permission_required('formBuilder.change_form_defination',raise_exception=True)
    def edit_form_defination(request,pk,app_id):
        try:
            app = Application.objects.get(id=app_id)
            form_obj = Form_Defination.objects.get(id=pk)
            form = FormDefinitionForm(instance=form_obj,app_id=app_id)
            if request.method=='POST':       
                updated_request = request.POST.copy() 
                updated_request.update({'name': form_obj.name})
                form = FormDefinitionForm(updated_request, instance=form_obj,app_id=app_id) 
                if form.is_valid():
                    table_name = f"ts_{app.name}_form_data_{form_obj.name}"
                    form_obj.table_name = table_name
                    form_obj = form.save()
                    logger.info(_(f"Form '{form_obj.title}' detail updated successfully."))
                    messages.info(request,_(f"Form '{form_obj.title}' detail updated successfully."))
                    return redirect('form_defination',app_id)
                else:
                    messages.error(request,form.errors)

            context={'form':form, 'form_id' : pk}
            return render(request,'formBuilder/edit_defination.html',context)
        except Exception as e:
            logger.error("FormBuilderView.edit_form_defination ->" + str(e))

    def delete_form_defination(request,pk,app_id):
        try:
            try:
                form_obj = Form_Defination.objects.get(id=pk)
            except Form_Defination.DoesNotExist:
                messages.error(request, "Form Defination is not found")
                return redirect('form_defination', app_id)

            if request.method == "POST":
                if not request.user.has_perm("formBuilder.delete_form_defination"):
                    messages.error(request, "You do not have a permission to delete this form defination")
                    return redirect('form_defination', app_id)

                form_obj.delete()

                messages.success(request, "Form defination deleted successfully")
                return redirect('form_defination', app_id)

            context = {'form':form_obj}
            return render(request, 'formBuilder/edit_defination.html',context)
        except Exception as e:
            logger.error("FormBuilderView.delete_form_defination ->" + str(e))


    @validate_license
    @form_module_check
    @login_required(login_url='login')
    def form_entry_view(request,pk,app_id):
        try:
            cursorDJango=connection.cursor()
            definition = Form_Defination.objects.get(id=pk)
            result_list = get_json_data1(start=0,length=0,tablename=definition.table_name,cur=cursorDJango,q_type = 'table')
            
            context = {'definition':definition, 'parent_table':result_list}
            return render(request,'formBuilder/entries_list.html',context)
        except Exception as e:
            logger.error("FormBuilderView.form_entry_view ->" + str(e))
        finally:
            close_connection(cursorDJango)

    @validate_license
    @form_module_check
    @login_required(login_url='login')
    def form_view(request,pk,app_id):
        try:
            definition = Form_Defination.objects.get(id=pk)
            param = definition.schema_obj.schema['properties']
            table_name = definition.table_name
            app = Application.objects.get(id=app_id)

            if bool(definition.schema_obj.db_ref):
                value = db_ref_handler(definition.schema_obj.db_ref)
                for key in value:
                    obj = param[key]
                    obj['enum']=value[key]

            if request.method == 'POST':
                if 'form_submit' in request.POST:
                    # filter_dict = {k:dict(request.POST)[k] for k in dict(request.POST) if k.startswith('root')}
                    # filter_dict = {k.replace('root','').replace('[','').replace(']',''): filter_dict[k]  for k in filter_dict}
                    json_data = json.loads(request.POST.get('json_data'))
                    if definition.parentId:
                        FormBuilderHandle.jsonschema2insert(definition.schema_obj.schema,table_name,json_data, parent_id='parent_id')
                    else:
                        FormBuilderHandle.jsonschema2insert(definition.schema_obj.schema, table_name,json_data)
                    Form_Defination.objects.filter(id=pk).update(total_entries=definition.total_entries+1)
                    messages.info(request,_('Form submitted successfully.'))
                    # status,error = insertFormDataHandler(definition, filter_dict)

            schema  = json.dumps(definition.schema_obj.schema)
            script = json.dumps(definition.schema_obj.formScript)
            context = {'definition':definition, 'schema':schema, 'script':script}
            return render(request,'formBuilder/form_view.html',context)
        except Exception as e:
           logger.error("FormBuilderView.form_view ->" + str(e))

    @validate_license
    @form_module_check
    @login_required(login_url='login')
    def form_entry_delete(request,pk,app_id):
        try:
            if request.method == 'GET':
                definition = Form_Defination.objects.get(id=pk)
                obj_id = request.GET.get('id')
                delete_record_from_db(definition.table_name, obj_id=obj_id)
                Form_Defination.objects.filter(id=pk).update(total_entries=definition.total_entries-1)
                messages.success(request, 'Item deleted successfully.')
            return redirect('form_entry', app_id, pk)
        except Exception as e:
            logger.error("FormBuilderView.form_entry_delete ->" + str(e))


    @validate_license
    @form_module_check
    @login_required(login_url='login')
    def form_entry_edit(request,pk,obj_id,app_id):
        try:
            cursorDJango=connection.cursor()
            definition = Form_Defination.objects.get(id=pk)
            child_definition = Form_Defination.objects.filter(parentId=pk)
            param = definition.schema_obj.schema['properties']

            if bool(definition.schema_obj.db_ref):
                value = db_ref_handler(definition.schema_obj.db_ref)
                for key in value:
                    obj = param[key]
                    obj['enum']=value[key]

            if request.method == 'POST':
                if 'form_submit' in request.POST:
                    # filter_dict = {k:dict(request.POST)[k] for k in dict(request.POST) if k.startswith('root')}
                    # filter_dict = {k.replace('root','').replace('[','').replace(']',''): filter_dict[k]  for k in filter_dict}
                    row_id = request.POST.get('parent_form_id')
                    filter_dict = json.loads(request.POST.get('json_data'))
                    if definition.parentId:
                        FormBuilderHandle.jsonschema2update(definition.schema_obj.schema, definition.table_name,filter_dict,row_id, parent_id=parent_id)
                    else:
                        FormBuilderHandle.jsonschema2update(definition.schema_obj.schema, definition.table_name,filter_dict,row_id)
                    # status,error = updateFormDataHandler(definition, filter_dict, row_id)
                    return redirect('form_entry', app_id, pk)

                elif 'modal_form_submit' in request.POST:
                    # filter_dict = {k:dict(request.POST)[k] for k in dict(request.POST) if k.startswith('root')}
                    # filter_dict = {k.replace('root','').replace('[','').replace(']',''): filter_dict[k]  for k in filter_dict}
                    form_def = child_definition.filter(id=request.POST.get('modal_form_id')).first()
                    parent_id = request.POST.get('child_parent_form_id')
                    json_data = json.loads(request.POST.get('child_json_data'))
                    if form_def.parentId:
                        FormBuilderHandle.jsonschema2insert(form_def.schema_obj.schema, form_def.table_name,json_data, parent_id=parent_id)
                    else:
                        FormBuilderHandle.jsonschema2insert(form_def.schema_obj.schema, form_def.table_name,json_data)
                    # status,error = insertFormDataHandler(form_def, filter_dict)

            param = {}
            param['startindex'] = obj_id
            param['filter_field'] = f'id'
            param['filter_operation'] = '='

            result_list = get_json_data1(start=0,length=0,tablename=definition.table_name,cur=cursorDJango,q_type = 'table',param=param)[0]

            result_list = json.dumps(result_list, default=str)

            child_value_list = {}   
            param['filter_field'] = f'parent_id'

            for each in child_definition:
                child_result_list = get_json_data1(start=0,length=0,tablename=each.table_name,cur=cursorDJango,q_type = 'table',param=param)
                if child_result_list:
                    child_value_list[each.name] = child_result_list

            child_column_list = {}  
            for each in child_definition:
                column_list = get_column_name_list('postgres',each.table_name,cur=cursorDJango) 
                child_column_list[each.name] = column_list
            schema  = json.dumps(definition.schema_obj.schema)
            context = {'definition':definition, 'schema':schema,'obj_id':obj_id,  'child_definition':child_definition, 'parent_form_data':result_list, 'child_list':child_definition, 'child_value_list':child_value_list, 'child_column_list':child_column_list, 'obj_id':obj_id}
            return render(request,'formBuilder/edit_entries.html',context)
        except Exception as e:
            logger.error("FormBuilderView.form_entry_edit ->" + str(e))
        finally:
            close_connection(cursorDJango)

    @validate_license
    @form_module_check
    @login_required(login_url='login')
    def schema_editor_view(request,app_id):
        try:
            context={}
            return render(request,'formBuilder/demo.html',context)
        except Exception as e:
            logger.error("FormBuilderView.schema_editor_view ->" + str(e))

    @validate_license
    @form_module_check
    @login_required(login_url='login')
    def add_wizard_defination(request,app_id):
        try:
            form = FormWizardDefinitionForm()
            if request.method=='POST':        
                name = request.POST.get('title')
                name = name_builder(name)
                updated_request = request.POST.copy() 
                updated_request.update({'name': name})
                form = FormWizardDefinitionForm(updated_request)
                if form.is_valid():
                    form_obj = form.save(commit=False)
                    app = Application.objects.get(id=app_id)
                    form_obj.app_name = app
                    table_name = 'page_group_data_'+ form_obj.name             ########################here##############################
                    table, msg = create_blank_table(table_name)
                    if table:
                        form_obj.table_name = table_name
                        form_obj.save()
                        logger.info(_('New Page Group created with parameter(name: {}, template_type: {}, allowed_user:{})').format(form_obj.name, form_obj.template_type, form_obj.allowed_user_group))
                        messages.info(request,_('New Page Group created successfully.'))
                        return redirect('edit_wizard_defination',app_id, form_obj.id)

            context={'form':form}
            return render(request,'formBuilder/add_wizard_defination.html',context)
        except Exception as e:
            logger.error("FormBuilderView.add_wizard_defination ->" + str(e))

    @validate_license
    @form_module_check
    @login_required(login_url='login')
    @permission_required('formBuilder.add_formwizarddefination',raise_exception=True)
    def edit_wizard_defination(request,pk,app_id):
        try:
            wiz_obj = FormWizardDefination.objects.get(id=pk)
            wiz_form_obj = WizardForm.objects.filter(wizard_name = pk)
            form = FormWizardDefinitionForm(instance=wiz_obj)
            page_form = WizardFormListForm()
            if request.method == 'POST':
                if 'wiz_def' in request.POST:
                    form = FormWizardDefinitionForm(request.POST,instance=wiz_obj)
                    if form.is_valid():
                        form.save()
                        return redirect('form_defination',app_id)
                    else:
                        messages.error(request, form.errors)
                elif 'add_page' in request.POST:
                    page_form = WizardFormListForm(request.POST)
                    if page_form.is_valid():
                        obj = page_form.save(commit=False)
                        obj.page_name = obj.form_def.name
                        obj.wizard_name = wiz_obj
                        table = wiz_obj.table_name
                        table, msg = add_column(obj.page_name, table)
                        if table:
                            obj.save()
                            logger.info(_(f'New Page added with parameter(name: {obj.page_name}, page level: {obj.level})'))
                            messages.info(request,_('New Page added successfully.'))
                        else:
                            WizardForm.objects.filter(id=obj.id).delete()
                            messages.info(request, msg)
                    else:
                        logger.error(page_form.errors)   
                        messages.info(request, page_form.errors)

                elif 'edit_page' in request.POST:
                    id = request.POST.get('page_id')
                    page = WizardForm.objects.get(id=id)
                    page_edit_form = WizardFormListForm(request.POST,instance=page)
                    if page_edit_form.is_valid():
                        page_edit_form.save()
                        logger.info(_(f'Page "{page.page_name}" detail updated successfully.'))
                    else:
                        logger.error(page_edit_form.errors)   
                        messages.info(request,page_edit_form.errors)

                elif 'delete_page' in request.POST:
                    id =request.POST.get('page_id')
                    page = WizardForm.objects.get(id=id)
                    page.delete()
                    logger.info(_(f'Page {page.page_name} deleted successfully.'))
                    messages.info(request,_(f'Page {page.page_name} deleted successfully.'))

                else:
                    print(request.POST)
                    pass
                
            context={'form':form, 'pk':pk, 'page_form':page_form, 'wiz_form_obj':wiz_form_obj}
            return render(request,'formBuilder/edit_wizard_defination.html',context)
        except Exception as e:
            logger.error("FormBuilderView.edit_wizard_defination ->" + str(e))

    @validate_license
    @form_module_check
    @login_required(login_url='login')
    def wizard_form_view(request,pk,app_id):
        try:
            wizard_def = FormWizardDefination.objects.get(id=pk)
            wizard_forms = WizardForm.objects.filter(wizard_name=pk).order_by('level')
            schema_dict = {}
            for i in wizard_forms:
                param = i.form_def.schema_obj.schema['properties']
                if bool(i.form_def.schema_obj.db_ref):
                    value = db_ref_handler(i.form_def.schema_obj.db_ref)
                    for key in value:
                        obj = param[key]
                        obj['enum']=value[key]
                temp = {
                    'schema_id' : i.id,
                    'schema' : i.form_def.schema_obj.schema,
                    'level': i.level,
                    'schema_name' : i.page_name
                }
                schema_dict[i.page_name] = temp

            if request.method == 'POST':
                if 'form_submit' in request.POST:
                    json_data = json.loads(request.POST.get('json_data'))
                    for i in json_data:
                        print(i,json_data[i])
                        # jsonschema2insert(i.form_def.schema_obj.schema, i.form_def.table_name,i)
                        # FormWizardDefination.objects.filter(id=pk).update(total_entries=wizard_def.total_entries+1)
                    messages.info(request,_('Form submitted successfully.'))

            schema  = json.dumps(schema_dict)
            context = {'definition':wizard_def, 'schema_dict':schema_dict, 'schema':schema}
            return render(request,'formBuilder/wizard_form_view.html',context)
        except Exception as e:
            logger.error("FormBuilderView.wizard_form_view ->" + str(e))
        

    def delete_wizard_defination(request, pk, app_id):
        try:
            try:
                wiz_obj = FormWizardDefination.objects.get(id=pk)
            except:
                messages.error(request, "Wizard defintion not found")
                return redirect('form_defination', app_id)

            if request.method == "POST":
                if not request.user.has_perm('formBuilder.delete_form_defination'):
                    messages.error(request, "You do not have permission to delete this wizard definition.")
                    return redirect('form_defination', app_id)

                wiz_obj.wizardform_set.all().delete()
                wiz_obj.delete()

                messages.success(request, "Wizard defination deleted successfully")
                return redirect('form_defination', app_id)

            context = {'page_grp_objs':wiz_obj}
            return render(request, 'formBuilder/index.html', context)
        except Exception as e:
            logger.error("FormBuilderView.delete_wizard_defination ->" + str(e))

    def Wizard_entry_list(request, pk, app_id):
        try:
            wizard_defination = Form_Defination.objects.get(id=pk)
            result_list = create_blank_table(wizard_defination.table_name, q_type='table')
            context = {'wizard_defination':wizard_defination, 'Wizard_entries':result_list}
            return render(request, 'formBuilder/wizard_entries_list.html', context)
        except Exception as e:
            logger.error("FormBuilder.wizard_entry_list.html -->" + str(e))
           