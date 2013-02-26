import types
import json
import tornado.web


class BaseHandler(tornado.web.RequestHandler):
    jsonp_parameter='callback'

    def _check_fields_param(self, kwargs):
        '''support "filter" as an alias of "fields" parameter for back-compatability.'''
        if 'filter' in kwargs and 'fields' not in kwargs:
            #support filter as an alias of "fields" parameter (back compatibility)
            kwargs['fields'] = kwargs['filter']
            del kwargs['filter']
        if 'fields' in kwargs:
            kwargs['fields'] = [x.strip() for x in kwargs['fields'].split(',')]
        return kwargs

    def get_query_params(self):
        _args = {}
        for k in self.request.arguments:
            v = self.request.arguments[k]
            if type(v) is types.ListType and len(v) == 1:
                _args[k] = v[0]
            else:
                _args[k] = v
        _args.pop(self.jsonp_parameter, None)   #exclude jsonp parameter if passed.
        self._check_fields_param(_args)
        return _args

    # def get_current_user(self):
    #     user_json = self.get_secure_cookie("user")
    #     if not user_json:
    #         return None
    #     return tornado.escape.json_decode(user_json)

    def return_json(self, data, encode=True):
        '''return passed data object as JSON response.
           if <jsonp_parameter> is passed, return a valid JSONP response.
           if encode is False, assumes input data is already a JSON encoded
           string.
        '''
        jsoncallback = self.get_argument(self.jsonp_parameter, '')  # return as JSONP
        _json_data = json.dumps(data) if encode else data
        self.set_header("Content-Type", "application/json; charset=UTF-8")
        #get etag if data is a dictionary and has "etag" attribute.
        etag = data.get('etag', None) if isinstance(data, dict) else None
        self.set_cacheable(etag=etag)
        self.support_cors();
        if jsoncallback:
            self.write('%s(%s)' % (jsoncallback, _json_data))
        else:
            self.write(_json_data)

    def set_cacheable(self, etag=None):
        '''set proper header to make the response cacheable.
           set etag if provided.
        '''
        self.set_header("Cache-Control", "max-age=604800, public")  # 7days
        if etag:
            self.set_header('Etag', etag)

    def support_cors(self, *args, **kwargs):
        '''Provide server side support for CORS request.'''
        self.set_header("Access-Control-Allow-Origin", "*")
        self.set_header("Access-Control-Allow-Methods", "GET,POST,OPTIONS")
        self.set_header("Access-Control-Allow-Headers", "Content-Type, Depth, User-Agent, X-File-Size, X-Requested-With, If-Modified-Since, X-File-Name, Cache-Control")
        self.set_header("Access-Control-Allow-Credentials", "false")
        self.set_header("Access-Control-Max-Age", "60")

    def options(self, *args, **kwargs):
        self.support_cors()
