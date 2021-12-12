# cardano-light-tools

<img src="image/logo.jpg" width="50%" height="50%" alt="Logo">
This repository includes a set of lightweight tools to operate and maintain a Cardano Stake Pool.

## Monitoring

This is a simple monitoring script that logs relevant metrics directly into a text file in human-readable form.
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

The default metrics are listed below:

- Leader: Slots that passed a leader check (if block producer)
- Adopted: Blocks successfully minted during leader slots (but not necessarily adopted by other nodes)
- Checked: Slots during which a leader check was performed
- Missed: Slots missed for various reasons (e.g., garbage collection)
- Live: Memory in use by data generated since the last garbage collection
- Heap: Memory reserved from the OS but not necessarily live
- Major #GC: Number of major garbage collections (causes missed slot leader checks)
- GC Wall: Total time spent in garbage collection (only relevant if using blocking GC).
- Within 1s/3s: Percent of blocks likely to be fetched within 1s/3s (each slot is one second).
