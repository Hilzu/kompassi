from distutils.util import strtobool as _bool
import os
import os

os.environ['DJANGO_SETTINGS_MODULE'] = 'turska.settings'
BEHAVE_DEBUG_ON_ERROR = _bool(os.environ.get("BEHAVE_DEBUG_ON_ERROR", "no"))


def before_all(context):
    # from django.core.management import setup_environ
    # from turska import settings
    # setup_environ(settings)

    from django.test.simple import DjangoTestSuiteRunner
    context.runner = DjangoTestSuiteRunner()

    from south.management.commands import patch_for_test_db_setup
    patch_for_test_db_setup()


def before_scenario(context, scenario):
    context.runner.setup_test_environment()
    context.old_db_config = context.runner.setup_databases()


def after_scenario(context, scenario):
    context.runner.teardown_databases(context.old_db_config)
    context.runner.teardown_test_environment()



def after_step(context, step):
    if BEHAVE_DEBUG_ON_ERROR and step.status == "failed":
        import ipdb
        ipdb.post_mortem(step.exc_traceback)