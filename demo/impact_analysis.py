#!/usr/bin/env python3

import argparse
import logging
import random
import sys

from pybatfish.client.commands import (
    bf_session,
    bf_set_network,
    bf_fork_snapshot,
    bf_init_snapshot,
)
from pybatfish.question.question import load_questions
from pybatfish.datamodel.flow import HeaderConstraints, PathConstraints
from pybatfish.question import bfq
from rich import print
from prettify import pprint_diff_reachability


# Constants
DST_IP_REACHABILITY = "10.2.10.1,10.2.20.1,10.2.30.1"
PORT_CHANNEL_MEMBER_SCOPE = "/access|aggr|core/"
L3_INTERFACE_SCOPE = "/access|aggr|core/"
NODE_SCOPE = "/aggr|core/"


def delete_bf_data():
    for snapshot in bf_session.list_snapshots():
        bf_session.delete_snapshot(snapshot)
    for network in bf_session.list_networks():
        bf_session.delete_network(network)


def get_differential_reachability(bf_snapshot_base, bf_snapshot_fail):
    answer = (
        bfq.differentialReachability(
            headers=HeaderConstraints(dstIps=DST_IP_REACHABILITY)
        )
        .answer(snapshot=bf_snapshot_fail, reference_snapshot=bf_snapshot_base)
        .frame()
    )
    return answer


def pprint_results(answer):
    if len(answer) > 0:
        print(
            ":cross_mark:\n\n[bold red][FAIL] Reachability differences found...[/bold red]\n"
        )
        pprint_diff_reachability(answer)
        quit()
    else:
        print(":white_heavy_check_mark:")


def print_bf_params(**bf_params):
    """Print name and value of each element to screen"""
    for name, value in bf_params.items():
        print(f"[white]{name}[white] = [bold blue]{value}[/bold blue]")


def deactivate_nodes(bf_snapshot_base, bf_snapshot_fail):
    nodes = bfq.nodeProperties(nodes=NODE_SCOPE).answer().frame()

    for node_index in range(len(nodes)):
        print(
            "[*] Deactivating node: [magenta bold]{}[/magenta bold]".format(
                nodes.loc[node_index].Node
            ),
            end=" ",
        )
        bf_fork_snapshot(
            base_name=bf_snapshot_base,
            name=bf_snapshot_fail,
            deactivate_nodes=[nodes.loc[node_index].Node],
            overwrite=True,
        )
        pprint_results(
            get_differential_reachability(bf_snapshot_base, bf_snapshot_fail)
        )


def deactivate_po_members(bf_snapshot_base, bf_snapshot_fail):
    po_members = list(
        bfq.interfaceProperties(
            nodes=PORT_CHANNEL_MEMBER_SCOPE, properties="Channel_Group"
        )
        .answer()
        .frame()
        .dropna()
        .Interface
    )

    for po_member in po_members:
        print(
            f"[*] Deactivating port-channel member: [magenta bold]{po_member}[/magenta  bold]",
            end=" ",
        )
        bf_fork_snapshot(
            base_name=bf_snapshot_base,
            name=bf_snapshot_fail,
            deactivate_interfaces=[po_member],
            overwrite=True,
        )
        pprint_results(
            get_differential_reachability(bf_snapshot_base, bf_snapshot_fail)
        )


def deactivate_l3_interfaces(bf_snapshot_base, bf_snapshot_fail):
    l3_links = (
        bfq.edges(nodes=L3_INTERFACE_SCOPE, remoteNodes=L3_INTERFACE_SCOPE)
        .answer(bf_snapshot_base)
        .frame()
    )

    for link_index in range(len(l3_links)):
        print(
            "[*] Deactivating l3 link interface: [magenta bold]{}[/magenta bold]".format(
                l3_links.loc[link_index].Interface
            ),
            end=" ",
        )
        bf_fork_snapshot(
            base_name=bf_snapshot_base,
            name=bf_snapshot_fail,
            deactivate_interfaces=[l3_links.loc[link_index].Interface],
            overwrite=True,
        )
        pprint_results(
            get_differential_reachability(bf_snapshot_base, bf_snapshot_fail)
        )


def main():
    random.seed(80)

    logging.disable(sys.maxsize)

    parser = argparse.ArgumentParser(description="Batfish Impact Analysis")
    parser.add_argument("-p", "--snapshot_path", help="BF_SNAPSHOT_PATH", required=True)
    parser.add_argument("-s", "--snapshot_name", help="SNAPSHOT_NAME", required=True)
    parser.add_argument("-n", "--network_name", help="BF_NETWORK", required=True)
    parser.add_argument(
        "-i", "--service_ip", help="SERVICE_IP", default="172.29.236.139"
    )

    args = vars(parser.parse_args())

    BF_NETWORK = args["network_name"]
    BF_SNAPSHOT_BASE = args["snapshot_name"]
    BF_SNAPSHOT_PATH = args["snapshot_path"]
    BF_SNAPSHOT_FAIL = "fail_snapshot"
    # BATFISH_SERVICE_IP = "172.29.236.139"
    BATFISH_SERVICE_IP = args["service_ip"]

    bf_session.host = BATFISH_SERVICE_IP

    load_questions()
    bf_set_network(BF_NETWORK)
    bf_init_snapshot(BF_SNAPSHOT_PATH, name=BF_SNAPSHOT_BASE, overwrite=True)

    # Print Batfish settings/parameters
    print_bf_params(
        DST_IP_REACHABILITY=DST_IP_REACHABILITY,
        PORT_CHANNEL_MEMBER_SCOPE=PORT_CHANNEL_MEMBER_SCOPE,
        L3_INTERFACE_SCOPE=L3_INTERFACE_SCOPE,
        NODE_SCOPE=NODE_SCOPE,
    )

    # Run Batfish tests
    print("\n[bold]== Deactivating Interfaces ==[/bold]")
    deactivate_po_members(BF_SNAPSHOT_BASE, BF_SNAPSHOT_FAIL)
    deactivate_l3_interfaces(BF_SNAPSHOT_BASE, BF_SNAPSHOT_FAIL)

    print("\n[bold]== Deactivating Nodes ==[/bold]")
    deactivate_nodes(BF_SNAPSHOT_BASE, BF_SNAPSHOT_FAIL)

    print("\n[bold green][SUCCESS] No reachability differences found[/bold green]")

    # Clean up Snapshots/Networks
    delete_bf_data()


if __name__ == "__main__":
    main()
