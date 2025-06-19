from django.urls import path
from .views import FormBuilderView


urlpatterns = [
    path("schema/add/get_form_data/", FormBuilderView.get_form_data, name="get_form_data"),
    path('form_defination/',FormBuilderView.form_defination_list,name='form_defination'),
    path('schema_editor/',FormBuilderView.schema_editor_view,name='schema_editor'),
    path('schema/add',FormBuilderView.add_schema,name='add_schema'),
    path('schema/<str:pk>/edit/',FormBuilderView.edit_schema,name='edit_schema'),
    path('schema/<str:pk>/delete/',FormBuilderView.delete_schema,name='delete_schema'),
    path('add/',FormBuilderView.add_form_defination,name='add_form_defination'),
    
    path('<str:pk>/edit/',FormBuilderView.edit_form_defination,name='edit_form_defination'),
    path('defination/<str:pk>/delete/',FormBuilderView.delete_form_defination, name='delete_form_defination'),
    path('<str:pk>/',FormBuilderView.form_view,name='form_view'),
    path('<str:pk>/entries',FormBuilderView.form_entry_view,name='form_entry'),
    path('entry/<str:pk>/delete/',FormBuilderView.form_entry_delete,name='form_entry_delete'),
    path('<str:pk>/edit/<str:obj_id>/',FormBuilderView.form_entry_edit,name='form_entry_edit'),

    #wizard
    path('Wizard_entry_view/<str:pk>', FormBuilderView.Wizard_entry_list, name="wizard_entry"),
    path('page-group/add/',FormBuilderView.add_wizard_defination,name='add_wizard_defination'),
    path('page-group/<str:pk>/',FormBuilderView.wizard_form_view,name='wizard_form_view'),
    path('page-group/<str:pk>/edit/',FormBuilderView.edit_wizard_defination,name='edit_wizard_defination'),
    path('page-group/<str:pk>/delete/', FormBuilderView.delete_wizard_defination, name='delete_wizard_defination'),
    
    
    # path('<str:pk>/edit/',view.edit_form_defination,name='edit_form_defination'),
    # path('<str:pk>/',view.form_view,name='form_view'),
    # path('<str:pk>/entries',view.form_entry_view,name='form_entry'),
    # path('<str:pk>/delete/',view.form_entry_delete,name='form_entry_delete'),
    # path('<str:pk>/edit/<str:obj_id>/',view.form_entry_edit,name='form_entry_edit'),

]