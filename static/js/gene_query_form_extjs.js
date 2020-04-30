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


if (typeof Ext == 'undefined') {
    alert("This widget requires Ext-core javascript library!");
}

function mygene_info_gene_query(query){
    var gene_query_url = 'http://mygene.info/query';
        Ext.ux.JSONP.request(gene_query_url, {
            callbackKey: 'jsoncallback',
            params: {
                q: query
            },
            callback: mygene_info_gene_query_callback
        });    
}

function mygene_info_gene_query_callback(result){
    //TODO: need error-handling here.
    var el = Ext.fly("mygene_info_gene_query_result");
    el.dom.innerHTML='';
    var html = '';
    if (Ext.isArray(result.rows)){
        html += '<p>Found '+result.total_rows+' matched gene(s).</p>';
        html += '<table>';
        for (var i=0;i<result.rows.length;i++){
            var gene = result.rows[i];
            html += String.format("<tr><td>{0}</td><td>{1}</td><td>{2}</td></tr>",
                                  gene.id,
                                  gene.symbol,
                                  gene.name);
        };
        html += '</table>';
    }
    else {        
        var err = result.error || result.reason || "Invalid query!";
        html = '<p>Error:<pre>&nbsp;'+err+'</pre></p>';
    }    
    el.update(html);
}

Ext.onReady(function() {
    Ext.get('mygene_info_gene_query_form').on('submit', function(ev) {
        ev.preventDefault();
        var query = Ext.DomQuery.selectNode('#mygene_info_gene_query_form input[name=query]').value;
        console.log(query);
        if (query){
            var el = Ext.fly("mygene_info_gene_query_result");
            el.update('<img src="http://mygene.info/static/img/ajax-loader.gif" style="width:35px;height:35px">');                
            mygene_info_gene_query(query);
        }
        return false;
    });
})
 
