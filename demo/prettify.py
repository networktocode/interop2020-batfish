import itertools

from rich import box
from rich.console import Console
from rich.syntax import Syntax
from rich.table import Table

console = Console()


def pprint_diff_reachability(answer):
    # Loop over flows
    for flow_n, flow in enumerate(answer["Flow"]):

        # Create table
        table = Table(show_header=True, box=box.ROUNDED)
        table.add_column(
            "[bold magenta]FLOW: [/bold magenta][blue]{}[/blue]".format(flow), width=100
        )
        reference_traces = list(answer["Reference_Traces"][flow_n])
        snapshot_traces = list(answer["Snapshot_Traces"][flow_n])

        # Add trace counts
        table.add_row(
            "[bold white]Reference Traces (count={})[/bold white]".format(
                str(answer.iloc[flow_n].Reference_TraceCount)
            ),
            "[bold white]Snapshot Traces (count={})[/bold white]".format(
                str(answer.iloc[flow_n].Snapshot_TraceCount)
            ),
        )

        # Zip traces and add to rows
        for zipped_flow_traces in list(
            itertools.zip_longest(reference_traces, snapshot_traces, fillvalue="")
        ):
            table.add_row("", "")
            table.add_row(str(zipped_flow_traces[0]), str(zipped_flow_traces[1]))
            
        console.print(table)
