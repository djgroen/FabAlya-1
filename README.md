
# FabAlya
FabAlya is a  [FabSim3](https://github.com/djgroen/FabSim3) plugin for automated [Alya](https://www.bsc.es/research-development/research-areas/engineering-simulations/alya-high-performance-computational) simulation code.

This plugin provides functionality to extend FabSim3's workflow and remote submission capabilities to Alya tasks.

## FabSim3 Installation
To install FabSim3 toolkit, please follow [the installation instruction](https://fabsim3.readthedocs.io/en/latest/installation.html#installing-fabsim3).

In case of having any issue, please look at to the [Known Issues](https://fabsim3.readthedocs.io/en/latest/installation.html#known-issues) page.

## FabAlya Installation
before submit a Alya simulation job,  you should install FabAlya which provides functionality to extend FabSim3's workflow and remote submission capabilities to Alya tasks. Please got to your local `FabSim3` folder , and install it by typing:
```sh
fab localhost install_plugin:FabMD
```
Once you have installed The FabAlya plugin, which will appear in  `FabSim3/plugins/FabAlya` directory, , you need to take a few small configuration steps before submitting a job to remote machine.

Modify  `FabSim3/plugins/FabAlya/machines_FabAlya_user.yml` file, and update the `username` and `home_path_template` variables with your username on [MarenoStrum4](https://www.bsc.es/user-support/mn4.php ) cluster.
 ```yaml
 ...
 marenostrum4:
     username: "pr1emk01"
     home_path_template: "/home/pr1emk00/pr1emk01"
     ...
 ```
Also, make sure the other required parameters for Alya job are filled correctly, variables such as :

 1. `ALYA_EXE_PATH` : PATH to Alya code
 2. `MPIO_BIN_PATH` : PATH to .mpio.bin files
 3. `ALYA_DAT_PATH` : PATH to Alya input dat files
 4. `PYTHON_CODES_PATH`: PATH to pre and post processing python codes
 5. `SH_SCRIPTS_PATH` : PATH to pre and post processing sh scripts

```yaml
Alya_simulation_config: &Alya_sim_config
  # ALYA_EXE_PATH: "/home/bsc21/bsc21717/Software/Alya_versions/777-hvad-pump-function_kpp_nobovel/Executables/unix_nastin_temper_fastest_ipo_onlyfiltAP/Alya.x"
  ALYA_EXE_PATH: "<PATH to Alya code>"

  MPIO_BIN_PATH: "<PATH to .mpio.bin files>"
  ALYA_DAT_PATH: "<PATH to Alya input dat files>"

  PYTHON_CODES_PATH: "<PATH to python pre/pos processing files>"
  PY_FILE_NAMES: ["field-ensi2mpio.py", "modifyHR.py", 
                  "remote_postpro.py", "remote_prepro.py"]

  SH_SCRIPTS_PATH: "<PATH to pre and post processing sh scripts>"
  SH_FILE_NAME: ["remote.sh", "remotepre.sh"]
 
```
 ## Submit a Alya job
 To submit a Alya job, you can follow this structure:
 ```sh
 fab <remote_machine_name> <Alya_task>:<Alya_config_name>
 ``` 
 for example,
  ```sh
 fab marenostrum4 alya:fluid
 ``` 
 In case of testing to make sure that the job scripts is created correctly or file/folder structure is correct, you can add `TestOnly=True` option at the end of you command which do the same process but ignore the job_submission step.
 
  ```sh
 fab marenostrum4 alya:fluid,TestOnly=True
 ``` 
