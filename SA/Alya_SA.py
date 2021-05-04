from base.fab import *
import ruamel.yaml
from shutil import copyfile, rmtree
from pprint import pprint
import json
import easyvvuq as uq
import chaospy as cp

from plugins.FabAlya.FabAlya import *

# authors: Hamid Arabnejad, Alfonso Santiago


@task
@load_plugin_env_vars("FabAlya")
def Alya_init_SA(config, ** args):
    """
    ==========================================================================

    fab <remote_machine> Alya_init_SA:<config_name>

    example:

        fab localhost Alya_init_SA:fluid
        fab marenostrum4 Alya_init_SA:fluid
        fab marenostrum4 Alya_init_SA:fluid,TestOnly=True
    ==========================================================================
    """
    update_environment()

    #############################################
    # load Alya SA configuration from yml file #
    #############################################
    Alya_SA_config_file = os.path.join(
        get_plugin_path("FabAlya"),
        "SA",
        "Alya_SA_config.yml"
    )
    SA_campaign_config = load_SA_campaign_config(Alya_SA_config_file)
    polynomial_order = SA_campaign_config["polynomial_order"]
    sampler_name = SA_campaign_config["sampler_name"]
    campaign_name = "Alya_SA_{}".format(sampler_name)

    campaign_work_dir = os.path.join(
        get_plugin_path("FabAlya"),
        "SA",
        "Alya_SA_{}".format(sampler_name)
    )

    runs_dir, campaign_dir = init_SA_campaign(
        campaign_name=campaign_name,
        campaign_config=SA_campaign_config,
        polynomial_order=polynomial_order,
        campaign_work_dir=campaign_work_dir
    )

    #############################################################
    # copy the EasyVVUQ campaign run set TO config SWEEP folder #
    #############################################################
    campaign2ensemble(config, campaign_dir)

    ###########################################################
    # set job_desc to avoid overwriting with previous SA jobs #
    ###########################################################
    env.job_desc = "_SA_%s" % (sampler_name)
    env.prevent_results_overwrite = "delete"
    with_config(config)
    execute(put_configs, config)

    ##########################################
    # submit ensemble jobs to remote machine #
    ##########################################
    alya_ensemble(config, **args)


