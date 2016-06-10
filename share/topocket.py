#!/usr/bin/env python
import json
import os
from pocket import Pocket, PocketException
from . import config, has_config


def add_to_pocket(url):
    if has_config:
        if 'pocket_settings' in config:
            pocket_config = config['pocket_settings']
            pc = Pocket(
            consumer_key=pocket_config['consumer_key'],
            access_token=pocket_config['access_token']
            )
            return pc.add( url=url )
        else:
            return {"status":0,"message":"Pocket not configured."}
    else:
        return {"status":0,"message":"No configuration file found."}
