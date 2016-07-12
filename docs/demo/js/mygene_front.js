var theseFields = [];
var serverAddress = 'mygene.info';
var apiVersion = 'v3';

function split( val ) {
    return val.split( /,\s*/ );
}

function extractLast( term ) {
    return split( term ).pop();
}

function endsWith(str, suffix) {
    return str.indexOf(suffix, str.length - suffix.length) !== -1;
}

function successHandler(data, textStatus, jqXHR, searchURL) {
    jQuery('.introduction').hide();
    jQuery('.json-panel button').remove();
    jQuery('.json-panel').remove();
    jQuery('.json-view').remove();
    if(searchURL) {
        jQuery('.results').html("<div class='json-panel'><p id='total-text'></p><button id='expand-json'>Expand</button><button id='collapse-json'>Collapse</button><a href='" + searchURL + "' target='_blank'>" + searchURL + "</a></div><div class='json-view'></div>").show();
    }
    else { 
        jQuery('.results').html("<div class='json-panel'><p id='total-text'></p><button id='expand-json'>Expand</button><button id='collapse-json'>Collapse</button></div><div class='json-view'></div>").show();
    }
    jQuery('.json-panel button').button();
    jQuery('.json-view').JSONView(data); //, {collapsed: true});
    jQuery('.json-view').JSONView('expand');
    jQuery('#expand-json').click(function() {jQuery('.json-view').JSONView('expand');});
    jQuery('#collapse-json').click(function() {jQuery('.json-view').JSONView('collapse');});
    if('total' in data) {
        jQuery('#total-text').html(data['total'] + " total result(s).  Showing top " + data["hits"].length + " result(s).").show();
    }
}

function errorHandler(message, m_class) {
    jQuery('.introduction').hide();
    jQuery('.json-panel button').remove();
    jQuery('.json-panel').remove();
    jQuery('.json-view').remove();
    jQuery('.results').html("<p class='" + m_class + "'>" + message + "</p>").show();
}

