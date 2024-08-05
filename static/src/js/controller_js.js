
odoo.define("crm_portal.FormFunction",[], function (require) {
    "use strict";
    var secteur = $("#secteur");
    var activities = $("#activity");

   $('input[name="has_account"]').change(function() {
        console.log('yes');
        if ($('#has_account_yes').is(':checked')) {
            $('#rib_group').show();
        } else {
            $('#rib_group').hide();
        }
    });
   $('input[name="has_confrere"]').change(function() {
        console.log('yes');
        if ($('#has_confrere_yes').is(':checked')) {
            $('.confrere').show();
        } else {
            $('.confrere').hide();
        }
    });
   $('input[name="has_importation"]').change(function() {
        console.log('yes');
        if ($('#has_importation_yes').is(':checked')) {
            $('.importation').show();
        } else {
            $('.importation').hide();
        }
    });
   $('input[name="has_appro"]').change(function() {
        console.log('yes');
        if ($('#has_appro_yes').is(':checked')) {
            $('.appro').show();
        } else {
            $('.appro').hide();
        }
    });
   $('#createconfrere').click(() =>{
   alert('clicked!!!!!!!!!')
   })
   secteur.change(()=> {
        console.log(secteur.val());
        activities.find('option')
                .remove()
                .end()
        $.ajax({
            url: "/credit-request/getActivities",
            type: 'GET',
            data : {
                'secteur_id' :secteur.val()
            },
            dataType: 'json', //added data type
            success: function(res) {
                console.log(res);
                var items = JSON.stringify(res);
                var items_parsed = JSON.parse(items);
                for (var key in items_parsed) {
                    activities.append($('<option>', {
                        value: key,
                        text : items_parsed[key]
                    }));
                }},
            error : function(e){
                console.log(e)
                }
            });
        });
})
