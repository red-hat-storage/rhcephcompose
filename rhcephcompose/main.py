""" rhcephcompose CLI """

from argparse import ArgumentParser
import kobo.conf
from rhcephcompose.compose import Compose


class RHCephCompose(object):
    """ Main class for rhcephcompose CLI. """

    def __init__(self):

        parser = ArgumentParser(description='Generate a compose for RHCS.')
        parser.add_argument('config_file', metavar='config',
                            help='main configuration file for this release.')
        args = parser.parse_args()

        conf = kobo.conf.PyConfigParser()
        conf.load_from_file(args.config_file)

        compose = Compose(conf)
        compose.run()
