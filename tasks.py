import sys
from invoke import run, task
from python_boilerplate.tasks import *


@task
def configure(ctx, has_flag=False):
    """
    Instructions for preparing package for development.
    """

    print('has flag:', has_flag)

    run("%s -m pip install .[dev] -r requirements.txt" % sys.executable)