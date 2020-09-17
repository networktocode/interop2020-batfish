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

## Execution
```
python -i demo/impact_analysis.py -p snapshots/3tier-multivendor/ -n demo-net -s demo-snapshot
```
