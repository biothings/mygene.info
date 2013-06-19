from pyga.requests import Tracker, Page, Session, Visitor, Event
import config

class GAMixIn:
    def ga_track(self, event={}):
        if getattr(config, 'RUN_IN_PROD', False):
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
            tracker.track_pageview(page, session, visitor)
            if event:
                evt = Event(**event)
                tracker.track_event(evt, session, visitor)
