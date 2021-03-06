# cardano-light-tools

<img src="image/logo.jpg" width="50%" height="50%" alt="Logo">
This repository includes a set of lightweight tools to operate and maintain a Cardano Stake Pool.

## Leaderlog

*Motivation*: Currently, most SPOs obtain their block schedule by running the cncli tool on the BP node. However, cncli requires
an external tool to calculate the total active stake and the pool's active stake for a given epoch. While this can be done using
cardano-cli, it also requires significant memory and computational resources that many BP nodes cannot spare. This script provides
an alternative solution based on [BlockFrost.io](https://blockfrost.io/) that eliminates the need to interact with cardano-cli
and cardano-node, effectively reducing memory and computational resource utilization.

To use it, create a free BlockFrost.io account and obtain an API key. Then, open `cncli-leaderlog.sh` and edit the user variables
(BlockFrost API key, pool id, path to cncli, etc.). The script will automatically obtain the active stake, synchronize the cncli
DB and calculate the leader log.

If you want to integrate the leaderlog output with other tools (e.g., Guild Operator Tools), you can keep running this script on
the BP node. However, you also have the freedom to keep track of the leaderlog on a completely different machine that does not
need to have a working cardano-cli and cardano-node setup.

## Monitoring

*Motivation*: This is a simple monitoring script that logs relevant metrics directly into a text file in human-readable form.
It can be used as an portable alternative to Grafana and other specialized tools that require a more complex setup and
consume more resources (CPU, memory).

To use it, make sure you have installed Python 3 for your distro. Then use pip to install the request and psutil libraries.
Open `cardano-log.py` and change the following parameters if necessary:

- CARDANO_NODE_HOST: hostname or ip of cardano-node (default: localhost)
- CARDANO_NODE_PORT: listening port of Prometheus (default: 12798)
- QUERY_INTERVAL: how often to query Prometheus (default: 10 seconds)

Copy `cardano-log.service` to `/etc/systemd/system`. Edit `cardano-log.service` to specify the path to `cardano-log.py` and to the
log file. It is recommended to run `cardano-node` as a separate user (default: User=cardano, Group=cardano). Change as necessary.
Start `cardano-log.service` and enable it to run automatically during boot:

```
systemctl start cardano-log
systemctl enable cardano-log
```

Now you can check the log file to analyze the metrics. Each line begins with a timestamp, folowed by a list of all defined metrics.
A new line is logged only if at least one of the metrics changed by a significant amount (called increment). The increment
is defined for each metric individually. You can rearrange, add or remove metrics as desired in the `cardano-log.py` script.
Metrics marked as separate will be displayed in a separate line and do not trigger the display of other metrics. This is useful
for logging slowly changing metrics that are not relevant in the context (e.g. epoch number). Metrics can be functional, in which
case their value is updated using a lambda closure (that may depend on other metrics). Metrics marked as hidden (visible=False)
will not be displayed. This is useful in reducing the verbosity of the log (while enabling functional metrics that depend on
them to provide a summary).

The default metrics are listed below:

- Epoch (separate): Epoch number
- Leader: Slots that passed a leader check (if block producer)
- Adopted: Blocks successfully minted during leader slots (but not necessarily adopted by other nodes)
- Checked (hidden): Slots during which a leader check was performed
- Missed (hidden): Slots missed for various reasons (e.g., garbage collection)
- Miss Rate (functional): Percent of missed slots ((Missed * 100) / (Missed + Checked))
- Within 1s/3s: Percent of blocks likely to be fetched within 1s/3s (each slot is one second).
- CPU (functional): CPU utilization during last QUERY_INTERVAL
- Live: Memory in use by data generated since the last garbage collection
- Heap: Memory reserved from the OS but not necessarily live
- Major #GC: Number of major garbage collections (causes missed slot leader checks)
- GC Wall: Total time spent in garbage collection (only relevant if using blocking GC).
