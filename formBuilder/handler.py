from random import randint
from attr import field
from deviceAdapter.common_methods import *
import json
import psycopg2
from formBuilder.jsonschema2db import JSONSchemaToPostgres
from deviceAdapter.common_methods import *
import random
from django.db import connection as conn

class FormBuilderHandle:

    def schema2databsehandler(schema,app_name,table_name,defName,parent_id=None):
        try:
            if parent_id:
                translator = JSONSchemaToPostgres(
                    schema,
                    postgres_schema='public',
                    database_flavor='postgres',
                    root_table=table_name,
                    extra_columns=[('parent_id', 'integer')],
                    abbreviations={
                        'AbbreviateThisReallyLongColumn': 'AbbTRLC',
                    },
                    debug=False
                )
            else:
                translator = JSONSchemaToPostgres(
                    schema,
                    postgres_schema='public',
                    database_flavor='postgres',
                    root_table=table_name,
                    abbreviations={
                        'AbbreviateThisReallyLongColumn': 'AbbTRLC',
                    },
                    debug=False
                )
            translator.create_tables(conn,app_name,defName)
            return True
        except Exception as e:
                logger.error("FormBuilderHandle.schema2databsehandler ->" + str(e))
                return False

    # translator.insert_items(con, [
    #     ('loan_file_abc123', {
    #         'Loan': {'Amount': 500000},
    #         'SubjectProperty': {'Address': {'City': 'New York', 'ZipCode': '12345', 'Latitude': 43}, 'Acreage': 42},
    #         'RealEstateOwned': {'1': {'Address': {'City': 'Brooklyn', 'ZipCode': '65432'}, 'RentalIncome': 1000},
    #                             '2': {'Address': {'City': 'Queens', 'ZipCode': '54321'}}},
    #     })
    # ])
    # translator.update_items(con, [
    #     ('loan_file_abc123', {
    #         'Loan': {'Amount': 500000},
    #         'SubjectProperty': {'Address': {'City': 'New York', 'ZipCode': '12345', 'Latitude': 43}, 'Acreage': 42},
    #         'RealEstateOwned': {'1': {'Address': {'City': 'Brooklyn', 'ZipCode': '65432'}, 'RentalIncome': 1000},
    #                             '2': {'Address': {'City': 'Queens', 'ZipCode': '54321'}}},
    #     })
    # ], 1)

    def jsonschema2insert(schema, table_name,data,parent_id=None):
        try:
            if parent_id:
                translator = JSONSchemaToPostgres(
                    schema,
                    postgres_schema='public',
                    database_flavor='postgres',
                    root_table=table_name,
                    extra_columns=[('parent_id', 'integer')],
                    abbreviations={
                        'AbbreviateThisReallyLongColumn': 'AbbTRLC',
                    },
                    debug=False
                )
                randomint = random.randint(1,99999)
                translator.insert_items(conn, [(randomint,data)], {randomint: {'parent_id': parent_id}})
                translator.create_links(conn)
            else:
                translator = JSONSchemaToPostgres(
                    schema,
                    postgres_schema='public',
                    database_flavor='postgres',
                    root_table=table_name,
                    abbreviations={
                        'AbbreviateThisReallyLongColumn': 'AbbTRLC',
                    },
                    debug=False
                )
                translator.insert_items(conn,[(random.randint(1,99999),data)])
    
            return True
        except Exception as e:
                logger.error("FormBuilderHandle.jsonschema2insert ->" + str(e))

    def jsonschema2update(schema, table_name,data,row_id,parent_id=None):
        try:
            if parent_id:
                translator = JSONSchemaToPostgres(
                    schema,
                    postgres_schema='public',
                    database_flavor='postgres',
                    root_table=table_name,
                    extra_columns=[('parent_id', 'integer')],
                    abbreviations={
                        'AbbreviateThisReallyLongColumn': 'AbbTRLC',
                    },
                    debug=False
                )
                randomint = random.randint(1,99999)
                translator.update_items(conn, [(randomint,data)], {randomint: {'parent_id': parent_id}},row_id=row_id)
                translator.create_links(conn)
            else:
                translator = JSONSchemaToPostgres(
                    schema,
                    postgres_schema='public',
                    database_flavor='postgres',
                    root_table=table_name,
                    abbreviations={
                        'AbbreviateThisReallyLongColumn': 'AbbTRLC',
                    },
                    debug=False
                )
                translator.update_items(conn, [(random.randint(1,99999),data)],row_id=row_id)

            return True
        except Exception as e:
            logger.error("FormBuilderHandle.jsonschema2update ->" + str(e))
        

    def insertFormDataHandler(definition,valDict):
        try:
            tablename = definition.table_name
            field_list = definition.field_list
            available_field = list(field_list.keys())
            valDict = {k:valDict[k][0] if len(valDict[k]) == 1 else ','.join(valDict[k]) if len(valDict[k]) > 1 else 'null'  for k in valDict} # replace array to single value
            valDict = {k:'null' if valDict[k] == '' else valDict[k] for k in valDict} #filter blank value with null
            valueDict = {}
            dataTypeDict = {}
            for k in valDict:
                if k in available_field:
                    valueDict[k] = valDict[k] 
                    dataTypeDict[k] = field_list[k]
            store_data_handler_with_datatype(valueDict, tablename, dataTypeDict = dataTypeDict)
            return True, None
        except Exception as e:
            logger.error("FormBuilderHandle.insertFormDataHandler ->" + str(e))
            return False

    def updateFormDataHandler(definition,valDict, row_id):
        try:
            tablename = definition.table_name
            field_list = definition.field_list
            available_field = list(field_list.keys())
            # valDict = {k:valDict[k][0] if len(valDict[k]) == 1 else ','.join(valDict[k]) if len(valDict[k]) > 1 else 'null'  for k in valDict} # replace array to single value
            # valDict = {k:'null' if valDict[k] == '' else valDict[k] for k in valDict} #filter blank value with null
            # valDict = valDict
            valueDict = {}
            dataTypeDict = {}
            for k in valDict:
                if k in available_field:
                    valueDict[k] = valDict[k] 
                    dataTypeDict[k] = field_list[k]
            update_data_handler_with_datatype(valueDict, tablename,row_id, dataTypeDict = dataTypeDict)
            return True, None
        except Exception as e:
            logger.error("FormBuilderHandle.updateFormDataHandler ->" + str(e))
            return False

    def deleteRecordFromTableHandler(definition):
        try:
            tablename = definition.table_name
            field_list = definition.field_list
            available_field = list(field_list.keys())
            valDict = {k:valDict[k][0] if len(valDict[k]) == 1 else ','.join(valDict[k]) if len(valDict[k]) > 1 else 'null'  for k in valDict} # replace array to single value
            valDict = {k:'null' if valDict[k] == '' else valDict[k] for k in valDict} #filter blank value with null
            valueDict = {}
            dataTypeDict = {}
            for k in valDict:
                if k in available_field:
                    valueDict[k] = valDict[k] 
                    dataTypeDict[k] = field_list[k]
            store_data_handler_with_datatype(valueDict, tablename, dataTypeDict = dataTypeDict)
            return True, None
        except Exception as e:
            logger.error("FormBuilderHandle.deleteRecordFromTableHandler ->" + str(e))
            return False