'''
    MyGene Local Tester
    > python local.py
'''

from nose.core import run

from biothings.tests import TornadoTestServerMixin
from tests.remote import MyGeneRemoteTest
from biothings.web.settings import BiothingESWebSettings


class MyGeneLocalTest(TornadoTestServerMixin, MyGeneRemoteTest):
    '''
        Starts a Tornado server on its own and perform tests against this server.
        Requires config.py under src folder.
    '''

    __test__ = True

    # Override default setting loader
    settings = BiothingESWebSettings(config='config')


if __name__ == '__main__':
    print()
    print('MyGene Local Test')
    print('-'*70)
    print()
    run(argv=['', '--logging-level=WARNING', '-v'], defaultTest='__main__.MyGeneLocalTest')
