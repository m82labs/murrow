#!/usr/bin/env python
import yaml
import os
import shutil

_config_path = os.path.join(os.path.expanduser('~'), '.murrow', 'murrow.config')
_example_path = '/usr/share/doc/murrow/examples/murrow.config.example'


if not os.path.isfile(_config_path):
    if os.path.isfile(_example_path):
        shutil.copyfile(_example_path, _config_path)
        has_config = True
    else:
        has_config = False
else:
    has_config = True

if has_config:
    with open(_config_path, 'r') as f:
        configuration = yaml.load(f)
else:
    configuration = None
