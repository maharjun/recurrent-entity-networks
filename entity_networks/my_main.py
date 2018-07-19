"Training task script."
from __future__ import absolute_import
from __future__ import print_function
from __future__ import division

import os
import tensorflow as tf

from basicutils import parse_commandline_info
from basicutils import yaml
from basicutils import getFrameDir
from simmanager import SimManager
from contextlib import ExitStack

from tensorflow.contrib.learn.python.learn import learn_runner

from entity_networks.experiment import generate_experiment_fn

"""
Design choices:

1.  Parameters by command line
2.  Parameters by file

For 1
advantages:

The invocation of each command contains all the info relating to the simulation
The folder name also contains all the info relevant

For 2

Can put a lot more parameters.
Will not have split parameterization between simulation code and command line
More streamlined in reading and writing parameters

disadv:
will need extra logic to create dir name from parameters
cannot control from command line

best of both worlds.
command line params override the parameters from file
"""


def main(param_dict, simmanager: SimManager):
    "Entrypoint for training."

    # perform basic type checks on parameters
    assert isinstance(param_dict['data_dir'], str)
    assert isinstance(param_dict['dataset_id'], str)
    assert isinstance(param_dict['seed'], int)

    assert isinstance(param_dict['batch_size'], int)
    assert isinstance(param_dict['num_blocks'], int)
    assert isinstance(param_dict['embedding_size'], int)
    assert isinstance(param_dict['clip_gradients'], float)

    assert isinstance(param_dict['num_epochs'], int)
    assert isinstance(param_dict['lr_min'], float)
    assert isinstance(param_dict['lr_max'], float)
    assert isinstance(param_dict['lr_step_size'], int)
    assert isinstance(param_dict['grad_noise'], float)

    # save the parameter configuration
    with open(os.path.join(simmanager.paths.data_path, 'sim_config.yaml'), 'w') as fout:
        yaml.dump(param_dict, fout)

    tf.set_random_seed(param_dict['seed'])

    tf.logging.set_verbosity(tf.logging.INFO)

    experiment_fn = generate_experiment_fn(
        data_dir=param_dict['data_dir'],
        dataset_id=param_dict['dataset_id'],
        num_epochs=param_dict['num_epochs'],

        batch_size=param_dict['batch_size'],
        num_blocks=param_dict['num_blocks'],
        embedding_size=param_dict['embedding_size'],
        clip_gradients=param_dict['clip_gradients'],

        learning_rate_min=param_dict['lr_min'],
        learning_rate_max=param_dict['lr_max'],
        learning_rate_step_size=param_dict['lr_step_size'],
        gradient_noise_scale=param_dict['grad_noise'])

    learn_runner.run(experiment_fn, simmanager.paths.simulation_path)


if __name__ == '__main__':
    is_debug = False

    if is_debug:
        from ipdb import launch_ipdb_on_exception, set_trace
        set_trace()

    with ExitStack() as E:
        if is_debug:
            E.enter_context(launch_ipdb_on_exception())

        results_directory = os.path.join(os.environ['HOME'], 'RESULTS')
        sim_name = 'EntNet-babi'
        script_dir = getFrameDir()
        with open(os.path.join(script_dir, 'my_main_params.yaml')) as fin:
            param_dict_from_file = yaml.safe_load(fin)
        final_param_dict, meta_info_dict = parse_commandline_info(param_dict_from_file)

        with SimManager(sim_name, results_directory, param_dict=meta_info_dict) as sim_man:
            main(final_param_dict, sim_man)
