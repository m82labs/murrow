#!/usr/bin/env python
import json

# Parse the config
_config_path = os.path.join(os.path.expanduser('~'), '.murrow', 'murrow.config')
config = json.loads(open(config_path, 'r').read())['murrow_settings']['share_settings']
