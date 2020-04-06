from tornado.web import RequestHandler


class TaxonHandler(RequestHandler):

    def get(self, taxid):
        self.redirect("http://t.biothings.io/v1/taxon/%s?include_children=1" % taxid)


class DemoHandler(RequestHandler):

    def get(self):
        with open('../docs/demo/index.html', 'r') as demo_file:
            self.write(demo_file.read())


class FrontPageHandler(RequestHandler):
    
    def get(self):
        self.write("MYGENE FRONTPAGE!")
