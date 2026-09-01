function numberWithCommas(x) {
    return x.toString().replace(/\B(?=(\d{3})+(?!\d))/g, ",");
}

var Releases = {};
var ReleaseYears = [];
var ReleaseDatesByYear = {};
var ALL_YEARS = "all";
var DATA_FORMAT_VERSION = "1.0";

jQuery(document).ready(function () {
    if (jQuery(' .indexed-field-table ').length) {
        jQuery.ajax({
            url: "//mygene.info/v3/metadata/fields",
            dataType: "json",
            type: "GET",
            success: function (data) {
                jQuery.each(data, function (field, d) {
                    var notes = indexed = '&nbsp;';
                    if (d.notes) { notes = d.notes; }
                    if (d.indexed) { indexed = '&#x2714'; }
                    jQuery('.indexed-field-table > tbody:last').append('<tr><td>' + field + '</td><td>' + indexed + '</td><td><span class="italic">' + d.type + '</span></td><td>' + notes + '</td>');
                });
                jQuery('.indexed-field-table').DataTable({
                    "iDisplayLength": 50,
                    "lengthMenu": [[10, 25, 50, 100, -1], [10, 25, 50, 100, "All"]],
                    "columns": [
                        { "width": "290px" },
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
            url: 'https://s3-us-west-2.amazonaws.com/biothings-releases/mygene.info/versions.json',
            cache: false,
            type: "GET",
            dataType: "json",
            success: function (data, Status, jqXHR) {
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
            if (!(t in rel)) { rel[t] = []; }
            rel[t].push(val);
            done.push(val.target_version);
        }
    });
}

function displayReleases() {
    // everything should be loaded and ready to display, first reverse sort all releases by date...
    var releaseDates = Object.keys(Releases);
    releaseDates.sort(function (a, b) {
        return new Date(b) - new Date(a);
    });

    // bucket the sorted dates into years, newest first, so the page can render one
    // year at a time rather than every release ever built
    ReleaseYears = [];
    ReleaseDatesByYear = {};
    jQuery.each(releaseDates, function (index, dateKey) {
        var year = anchorFor(dateKey).slice(0, 4);
        if (!ReleaseDatesByYear[year]) {
            ReleaseDatesByYear[year] = [];
            ReleaseYears.push(year);
        }
        ReleaseDatesByYear[year].push(dateKey);
    });

    if (!ReleaseYears.length) {
        jQuery('#all-releases').html('<p class="loading">No release data available.</p>');
        return;
    }

    jQuery('#all-releases').html(`
        <p class="release-control-line">
            <a href="javascript:;" class="release-expand">Expand All</a>|
            <a href="javascript:;" class="release-collapse">Collapse All</a>
        </p>
        <p class="release-years"></p>
        <div id="release-list"></div>`)

    // year strip, newest first, with an "All" escape hatch at the end
    jQuery.each(ReleaseYears.concat([ALL_YEARS]), function (index, year) {
        jQuery('.release-years').append($('<a>', {
            "href": "javascript:;",
            "class": "release-year",
            "data-year": year,
            "text": year === ALL_YEARS ? "All" : year
        }));
    });

    // handlers are delegated from #all-releases so they survive re-rendering a year
    jQuery('#all-releases').on('click', '.release-year', function () {
        renderYear(jQuery(this).attr('data-year'));
    });

    // attach click handlers for each pop down link
    jQuery('#all-releases').on('click', '.release-link', function () {
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
    jQuery('#all-releases').on('click', '.release-collapse', function () { jQuery('.release-info').slideUp(); });
    jQuery('#all-releases').on('click', '.release-expand', function () {
        jQuery('.release-info.loaded').slideDown();
        jQuery('.release-info:not(.loaded)').siblings('.release-link').click();
    });

    // a permalink pasted in later still has to be able to switch years
    jQuery(window).on('hashchange', goToHash);

    renderYear(yearForHash(window.location.hash) || ReleaseYears[0]);
    goToHash();
}

// The YYYYMMDD anchor for a release date. Year grouping keys off this same string
// so a #20240115 permalink always resolves to the bucket that actually holds it.
function anchorFor(dateKey) {
    return new Date(dateKey).toISOString().substr(0, 10).replace(/-/g, '');
}

// Year a #YYYYMMDD permalink belongs to, or null if the hash isn't one of ours.
function yearForHash(hash) {
    var match = /^#?(\d{4})\d{4}$/.exec(hash || '');
    return (match && ReleaseDatesByYear[match[1]]) ? match[1] : null;
}

function renderYear(year) {
    jQuery('.release-year').removeClass('active');
    jQuery('.release-year[data-year="' + year + '"]').addClass('active');

    var shown = (year === ALL_YEARS) ? ReleaseYears : [year];
    var $list = jQuery('#release-list').empty();
    jQuery.each(shown, function (index, val) {
        jQuery.each(ReleaseDatesByYear[val] || [], function (dIndex, dateKey) {
            $list.append(buildReleasePane(dateKey));
        });
    });
}

function buildReleasePane(dateKey) {
    var rDate = new Date(dateKey)
    var tDate = rDate.toDateString().slice(4)
    var hDate = anchorFor(dateKey)

    var $release = $('<div>', {
        class: "release-pane",
        id: hDate,
    })
        .append($('<h4>', {
            class: "release-date",
            text: tDate
        })
            .append($('<a>', {
                class: "headerlink",
                href: "#" + hDate,
                title: "Permalink to this release",
                text: '\u00b6'
            })))

    jQuery.each(Releases[dateKey], function (rIndex, rVal) {
        $release.append($('<div>')
            .append($('<a>', {
                "href": "javascript:;",
                "class": "release-link",
                "data-url": rVal.url,
                "text": 'Build version '
            })
                .append($('<span>', {
                    class: "release-version",
                    html: rVal['target_version']
                }))
            ).append($('<div>', {
                class: "release-info"
            })))
    })

    return $release;
}

// Jump to a permalink, switching to its year first if that release isn't rendered.
function goToHash() {
    var id = (window.location.hash || '').slice(1);
    if (!id) { return; }
    if (!document.getElementById(id)) {
        var year = yearForHash(window.location.hash);
        if (!year) { return; }
        renderYear(year);
    }
    var target = document.getElementById(id);
    if (target) {
        target.scrollIntoView();
        jQuery(target).children("div").children("a.release-link").click();
    }
}
