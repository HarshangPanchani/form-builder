window.setTimeout(function() {
    $(".alert").fadeTo(500, 0).slideUp(500, function(){
        $(this).remove(); 
    });
}, 4000);


$(document).ready( function() {
        
    $('.preview_class').hide()
})
// function change_form_type() {
//     var form_type = $('#id_form_type').val();
//     if (form_type == 'wizard') {
//         $('.wizard_field').show();
//         $('#id_wizard_level,#id_wizard_level_name').attr('required',true);
//     } 
//     else {
//         $('.wizard_field').hide();
//         $('#id_wizard_level,#id_wizard_level_name').attr('required',false);
//     }
// } 
function check() 
{
    var json_file=document.getElementById('schema_file')
        .addEventListener('change', function() 
        {
          
            var fr=new FileReader();
            fr.onload=function(){
                document.getElementById('id_params')
                        .textContent=fr.result;
        }
        
        fr.readAsText(this.files[0]);
    })
}
//  function change_cron() {
//     var cron_type = $('#id_cr_pattern').val();
    
//     if (cron_type == 'custom') {
//         $('.crn').show();
//     } else {
//         $('#id_cron_pattern').val(cron_type);
//         $('.crn').hide();
//     }
// }
// function change_sync() {
//     var sync_type = $('#id_data_sync').val();
//     if (sync_type == 'true') {
//         $('.data_sync_type_field,.att_sync_f').show();
//         $('#id_data_sync_type').attr('required',true);
//     } else {
//         $('.data_sync_type_field,.att_sync_f').hide();
//         $('#id_data_sync_type').attr('required',false);
//         $("#id_data_sync_type").val("");
//         $('#id_attribute_sync').val("False")
//     }
//     change_sync_type();
//     change_attribute_type();
// }

// function change_sync_type() {
//     var dst = $('#id_data_sync_type').val();
//     $('.token_field').show();
   
//     if (dst == 'mqtt') {

//         $('.mqtt_pub_topic_field').show();
//         $('#id_mqtt_topic').attr('required',true);

//     } else if (dst == 'http') {
//         $('.mqtt_pub_topic_field').hide();
//         $('#id_mqtt_topic').attr('required',false);
//         $('#id_mqtt_topic').val('');
//     } else {
        
//         $('.mqtt_pub_topic_field, .token_field').hide();
//         $('#id_mqtt_topic, #id_access_token').attr('required',false);
        
//     }
    
// }
// function change_attribute_type(){
//     var att_sync = $('#id_attribute_sync').val();
//     if (att_sync=='True') {
//         $('.attribute_sync_field').show();
//         $('#id_attribute_sync_interval').attr('required',true);
//     } else {
//         $('.attribute_sync_field').hide();
//         $('#id_attribute_sync_interval').attr('required',false);
//     }

// } 


$(document).on('click', '#form_preview_btn', function(){ 

    $('.preview_class').show()
    $('#field').empty();
    var properties = JSON.parse(document.getElementById('id_schema').value);

    var options = { 
        "theme": "bootstrap4",
        "schema": {
            "title": properties['title'],
            "type": "object",
            "id": "schema",     
            "options": {
                "disable_edit_json": true,
                "disable_properties": true,
                "disable_collapse":true,
                "no_additional_properties":true,
                "object_layout":"grid",
                "ordered": false,
            },
            "properties": properties['properties'],
            "required": properties['required']
        }
    }
    var element = document.getElementById('field');
    var editor = new JSONEditor(element, options);
});


window.setTimeout(function() {
    $(".alert").fadeTo(500, 0).slideUp(500, function(){
        $(this).remove(); 
    });
}, 5000);


$(document).ready(function() {
    $('#addMappingBtn').click(function() {
        $('#mappingModal').modal('show');
    });

    $('#saveMappingBtn').click(function() {
        var fieldA = $('#fieldA').val();
        var fieldB = $('#fieldB').val();
        var fieldC = $('#fieldC').val();

        var newRow = '<tr>' +
            '<td>' + fieldA + '</td>' +
            '<td>' + fieldB + '</td>' +
            '<td>' + fieldC + '</td>' +
            '</tr>';

        $('#Check tbody').append(newRow);
        $('#mappingModal').modal('hide');

        // Clear input fields after adding row
        $('#fieldA').val('');
        $('#fieldB').val('');
        $('#fieldC').val('');
    });
});