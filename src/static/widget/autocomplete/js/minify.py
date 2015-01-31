#!/usr/bin/python
import sys
if sys.version > '3':
    PY3 = True
else:
    PY3 = False
if PY3:
    import http.client, urllib.request, urllib.parse, urllib.error, sys, json,pprint, os.path
else:
    import httplib, urllib, sys, json,pprint, os.path

infile = sys.argv[1] if len(sys.argv)>1 else 'mygene_query.js'
outfile = '_min'.join(os.path.splitext(infile))

with file(infile) as in_f:
    if PY3:
        params = urllib.parse.urlencode([
            #('code_url', sys.argv[1]),
            ('js_code', in_f.read()),
            #('compilation_level', 'ADVANCED_OPTIMIZATIONS'),
            ('compilation_level', 'SIMPLE_OPTIMIZATIONS'),
            ('output_format', 'json'),
            ('output_info', 'compiled_code'),
            ('output_info', 'warnings'),
            ('output_info', 'errors'),
            ('output_info', 'statistics'),
            #('warning_level', 'verbose'),

        ])
    else:
        params = urllib.urlencode([
            #('code_url', sys.argv[1]),
            ('js_code', in_f.read()),
            #('compilation_level', 'ADVANCED_OPTIMIZATIONS'),
            ('compilation_level', 'SIMPLE_OPTIMIZATIONS'),
            ('output_format', 'json'),
            ('output_info', 'compiled_code'),
            ('output_info', 'warnings'),
            ('output_info', 'errors'),
            ('output_info', 'statistics'),
            #('warning_level', 'verbose'),

        ])

    headers = { "Content-type": "application/x-www-form-urlencoded" }
    if PY3:
        conn = http.client.HTTPConnection('closure-compiler.appspot.com')
    else:
        conn = httplib.HTTPConnection('closure-compiler.appspot.com')
    conn.request('POST', '/compile', params, headers)
    response = conn.getresponse()
    data = response.read()
    conn.close

    res = json.loads(data)
    print("Errors:",)
    pprint.pprint(res.get('errors', None))
    print("Warnings:",)
    pprint.pprint(res.get('warnings', None))
    pprint.pprint(res['statistics'])
    out_f = file(outfile, 'w')
    out_f.write(res['compiledCode'])
    out_f.close()


