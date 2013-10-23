from tornado.httpclient import HTTPRequest, AsyncHTTPClient
from pyga.requests import (Tracker, Page, Session, Visitor,
                           Event, PageViewRequest, EventRequest)
import config


class GAMixIn:
    def ga_track(self, event={}):
        _req_list = []
        no_tracking = self.get_argument('no_tracking', None)
        is_prod = getattr(config, 'RUN_IN_PROD', False)
        if not no_tracking and is_prod and hasattr(config, "GA_ACCOUNT"):
            _req = self.request
            remote_ip = _req.headers.get("X-Real-Ip",
                        _req.headers.get("X-Forwarded-For",
                        _req.remote_ip))
            user_agent = _req.headers.get("User-Agent", None)
            visitor = Visitor()
            visitor.ip_address = remote_ip
            visitor.user_agent = user_agent
            #get visitor.locale
            visitor.extract_from_server_meta(
                {"HTTP_ACCEPT_LANGUAGE": _req.headers.get("Accept-Language", None)}
            )
            session = Session()
            page = Page(_req.path)
            tracker = Tracker(config.GA_ACCOUNT, 'mygene.info')
            # tracker.track_pageview(page, session, visitor)  #this is non-async request
            pvr = PageViewRequest(config=tracker.config,
                                  tracker=tracker,
                                  visitor=visitor,
                                  session=session,
                                  page=page)
            r = pvr.build_http_request()
            _req_list.append(HTTPRequest(r.get_full_url(),
                                         "POST" if r.has_data() else "GET",
                                         headers=r.headers,
                                         body=r.data))
            if event:
                evt = Event(**event)
                #tracker.track_event(evt, session, visitor)  #this is non-async request
                er = EventRequest(config=tracker.config,
                                  tracker=tracker,
                                  visitor=visitor,
                                  session=session,
                                  event=evt)
                r = er.build_http_request()
                _req_list.append(HTTPRequest(r.get_full_url(),
                                             "POST" if r.has_data() else "GET",
                                             headers=r.headers,
                                             body=r.data))

            #now send actual async requests
            http_client = AsyncHTTPClient()
            for _req in _req_list:
                http_client.fetch(_req)
