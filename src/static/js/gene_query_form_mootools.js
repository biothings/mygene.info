// Copyright [2010-2011] [Chunlei Wu]
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


if (typeof MooTools == 'undefined') {
    alert("This widget requires MooTools javascript library!");
}

function mygene_info_gene_query(query){
    var gene_query_url = 'http://mygene.info/query';
    var url = gene_query_url + "?q="+query;
    new Request.JSONP({
        callbackKey: 'jsoncallback',
        url: url,
        onComplete: mygene_info_gene_query_callback
    }).send();
}

function mygene_info_gene_query_callback(result){
    var html = '';
    $("mygene_info_gene_query_result").empty();
    if (Type.isArray(result.rows)){
        html += '<p>Found '+result.total_rows+' matched gene(s).</p>';
        if (result.total_rows > 0){
            html += '<table>';
            result.rows.each(function(gene, i){
                html += "<tr><td>{id}</td><td>{symbol}</td><td>{name}</td></tr>".substitute(gene);
            });
            html += '</table>';
        }
    }
    else {
        var err = result.error || result.reason || "Invalid query!";
        html = '<p>Error:<pre>&nbsp;'+err+'</pre></p>';
    }
    $("mygene_info_gene_query_result").set('html', html);
}

window.addEvent('domready', function() {
    $("mygene_info_gene_query_form").addEvent('submit', function(e){
        e.stop();
        var query = $$("#mygene_info_gene_query_form input[name=query]").get('value')[0];
        if (query){
            $("mygene_info_gene_query_result").empty();
            $("mygene_info_gene_query_result").set('html', '<img src="http://mygene.info/static/img/ajax-loader.gif" style="width:35px;height:35px">');
            mygene_info_gene_query(query);
        }
    });
});
