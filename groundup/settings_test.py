# A workaround Django's new extremely annoying
# new feature of making tests execute migrations.
# Run tests like this:
# ./manage.py test --settings groundup.settings_test [test spec]
# See https://gist.github.com/NotSqrt/5f3c76cd15e40ef62d09 for details

from .settings import *


class DisableMigrations(object):

    def __contains__(self, item):
        return True

    def __getitem__(self, item):
        return "notmigrations"

MIGRATION_MODULES = DisableMigrations()
