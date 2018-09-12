import pip
from pip._internal.utils.misc import get_installed_distributions
from subprocess import call
from time import sleep

for dist in get_installed_distributions():
    call("pip install --upgrade " + dist.project_name, shell=True)