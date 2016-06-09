#!/usr/bin/env python
import json
import os
from pocket import Pocket, PocketException

# https://github.com/rakanalh/pocket-api

def add_to_pocket(url):
    # Parse the config
    config_path = os.path.join(os.path.expanduser('~'), '.murrow', 'murrow.config')
    config = json.loads(open(config_path, 'r').read())['murrow_settings']['pocket_settings']
    pc = Pocket( consumer_key=config['consumer_key'], access_token=config['access_token'] )
    return pc.add( url=url )