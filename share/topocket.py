#!/usr/bin/env python
import json
import os
from pocket import Pocket, PocketException
from . import config


def add_to_pocket(url):
    if 'pocket_settings' in config:
	    pocket_config = config['pocket_settings']
	    pc = Pocket(
		consumer_key=pocket_config['consumer_key'],
		access_token=pocket_config['access_token']
	    )
	    return pc.add( url=url )
    else:
	return {"status":0,"message":"Pocket not configured."}
