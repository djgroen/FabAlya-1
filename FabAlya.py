# -*- coding: utf-8 -*-
#
# This source file is part of the FabSim software toolkit, which is
# distributed under the BSD 3-Clause license.
# Please refer to LICENSE for detailed information regarding the licensing.
#
# This file contains FabSim definitions specific to FabAlya.
# authors:
#           Hamid Arabnejad, and Alfonso Santiago
import sys
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
    with_config(config)
    execute(put_configs, config)

    job(dict(script=script), args)


@task
@load_plugin_env_vars("FabAlya")
def alya_ensemble(config, script="alya", **args):
    """
    This function will submit an ensemble of Alya jobs.

        fab marenostrum4 alya_ensemble:fluid,TestOnly=True
    """
    update_environment(args)
    with_config(config)
    path_to_config = find_config_file_path(config)
    sweep_dir = path_to_config + "/SWEEP"
    env.script = script

    run_ensemble(config, sweep_dir, **args)


try:

    # loads Sensitivity analysis (SA) tasks
    from plugins.FabAlya.SA.Alya_SA import Alya_init_SA

except ImportError as err:
    # Output expected ImportErrors.
    print(error.__class__.__name__ + ": " + error.message)
    sys.exit()
except Exception as exception:
    # Output unexpected Exceptions.
    print(exception, False)
    print(exception.__class__.__name__ + ": " + exception.message)
    sys.exit()
