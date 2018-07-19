from collections import OrderedDict
import inspect
import os
import argparse
import sys
import yaml
from contextlib import contextmanager

from autocast import estimateTypedValue

# The following lines cause all dict's to be output in block
# style while leaving the rest as default
# inspired from https://stackoverflow.com/a/38370522/3140750
def dict_representer(dumper, data):
    return dumper.represent_mapping('tag:yaml.org,2002:map', data, flow_style=False)


yaml.add_representer(dict, dict_representer)


@contextmanager
def changed_dir(dirname):
    try:
        cwd = os.getcwd()
        os.chdir(dirname)
        yield
    finally:
        os.chdir(cwd)


def collect_items_into_dict(items_list):
    return_dict = OrderedDict()
    for item_name, item_value in items_list:
        if item_name in return_dict:
            return_dict[item_name].append(item_value)
        else:
            return_dict[item_name] = [item_value]
    return return_dict


def getFrameDir():
    """
    Gets the direcctory of the script calling this function.
    """
    CurrentFrameStack = inspect.stack()
    if len(CurrentFrameStack) > 1:
        ParentFrame = CurrentFrameStack[1][0]
        FrameFileName = inspect.getframeinfo(ParentFrame).filename
        FrameDir = os.path.dirname(os.path.abspath(FrameFileName))
    else:
        FrameDir = None

    return FrameDir


def build_description(param_dict, suffix_desc=None):
    seed = param_dict['seed']
    dataset_id = param_dict['dataset_id']

    desclist = []
    desclist.append('seed')
    desclist.append(str(seed))
    desclist.append(dataset_id)
    if suffix_desc:
        desclist.append(suffix_desc)

    return "_".join(desclist)


def parse_params_from_args(param_dict, argv):
    """
    Parses the commandline parameters and returns a dict. This searches for options specifying the values in param_dict.
    values for which param_dict is None are considered required arguments of indeterminate type.
    """

    assert all(isinstance(x, str) for x in argv), 'Each argv element should be a string'

    parser = argparse.ArgumentParser()
    for pname, pval in param_dict.items():
        pargname = '--' + pname.replace('_', '-')
        if pval is None:
            parser.add_argument(pargname, type=estimateTypedValue, required=True)
        else:
            parser.add_argument(pargname, type=type(pval), default=pval)

    parsed_cl_params = parser.parse_args(argv)

    return_dict = {pname: getattr(parsed_cl_params, pname) for pname in param_dict}
    return return_dict


def parse_commandline_info(param_dict_from_file):
    parser = argparse.ArgumentParser()
    parser.add_argument('-d', '--description', type=str, default=None)
    parser.add_argument('-i', '--index', type=int, default=0)

    parsed_args, remaining_args = parser.parse_known_args()
    commandline_param_dict = parse_params_from_args(param_dict_from_file, remaining_args)

    final_param_dict = param_dict_from_file.copy()
    final_param_dict.update(commandline_param_dict)

    if parsed_args.description is not None:
        if parsed_args.description.startswith('_'):
            sim_description = build_description(final_param_dict, parsed_args.description[1:])
        else:
            sim_description = parsed_args.description
    else:
        sim_description = build_description(final_param_dict)

    meta_info_dict = {}
    meta_info_dict['index'] = parsed_args.index
    if sim_description:
        meta_info_dict['description'] = sim_description

    return final_param_dict, meta_info_dict


def parse_meta_info_basic():
    parser = argparse.ArgumentParser()
    parser.add_argument('-d', '--description', type=str)
    parser.add_argument('-i', '--index', type=int, default=0)
    parsed_args = parser.parse_args(sys.argv[1:])
    sim_description = parsed_args.description

    meta_info_dict = {}
    meta_info_dict['index'] = parsed_args.index
    if sim_description:
        meta_info_dict['description'] = sim_description

    return meta_info_dict
