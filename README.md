# Interop 2020 Batfish Demo
This demo runs a flow based verfication check across a 3 tier network.
Full details and explanations can be seen within the Interop presentation - **Validating Network HA with Batfish**.

## Logic
This script will run the following steps over the following
1. Create a snapshot fork
2. Disable an attribute (node or interface)
3. Run a differential reachability test
4. If the flow result (success/fail) IS different to the original snapshot it will print the flow results
5. If the flow result (success/fail) IS NOT different step the script will proceed to step 1 again

## Quickstart

Install and run Batfish from a Docker container.
```bash
$ docker run --name batfish -d -v batfish-data:/data -p 8888:8888 -p 9997:9997 -p 9996:9996 batfish/allinone
```

Install the Python dependencies (assuming you have [Poetry](https://python-poetry.org) installed). This will automatically install the Python package dependencies into a virtual environment.
```bash
$ poetry install
```

Use `poetry run` to execute the demo script. Pass the IP address of your Batfish service using the `-i/--service_ip` argument. If you are running Batfish from the container in the previous step, just use `-i localhost`.
```bash
$ poetry run ./demo/impact_analysis.py -p snapshots/3tier-multivendor/ -n demo-net -s demo-snapshot -i localhost
```
