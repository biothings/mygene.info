/*! jquery.ui.genequery_autocomplete.js
 *  A JQuery UI widget for gene query autocomplete
 *  This autocomplete widget for gene query provides suggestions while you type a gene
 *  symbol or name into the field. By default the gene suggestions are displayed as
 *  "<Symbol>:<Name>", automatically triggered when at least two characters are entered
 *  into the field.
 *  Copyright (c) 2012 Chunlei Wu; Apache License, Version 2.0.
 */


//Ref: http://stackoverflow.com/questions/1038746/equivalent-of-string-format-in-jquery
//Example usage: alert("Hello {name}".format({ name: 'World' }));
String.prototype.format = function (args) {
    var newStr = this;
    for (var key in args) {
        var regex = new RegExp('{'+key+'}', "igm");
        newStr = newStr.replace(regex, args[key]);
    }
    return newStr;
};

//Subclass default jQuery UI autocomplete widget
//Ref: http://stackoverflow.com/questions/5218300/how-do-subclass-a-widget
//Ref: https://gist.github.com/962848
$.widget("my.genequery_autocomplete", $.ui.autocomplete, {

	options: {
        mygene_url: 'http://mygene.info/query',
        //exact match with symbol is boosted.
        q: "(symbol:{term} OR symbol: {term}* OR name:{term}* OR summary:{term}*) AND species:human",
        sort:'_score,_id',
        limit:20,
        gene_label: "{symbol}: {name}",
        value_attr: 'symbol',
        return_attrs: ["symbol", "name"],
        minLength: 2,
        include_docs: false
	},

	_create: function() {
		//this._super("_create");
        $.ui.autocomplete.prototype._create.call(this);
		var self = this;
        var _options = self.options;

        this.source = function( request, response ) {
                $.ajax({
                    url: _options.mygene_url,
                    dataType: "jsonp",
                    jsonp: 'jsoncallback',
                    data: {
                        q: _options.q.format({term:request.term}),
                        sort:_options.sort,
                        limit:_options.limit,
                        include_docs: _options.include_docs,
                    },
                    success: function( data ) {
                        if (data.total_rows > 0){
                            response( $.map( data.rows, function( item ) {
                                var obj = {
                                    label: _options.gene_label.format(item),
                                    id: item.id,
                                    value: item[_options.value_attr]
                                }

                                $.map(_options.return_attrs, function(attr){
                                    var gene_doc = item.doc || item;
                                    if (gene_doc[attr]) obj[attr]=gene_doc[attr];
                                });
                                return obj;
                            }));
                        }else{
                            response([{label:'no matched gene found.', value:''}]);
                        }
                    }
                });
            };

        //set default title attribute if not set already.
        if (this.element.attr("title") === undefined){
            this.element.attr("title", 'Powered by mygene.info');
        }
        //set default select callback if not provided.
        _options.select = _options.select || this._default_select_callback;

        //set default loading icon
        this._add_css('.ui-autocomplete-loading { background: white url("'+this._url_root+'img/ui-anim_basic_16x16.gif") right center no-repeat; }');

	},

    _url_root : 'http://mygene.info/widget/autocomplete/',

    //helper function for adding custom css style.
    _add_css : function(cssCode) {
        var styleElement = document.createElement("style");
        styleElement.type = "text/css";
        if (styleElement.styleSheet) {
        styleElement.styleSheet.cssText = cssCode;
        } else {
        styleElement.appendChild(document.createTextNode(cssCode));
        }
        document.getElementsByTagName("head")[0].appendChild(styleElement);
    },

    _default_select_callback: function(event, ui) {
                alert( ui.item ?
                    "Selected: " + ui.item.label + '('+ui.item.id+')':
                    "Nothing selected, input was " + this.value);
    }

});
