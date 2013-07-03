// Copyright [2013-2014] [Chunlei Wu]
//
// Licensed under the Apache License, Version 2.0 (the "License");
// you may not use this file except in compliance with the License.
// You may obtain a copy of the License at
//
//    http://www.apache.org/licenses/LICENSE-2.0
//
// Unless required by applicable law or agreed to in writing, software
// distributed under the License is distributed on an "AS IS" BASIS,
// WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
// See the License for the specific language governing permissions and
// limitations under the License.


function mygene_info_gene_query(query){
    var gene_query_url = 'http://mygene.info/v2/query';
    var url = gene_query_url + "?species=mouse&limit=100&callback=?&q="+query;
    $.getJSON(url, mygene_info_gene_query_callback);
}

function mygene_info_gene_query_callback(result){
    var html;
    $("#mygene_info_gene_query_result").empty();
    if ($.isArray(result.hits)){
        html = '<p>Found '+result.total+' matched mouse gene(s).</p>';
        if (result.total > 0){
            html += '<table>';
            $.each(result.hits, function(i, gene){
                html += '<tr><td><a href="javascript:showgene(\'' + gene._id + '\');">' + gene.symbol + '</a></td><td>'+ gene.name + '</td></tr>';
            });
            html += '</table>';
        }
    }
    else {
        var err = result.error || result.reason || "Invalid query!";
        html = '<p>Error:<pre>&nbsp;'+err+'</pre></p>';
    }

    $("#mygene_info_gene_query_result").append(html);
}

function showgene(geneid){
    var gene_url = 'http://mygene.info/v2/gene/'+geneid+'?fields=reporter&callback=?';
    show_loading("#mygene_info_gene_datachart");
    $.getJSON(gene_url, mygene_info_get_gene_callback);
}

function mygene_info_get_gene_callback(result){
    $("#mygene_info_gene_datachart").empty();
    if (result && result.reporter && result.reporter['Mouse430_2']){
        var ps_list = result.reporter['Mouse430_2'];
        if (!$.isArray(ps_list)){
            ps_list = [ps_list];
        }
        $.each(ps_list, function(i, ps){
            $("#mygene_info_gene_datachart").append('<img src="http://biogps.org/dataset/4/chart/'+ps+'" />');
        });
    }
    else {
        $("#mygene_info_gene_datachart").append('<p>No data available for this gene.</p>');
    }
}

function show_loading(el){
  $(el).empty();
  $(el).append('<img src="http://mygene.info/static/img/ajax-loader.gif" style="width:35px;height:35px">');
}

$(document).ready(function(){
 $("#mygene_info_gene_query_form").submit(function(){
  var query = $("#mygene_info_gene_query_form input[name=query]").val();
  if (query) {
    mygene_info_gene_query(query);
    show_loading("#mygene_info_gene_query_result");
  }
  return false;
 });
});
