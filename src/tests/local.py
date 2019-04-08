''' MyGene Data-Aware Tests
    > python tests.py
'''

from nose.core import run

from biothings.tests import TornadoTestServerMixin
from tests.remote import MyGeneRemoteTest
from web.settings import MyGeneWebSettings


class MyGeneLocalTest(TornadoTestServerMixin, MyGeneRemoteTest):
    ''' Self contained test class, can be used for CI tools such as Travis
        Starts a Tornado server on its own and perform tests against this server.
    '''

    __test__ = True

    # Reads Settings from config.py
    WEB_SETTINGS = MyGeneWebSettings(config='config')


if __name__ == '__main__':
    run(argv=['', '--logging-level=INFO', '-v'], defaultTest='tests.local.MyGeneLocalTest')