jQuery(document).ready(function() {
    // Get the available fields
    jQuery.get('https://' + serverAddress + '/metadata/fields').done(
        function(data) {
            // success, get the fields
            jQuery.each(data, function(key, value) {theseFields.push(key)});
            jQuery( "#fields-input" )
              // don't navigate away from the field on tab when selecting an item
              .bind( "keydown", function( event ) {
                if ( event.keyCode === jQuery.ui.keyCode.TAB &&
                    $( this ).autocomplete( "instance" ).menu.active ) {
                  event.preventDefault();
                }
              })
              .autocomplete({
                minLength: 2,
                source: function( request, response ) {
                  // delegate back to autocomplete, but extract the last term
                  response( jQuery.ui.autocomplete.filter(
                    theseFields, extractLast( request.term ) ) );
                },
                focus: function() {
                  // prevent value inserted on focus
                  return false;
                },
                select: function( event, ui ) {
                  var terms = split( this.value );
                  // remove the current input
                  terms.pop();
                  // add the selected item
                  terms.push( ui.item.value );
                  // add placeholder to get the comma-and-space at the end
                  terms.push( "" );
                  this.value = terms.join( ", " );
                  return false;
                }
              });
        }
    ).fail(
        function() {
            // couldn't get fields
            console.log("Error getting available fields.");
        }
    );

    // gene examples
    jQuery('.gene-example a').click(function() {
        if(jQuery(this).data().example == "1") {
            jQuery("#main-input").val("1017");
            jQuery("#fields-input").val("");
        }
        else if(jQuery(this).data().example == "2") { 
            jQuery("#main-input").val("ENSG00000123374");
            jQuery("#fields-input").val("");
        }
        else if(jQuery(this).data().example == "3") { 
        }
    });

    // query examples
    jQuery('.query-example a').click(function() {
        if(jQuery(this).data().example == "1") { 
            jQuery("#main-input").val("symbol:cdk?");
            jQuery("#fields-input").val("symbol, ensembl.gene");
            jQuery("#size-input").val("50").selectmenu('refresh', true);
        }
        else if(jQuery(this).data().example == "2") { 
            jQuery('#main-input').val("tumor AND suppressor");
            jQuery("#fields-input").val("");
            jQuery("#size-input").val("10").selectmenu('refresh', true);
        }
        else if(jQuery(this).data().example == "3") { 
            jQuery('#main-input').val("uniprot:P24941");
            jQuery("#fields-input").val("");
            jQuery("#size-input").val("10").selectmenu('refresh', true);
        }
        else if(jQuery(this).data().example == "help") { 
            
        }
    });

    // Make this a button
    jQuery('#search-button').button().click(function() {
        // Search button click handler
        var searchType = jQuery('#search-type').val();
        var endpointBase = 'https://' + serverAddress + '/' + apiVersion;
        var queryText = jQuery('#main-input').val();
        var fieldsText = jQuery('#fields-input').val();
        if(!(fieldsText)) {fieldsText = 'all';}
        if(endsWith(fieldsText, ', ')) {fieldsText = fieldsText.substring(0, fieldsText.length - 2);}
        if(endsWith(fieldsText, ',')) {fieldsText = fieldsText.substring(0, fieldsText.length - 1);}
        var searchURL = '';
        var getURL = '';
        if(searchType == 1) {
            // HGVS ID query
            errorHandler("Query executing . . .", "executing");
            if(queryText.indexOf(",") == -1) {
                // get to gene endpoint
                getURL = endpointBase + '/gene/' + encodeURIComponent(queryText) + '?fields=' + encodeURIComponent(fieldsText);
                searchURL = decodeURIComponent(getURL);
                jQuery.get(getURL).done(function(data, textStatus, jqXHR) {successHandler(data, textStatus, jqXHR, searchURL);}).fail(function(jqXHR, statusText, errorThrown) {errorHandler("Couldn't retrieve annotation " + jQuery('#main-input').val() + ".  ", "error");});
            }
            else {
                // post to gene endpoint
                jQuery.post(endpointBase + '/gene', {'ids': queryText, 'fields': fieldsText}).done(function(data, textStatus, jqXHR) {successHandler(data, textStatus, jqXHR, searchURL);}).fail(function(jqXHR, statusText, errorThrown) {errorHandler("Error retrieving annotations.", "error");});
            }
        }
        else if(searchType == 2) {
            var querySize = jQuery('#size-input').val();
            // Full text query
            errorHandler("Query executing . . .", "executing");
            getURL = endpointBase + '/query?q=' + encodeURIComponent(queryText) + '&fields=' + encodeURIComponent(fieldsText) + '&size=' + querySize;
            searchURL = decodeURIComponent(getURL);
            jQuery.get(getURL).done(function(data, textStatus, jqXHR) {successHandler(data, textStatus, jqXHR, searchURL);}).fail(function(jqXHR, statusText, errorThrown) {errorHandler("Couldn't retrieve results for query " + jQuery('#main-input').val() + ".", "error");});
        }
        else if(searchType == 3) {
            // metadata query
            errorHandler("Query executing . . .", "executing");
            getURL = endpointBase + '/metadata';
            searchURL = decodeURIComponent(getURL);
            jQuery.get(getURL).done(function(data, textStatus, jqXHR) {successHandler(data, textStatus, jqXHR, searchURL);}).fail(function(jqXHR, statusText, errorThrown) {errorHandler("Couldn't retrieve MyGene database metadata.  API error.", "error");});
        }
        else if(searchType == 4) {
            // available fields query
            errorHandler("Query executing . . .", "executing");
            getURL = endpointBase + '/metadata/fields';
            searchURL = decodeURIComponent(getURL);
            jQuery.get(getURL).done(function(data, textStatus, jqXHR) {successHandler(data, textStatus, jqXHR, searchURL);}).fail(function(jqXHR, statusText, errorThrown) {errorHandler("Couldn't retrieve available fields.  API error.", "error");});
        }
    });
    // Select menu is a widget
    jQuery('#size-input').selectmenu();

    // Make this a select menu widget
    jQuery('#search-type').selectmenu({
        change: function() {
            if(jQuery(this).val() == 1) {
                // Query by gene ID
                jQuery('#main-input').val("");
                jQuery('#main-input').attr('placeholder', 'Enter comma separated Entrez or Ensembl gene ids here');
                jQuery('#main-input').prop('disabled', false);
                jQuery("#fields-input").prop('disabled', false);
                jQuery("#size-input-button").hide();
                jQuery("label[for='size-input-button']").hide();
                jQuery(".examples").hide();
                jQuery(".gene-example").show();
            }
            else if(jQuery(this).val() == 2) {
                jQuery('#main-input').val("");
                jQuery('#main-input').attr('placeholder', 'Enter query here');
                jQuery('#main-input').prop('disabled', false);
                jQuery("#fields-input").prop('disabled', false);
                jQuery("#size-input-button").show();
                jQuery("label[for='size-input-button']").show();
                jQuery(".examples").hide();
                jQuery(".query-example").show();
            }
            else if(jQuery(this).val() == 3) {
                jQuery('#main-input').val("");
                jQuery('#fields-input').val("");
                jQuery('#main-input').attr('placeholder', 'No input accepted');
                jQuery('#main-input').prop('disabled', true);
                jQuery("#fields-input").prop('disabled', true);
                jQuery("#size-input-button").hide();
                jQuery("label[for='size-input-button']").hide();
                jQuery(".examples").hide();
                jQuery(".filler").show();
            }
            else if(jQuery(this).val() == 4) {
                jQuery('#main-input').val("");
                jQuery('#fields-input').val("");
                jQuery('#main-input').attr('placeholder', 'No input accepted');
                jQuery('#main-input').prop('disabled', true);
                jQuery("#fields-input").prop('disabled', true);
                jQuery("#size-input-button").hide();
                jQuery("label[for='size-input-button']").hide();
                jQuery(".examples").hide();
                jQuery(".filler").show();
            }
        }
    });
});