def init_SA_campaign(campaign_name, campaign_config,
                     polynomial_order, campaign_work_dir):

    ######################################
    # delete campaign_work_dir is exists #
    ######################################
    if os.path.exists(campaign_work_dir):
        rmtree(campaign_work_dir)
    os.makedirs(campaign_work_dir)

    #####################
    # Create an encoder #
    #####################
    encoder = uq.encoders.GenericEncoder(
        template_fname=os.path.join(get_plugin_path("FabAlya"),
                                    "templates",
                                    campaign_config["encoder_template_fname"]
                                    ),
        delimiter=campaign_config["encoder_delimiter"],
        target_filename=campaign_config["encoder_target_filename"]
    )

    ###########################
    # Set up a fresh campaign #
    ###########################
    db_location = "sqlite:///" + campaign_work_dir + "/campaign.db"

    actions = uq.actions.Actions(
        uq.actions.CreateRunDirectory(root=campaign_work_dir, flatten=True),
        uq.actions.Encode(encoder),
    )

    campaign = uq.Campaign(
        name=campaign_name,
        db_location=db_location,
        work_dir=campaign_work_dir
    )

    ################################
    # Add the flee-SA-Sampler app #
    ################################
    campaign.add_app(
        name=campaign_name,
        params=campaign_config["params"],
        actions=actions
    )

    ######################
    # parameters to vary #
    ######################
    vary = {}
    for param in campaign_config["selected_vary_parameters"]:
        pprint(campaign_config[
            "vary_parameters_range"][param])
        lower_value = campaign_config[
            "vary_parameters_range"][param]["range"][0]
        upper_value = campaign_config[
            "vary_parameters_range"][param]["range"][1]
        if campaign_config["distribution_type"] == "DiscreteUniform":
            vary.update({param: cp.DiscreteUniform(lower_value, upper_value)})
        elif campaign_config["distribution_type"] == "Uniform":
            vary.update({param: cp.Uniform(lower_value, upper_value)})

    ####################
    # create Sampler #
    ####################
    sampler_name = campaign_config["sampler_name"]
    if sampler_name == "SCSampler":
        sampler = uq.sampling.SCSampler(
            vary=vary,
            polynomial_order=polynomial_order,
            quadrature_rule=campaign_config["quadrature_rule"],
            growth=campaign_config["growth"],
            sparse=campaign_config["sparse"],
            midpoint_level1=campaign_config["midpoint_level1"],
            dimension_adaptive=campaign_config["dimension_adaptive"]
        )
    elif sampler_name == "PCESampler":
        sampler = uq.sampling.PCESampler(
            vary=vary,
            polynomial_order=polynomial_order,
            rule=campaign_config["quadrature_rule"],
            sparse=campaign_config["sparse"],
            growth=campaign_config["growth"]
        )
    # TODO: add other sampler here

    ###########################################
    # Associate the sampler with the campaign #
    ###########################################
    campaign.set_sampler(sampler)

    #########################################
    # draw all of the finite set of samples #
    #########################################
    campaign.execute().collate()

    #########################################
    # extract generated runs id by campaign #
    #########################################
    runs_dir = []
    for _, run_info in campaign.campaign_db.runs(
            status=uq.constants.Status.NEW
    ):
        runs_dir.append(run_info["run_name"])

    campaign_dir = campaign.campaign_db.campaign_dir()

    ######################################################
    # backup campaign files, i.e, *.db, *.json, *.pickle #
    ######################################################
    backup_campaign_files(campaign.work_dir)

    print("=" * 50)
    print("With user's specified parameters for {}".format(sampler_name))
    print("campaign name : {}".format(campaign_name))
    print("number of generated runs : {}".format(len(runs_dir)))
    print("campaign dir : {}".format(campaign_work_dir))
    print("=" * 50)

    return runs_dir, campaign_dir


def load_SA_campaign_config(Alya_SA_config_file):
    SA_campaign_config = yaml.load(
        open(Alya_SA_config_file),
        Loader=yaml.SafeLoader
    )
    #####################################################
    # load parameter space for the easyvvuq sampler app #
    #####################################################
    sampler_params_json_PATH = os.path.join(
        get_plugin_path("FabAlya"),
        "templates",
        "params.json"
    )

    # here, I parse the lines in the json file and remove lines with comments
    with open(sampler_params_json_PATH, "r") as jsonfile:
        jsondata = "".join(
            line for line in jsonfile if "//" not in line
        )
        sampler_params = json.loads(jsondata)

    #####################################################
    # add loaded campaign params to SA_campaign_config #
    #####################################################
    SA_campaign_config.update({"params": sampler_params})

    return SA_campaign_config


def backup_campaign_files(campaign_work_dir):
    backup_dir = os.path.join(campaign_work_dir, "backup")
    # delete backup folder
    if os.path.exists(backup_dir):
        rmtree(backup_dir)
    os.mkdir(backup_dir)

    with hide("output", "running", "warnings"), settings(warn_only=True):
        local(
            "rsync -av -m -v \
            --include='*.db' \
            --include='*.pickle' \
            --include='*.json' \
            --exclude='*' \
            {}/  {} ".format(campaign_work_dir, backup_dir)
        )


def load_campaign_files(campaign_work_dir):
    backup_dir = os.path.join(campaign_work_dir, "backup")
    with hide("output", "running", "warnings"), settings(warn_only=True):
        local(
            "rsync -av -m -v \
            --include='*.db' \
            --include='*.pickle' \
            --include='*.json' \
            --exclude='*' \
            {}/  {} ".format(backup_dir, campaign_work_dir)
        )
