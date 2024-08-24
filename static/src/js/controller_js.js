
odoo.define("crm_portal.FormFunction",[], function (require) {
    "use strict";
    var secteur = $("#secteur");
    var activities = $("#activity");
        window.onbeforeunload = function() {
            console.log('yes it does');
            history.replaceState(null, null, window.location.pathname + '#scroll=' + window.scrollY);
        };

    // Restaurer la position de scroll après le rafraîchissement
    window.onload = function() {
        console.log('yes it does again');
        var scrollY = window.location.hash.replace('#scroll=', '');
        if (scrollY) {
            window.scrollTo(0, parseInt(scrollY, 10));
        }
    };
    $('input[name="has_account"]').change(function() {
        var hasAccount = false;
        if ($('#has_account_yes').is(':checked')) {
            $('#rib_group').show();
            hasAccount = true
        } else {
            $('#rib_group').hide();
            hasAccount = false
        }
        $.ajax({
            url: "/credit-request/hasAccount",
            type: 'GET',
            data : {
                'hasAccount' : hasAccount,
                'opportunity_id' :$('input[name="opportunity_id"]').val()
            },
            dataType: 'json', //added data type
            success: function(res) {
                console.log(res);
                },
            error : function(e){
                console.log(e)
                }
            });
    });
    var csrfToken = $('input[name="csrf_token"]').val();
    $('input[name="has_confrere"]').change(function() {
        console.log('yes');
        var hasConfrere = false;
        if ($('#has_confrere_yes').is(':checked')) {
            $('.confrere').show();
            hasConfrere = true
        } else {
            $('.confrere').hide();
            hasConfrere = false
        }
        $.ajax({
            url: "/credit-request/hasConfrere",
            type: 'GET',
            data : {
                'hasConfrere' : hasConfrere,
                'opportunity_id' :$('input[name="opportunity_id"]').val()
            },
            dataType: 'json', //added data type
            success: function(res) {
                console.log(res);
                },
            error : function(e){
                console.log(e)
                }
            });
    });
    $('input[name="has_importation"]').change(function() {
        var hasImportation = false;
        if ($('#has_importation_yes').is(':checked')) {
            $('.importation').show();
            hasImportation = true
        } else {
            $('.importation').hide();
            hasImportation = false
        }
        $.ajax({
            url: "/credit-request/hasImportation",
            type: 'GET',
            data : {
                'hasImportation' : hasImportation,
                'opportunity_id' :$('input[name="opportunity_id"]').val()
            },
            dataType: 'json', //added data type
            success: function(res) {
                console.log(res);
                },
            error : function(e){
                console.log(e)
                }
            });
    });
    $('input[name="has_appro"]').change(function() {
        var hasAppro = false;
        if ($('#has_appro_yes').is(':checked')) {
            $('.appro').show();
            hasAppro = true;
        } else {
            $('.appro').hide();
            hasAppro = false;
        }
        $.ajax({
            url: "/credit-request/hasAppro",
            type: 'GET',
            data : {
                'hasAppro' : hasAppro,
                'opportunity_id' :$('input[name="opportunity_id"]').val()
            },
            dataType: 'json', //added data type
            success: function(res) {
                console.log(res);
                },
            error : function(e){
                console.log(e)
                }
            });
    });

    $('input[name="num_compte"]').change(function() {
        console.log('num_compte changed');
        $.ajax({
            url: "/credit-request/numcompteChanged",
            type: 'GET',
            data : {
                'num_compte' :$('input[name="num_compte"]').val(),
                'opportunity_id' :$('input[name="opportunity_id"]').val()
            },
            dataType: 'json', //added data type
            success: function(res) {
                console.log(res);
                },
            error : function(e){
                console.log(e)
                }
            });
    });

    $('textarea[name="company_description"]').change(function() {
        console.log('company_description changed');
        $.ajax({
            url: "/credit-request/companydescriptionChanged",
            type: 'GET',
            data : {
                'company_description' :$('textarea[name="company_description"]').val(),
                'opportunity_id' :$('input[name="opportunity_id"]').val()
            },
            dataType: 'json', //added data type
            success: function(res) {
                console.log(res);
                },
            error : function(e){
                console.log(e)
                }
            });
    });
   $('textarea[name="garanties"]').change(function() {
        console.log('garanties changed');
        $.ajax({
            url: "/credit-request/garantiesChanged",
            type: 'GET',
            data : {
                'garanties' :$('textarea[name="garanties"]').val(),
                'opportunity_id' :$('input[name="opportunity_id"]').val()
            },
            dataType: 'json', //added data type
            success: function(res) {
                console.log(res);
                },
            error : function(e){
                console.log(e)
                }
            });
    });

   $('input[name="nbr_employees"]').change(function() {
        console.log('nbr_employees changed');
        $.ajax({
            url: "/credit-request/nbremployeesChanged",
            type: 'GET',
            data : {
                'nbr_employees' :$('input[name="nbr_employees"]').val(),
                'opportunity_id' :$('input[name="opportunity_id"]').val()
            },
            dataType: 'json', //added data type
            success: function(res) {
                console.log(res);
                },
            error : function(e){
                console.log(e)
                }
            });
    });
   $('input[name="date_debut"]').change(function() {
        console.log('date_debut changed');
        $.ajax({
            url: "/credit-request/datedebutChanged",
            type: 'GET',
            data : {
                'date_debut' :$('input[name="date_debut"]').val(),
                'opportunity_id' :$('input[name="opportunity_id"]').val()
            },
            dataType: 'json', //added data type
            success: function(res) {
                console.log(res);
                },
            error : function(e){
                console.log(e)
                }
            });
    });

   $('#branch').change(function() {
        console.log('branch changed');
        $.ajax({
            url: "/credit-request/branchChanged",
            type: 'GET',
            data : {
                'branch' :$('#branch').val(),
                'opportunity_id' :$('input[name="opportunity_id"]').val()
            },
            dataType: 'json', //added data type
            success: function(res) {
                console.log(res);
                },
            error : function(e){
                console.log(e)
                }
            });
    });

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
