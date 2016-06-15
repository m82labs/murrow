# -*- coding: utf-8 -*-
from pocket import Pocket
from config import configuration as mconfig


def send_to_pocket(url):
    if mconfig:
        if 'share_settings' in mconfig:
            if 'pocket' in mconfig['share_settings']:
                pocket_config = mconfig['share_settings']['pocket']
                pc = Pocket(
                    consumer_key=pocket_config['consumer_key'],
                    access_token=pocket_config['access_token']
                )
                return pc.add( url=url )
        else:
            return {"status":0,"message":"Pocket not configured."}
    else:
        return {"status":0,"message":"No configuration file found."}
