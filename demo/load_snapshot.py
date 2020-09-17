#!/usr/bin/env python

from pybatfish.client.commands import *
from pybatfish.question.question import load_questions
from pybatfish.datamodel.flow import HeaderConstraints, PathConstraints
from pybatfish.question import bfq
import random
import sys
import argparse

parser = argparse.ArgumentParser(description="Batfish Shell")
parser.add_argument("-p", "--snapshot_path", help="SNAPSHOT_PATH", required=True)
parser.add_argument("-s", "--snapshot_name", help="SNAPSHOT_NAME", required=True)
parser.add_argument("-n", "--network_name", help="NETWORK_NAME", required=True)

BATFISH_SERVICE_IP = "172.29.236.139"
args = vars(parser.parse_args())
bf_session.host = BATFISH_SERVICE_IP
load_questions()

print("[*] Initializing BASE_SNAPSHOT")
bf_set_network(args["network_name"])
bf_init_snapshot(args["snapshot_path"], name=args["snapshot_name"], overwrite=True)

print("[OK] Success - Batfish imports ready...")
