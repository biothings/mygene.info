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


if (typeof jQuery == 'undefined') {
    alert("This widget requires JQuery javascript library!");
}

function mygene_info_gene_query(query){
    var gene_query_url = 'http://mygene.info/query';
    var url = gene_query_url + "?jsoncallback=?&q="+query;
    $.getJSON(url, mygene_info_gene_query_callback);
}

function mygene_info_gene_query_callback(result){
    var html='';
    $("#mygene_info_gene_query_result").empty();
    if ($.isArray(result.rows)){
        html += '<p>Found '+result.total_rows+' matched gene(s).</p>';
        if (result.total_rows > 0){
            html += '<table>';
            $.each(result.rows, function(i, gene){
                html += $.format("<tr><td>{0}</td><td>{1}</td><td>{2}</td></tr>",
                                 gene.id,
                                 gene.symbol,
                                 gene.name);
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

$(document).ready(function(){
 $("#mygene_info_gene_query_form").submit(function(){
  var query = $("#mygene_info_gene_query_form input[name=query]").val();
  if (query){
    $("#mygene_info_gene_query_result").empty();
    $("#mygene_info_gene_query_result").append('<img src="http://mygene.info/static/img/ajax-loader.gif" style="width:35px;height:35px">');
    mygene_info_gene_query(query);
  }
  return false;
 });

});


/*
The following jquery plugin (adds $.format) is taken from:
http://plugins.jquery.com/files/jquery-dotnet_string_formatting-1.0.0.js.txt
*/

/*
The MIT License

Copyright (c) 2002, 2009 Michael D. Hall (aka just3ws)

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in
all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
THE SOFTWARE.
*/

/*

  var result = $.format("Hello, {0}.", "world");
  //result -> "Hello, world."

*/

jQuery.format = function jQuery_dotnet_string_format(text) {
  //check if there are two arguments in the arguments list
  if (arguments.length <= 1) {
    //if there are not 2 or more arguments there's nothing to replace
    //just return the text
    return text;
  }
  //decrement to move to the second argument in the array
  var tokenCount = arguments.length - 2;
  for (var token = 0; token <= tokenCount; ++token) {
    //iterate through the tokens and replace their placeholders from the text in order
    text = text.replace(new RegExp("\\{" + token + "\\}", "gi"), arguments[token + 1]);
  }
  return text;
};
