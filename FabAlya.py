# -*- coding: utf-8 -*-
#
# This source file is part of the FabSim software toolkit, which is
# distributed under the BSD 3-Clause license.
# Please refer to LICENSE for detailed information regarding the licensing.
#
# This file contains FabSim definitions specific to FabAlya.
# authors:
#           Hamid Arabnejad, and Alfonso Santiago

from base.fab import *
add_local_paths("FabAlya")


@task
@load_plugin_env_vars("FabAlya")
def alya(config, script="alya", **args):
    """
    This function will submit a single Alya task.
        fab marenostrum4 alya:fluid,TestOnly=True
    """
    update_environment(args)
    extra_update_environment()
    with_config(config)
    execute(put_configs, config)

    job(dict(script=script), args)


def extra_update_environment():
    # we convert the PY_FILE_NAMES, SH_FILE_NAME array to
    # string to be used in the job script
    env.PY_FILE_NAMES = ' '.join(env.PY_FILE_NAMES)
    env.SH_FILE_NAME = ' '.join(env.SH_FILE_NAME)
