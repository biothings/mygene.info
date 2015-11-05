jQuery(document).ready(function() {
    if( jQuery(' .indexed-field-table ').length ) {
        jQuery.ajax({
            url: "http://mygene.info/v2/metadata/fields",
            dataType: "JSONP",
            jsonpCallback: "callback",
            type: "GET",
            success: function(data) {
                jQuery.each(data, function(field, d) {
                    var notes = indexed = '&nbsp;';
                    if(d.notes) {notes=d.notes;}
                    if(d.indexed) {indexed='&#x2714';}
                    jQuery('.indexed-field-table > tbody:last').append('<tr><td>' + field + '</td><td>' + indexed + '</td><td><span class="italic">' + d.type + '</span></td><td>' + notes + '</td>');
                });
                jQuery('.indexed-field-table').DataTable({
                    "iDisplayLength": 50,
                    "lengthMenu": [[10, 25, 50, 100, -1], [10, 25, 50, 100, "All"]],
                    "columns": [
                        {"width":"290px"},
                        null,
                        null,
                        null
                    ],
                    "autoWidth": false,
                    "dom": "flrtip"
                });
            }
        });
    }
});
