/** XHConn - Simple XMLHTTP Interface - bfults@gmail.com - 2005-04-08        **
 ** Code licensed under Creative Commons Attribution-ShareAlike License      **
 ** http://creativecommons.org/licenses/by-sa/2.0/                           **/
//http://xkr.us/code/javascript/XHConn/XHConn.js
function XHConn()
{
  var xmlhttp, bComplete = false;
  try { xmlhttp = new ActiveXObject("Msxml2.XMLHTTP"); }
  catch (e) { try { xmlhttp = new ActiveXObject("Microsoft.XMLHTTP"); }
  catch (e) { try { xmlhttp = new XMLHttpRequest(); }
  catch (e) { xmlhttp = false; }}}
  if (!xmlhttp) return null;
  this.connect = function(sURL, sMethod, sVars, fnDone)
  {
    if (!xmlhttp) return false;
    bComplete = false;
    sMethod = sMethod.toUpperCase();

    try {
      if (sMethod == "GET")
      {
        xmlhttp.open(sMethod, sURL+"?"+sVars, true);
        sVars = "";
      }
      else
      {
        xmlhttp.open(sMethod, sURL, true);
        xmlhttp.setRequestHeader("Method", "POST "+sURL+" HTTP/1.1");
        xmlhttp.setRequestHeader("Content-Type",
          "application/x-www-form-urlencoded");
      }
      xmlhttp.onreadystatechange = function(){
        if (xmlhttp.readyState == 4 && !bComplete)
        {
          bComplete = true;
          fnDone(xmlhttp);
        }};
      xmlhttp.send(sVars);
    }
    catch(z) { return false; }
    return true;
  };
  return this;
}


/*!
  * domready (c) Dustin Diaz 2012 - License MIT
  */
//https://github.com/ded/domready/blob/master/src/ready.js
!function (name, definition) {
  if (typeof module != 'undefined') module.exports = definition()
  else if (typeof define == 'function' && typeof define.amd == 'object') define(definition)
  else this[name] = definition()
}('domready', function (ready) {

  var fns = [], fn, f = false
    , doc = document
    , testEl = doc.documentElement
    , hack = testEl.doScroll
    , domContentLoaded = 'DOMContentLoaded'
    , addEventListener = 'addEventListener'
    , onreadystatechange = 'onreadystatechange'
    , readyState = 'readyState'
    , loaded = /^loade|c/.test(doc[readyState])

  function flush(f) {
    loaded = 1
    while (f = fns.shift()) f()
  }

  doc[addEventListener] && doc[addEventListener](domContentLoaded, fn = function () {
    doc.removeEventListener(domContentLoaded, fn, f)
    flush()
  }, f)


  hack && doc.attachEvent(onreadystatechange, fn = function () {
    if (/^c/.test(doc[readyState])) {
      doc.detachEvent(onreadystatechange, fn)
      flush()
    }
  })

  return (ready = hack ?
    function (fn) {
      self != top ?
        loaded ? fn() : fns.push(fn) :
        function () {
          try {
            testEl.doScroll('left')
          } catch (e) {
            return setTimeout(function() { ready(fn) }, 50)
          }
          fn()
        }()
    } :
    function (fn) {
      loaded ? fn() : fns.push(fn)
    })
})


function template(template_text,data){
    return template_text.replace(/%(\w*)%/g,function(m,key){return data.hasOwnProperty(key)?data[key]:"";});
}

domready(function () {
  var myConn = new XHConn();
  if (!myConn) alert("XMLHTTP not available. Try a newer/better browser.");
  var update_status = function (oXML) {
    if (oXML.status == 200){
      meta = eval('('+oXML.responseText+')');
      //var d = meta['src_version'];
      var d = {};
      for (src in meta['src']){
          d[src] = meta['src'][src]['version'];
      }
      d['total_genes'] = meta['stats']['total_genes'];
      //var status_text = 'Status: NCBI snapshot: %NCBI_SNAPSHOT%, ensembl release: %ENSEMBL_MART_VERSION%, NetAffy: %NETAFFY_RELEASE%, <a href="/metadata">view complete</a>.'
      //var status_text = 'Stats: total genes: %total_genes% Status: NCBI snapshot: %entrez%,  Ensembl release: %ensembl%,  UniProt: %uniprot%,  NetAffy: %netaffy%,  <a href="/v2/metadata">view complete</a>.'
      var status_text = 'Status: NCBI snapshot: %entrez%,  Ensembl release: %ensembl%,  UniProt: %uniprot%,  UCSC: %ucsc%, NetAffx: %reporter%,  <a href="https://mygene.info/v3/metadata">view complete</a>.'
      var status_text = template(status_text, d)
      var el = document.getElementById('status_text')
      if (el) el.innerHTML = status_text;
    }
  };
  myConn.connect("https://mygene.info/v3/metadata", "GET", "", update_status);
})
