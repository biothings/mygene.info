function numberWithCommas(x) {
    return x.toString().replace(/\B(?=(\d{3})+(?!\d))/g, ",");
}

var Releases = {};
var DATA_FORMAT_VERSION = "1.0";

jQuery(document).ready(function() {
    if( jQuery(' .indexed-field-table ').length ) {
        jQuery.ajax({
            url: "http://mygene.info/v3/metadata/fields",
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
    if ((jQuery('#all-releases').length)) {
        // load releases
        jQuery.ajax({
            url: 'http://biothings-releases.s3-website-us-west-2.amazonaws.com/mygene.info/versions.json',
            cache: false,
            type: "GET",
            dataType: "json",
            success: function (data, Status, jqXHR)
            {
                if (data.format == DATA_FORMAT_VERSION) {
                    appendResponses(Releases, data.versions);
                }
                displayReleases();
            }
        });
    }
});

function appendResponses(rel, res) {
    var done = [];
    jQuery.each(res, function (index, val) {
        var t = new Date(val["release_date"].split("T")[0].split('-'));
        if (done.indexOf(val.target_version) == -1) {
            if (!(t in rel)) {rel[t] = [];}    
            rel[t].push(val);
            done.push(val.target_version);
        }
    });
}

function displayReleases() {
    // everything should be loaded and ready to display, first reverse sort all releases by date...
    var releaseDates = Object.keys(Releases);
    releaseDates.sort(function(a,b) {
        return new Date(b) - new Date(a);
    });
    // now compile the html 
    var html = '<p class="release-control-line"><a href="javascript:;" class="release-expand">Expand All</a>|<a href="javascript:;" class="release-collapse">Collapse All</a></p>'
    jQuery.each(releaseDates, function (index, val) {
        var tDate = val.toString().split(" ").slice(1,4); tDate[1] += ","; tDate = tDate.join(" ");
        html += '<div class="release-pane"><p class="release-date">' + tDate + '</p>';
        jQuery.each(Releases[val], function (rIndex, rVal) {
            html += '<div><a href="javascript:;" class="release-link" data-url="' + rVal.url + '">Build version <span class="release-version">' + rVal['target_version'] + '</span></a><div class="release-info"></div></div>';
        });
        html += '</div>'
    });
    // show the html
    jQuery('#all-releases').html(html);
    // attach click handlers for each pop down link
    jQuery('.release-link').click(function () {
        if (!(jQuery(this).siblings('.release-info').hasClass('loaded'))) {
            var that = this;
            jQuery.ajax({
                url: jQuery(this).data().url,
                cache: false,
                type: "GET",
                dataType: "json",
                success: function (ndata, nStatus, njqXHR) {
                    jQuery.ajax({
                        url: ndata.changes.txt.url,
                        cache: false,
                        type: "GET",
                        success: function (edata, eStatus, ejqXHR) {
                            jQuery(that).siblings('.release-info').html('<pre>' + edata + '</pre>');
                            jQuery(that).siblings('.release-info').addClass('loaded');
                            jQuery(that).siblings('.release-info').slideToggle();
                        }
                    });
                }
            });
        }
        else {
            jQuery(this).siblings('.release-info').slideToggle();
        }
    });
    // add expand collapse click handlers
    jQuery('.release-collapse').click(function () {jQuery('.release-info').slideUp();});
    jQuery('.release-expand').click(function () {
        jQuery('.release-info.loaded').slideDown();
        jQuery('.release-info:not(.loaded)').siblings('.release-link').click();
    });
}
