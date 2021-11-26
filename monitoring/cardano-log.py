#!/usr/bin/python

CARDANO_NODE_HOST='localhost'
CARDANO_NODE_PORT=12798
QUERY_INTERVAL=10

import requests, time, datetime, psutil

class Metric:
    def __init__(self, name, print_name, kind='normal', increment=0.0, initial=0.0):
        self.name = name
        self.print_name = print_name
        self.value = initial
        self.last_value = self.value
        self.increment = increment
        if kind == 'size':
            self.formatter = lambda x: "%.2f GiB" % (x / 2**30)
        elif kind == 'time':
            self.formatter = lambda x: "%d ms" % int(x)
        elif kind == 'probability':
            self.formatter = lambda x: "%.2f%%" % (x * 100)
        else:
            self.formatter = lambda x: "%d" % int(x)

    def update(self, value):
        self.value = value
        if abs(self.value - self.last_value) > self.increment:
            self.last_value = self.value
            return True
        else:
            return False

    def __str__(self):
        return "%s: %s" % (self.print_name, self.formatter(self.value))

class PrometheusMetrics:
    def __init__(self, host, port):
        self.url = "http://%s:%d/metrics" % (host, port)
        self.metrics = {}

    def add_metric(self, metric):
        self.metrics[metric.name] = metric

    def __str__(self):
        try:
            r = requests.post(self.url)
        except:
            return ""
        increment = False
        for line in r.text.splitlines():
            name, val = line.partition(' ')[::2]
            if name in self.metrics:
                increment = self.metrics[name].update(float(val)) or increment
        if increment:
            return ', '.join(str(metric) for metric in self.metrics.values())
        else:
            return ""

if __name__ == "__main__":
    pid = None
    prometheus = PrometheusMetrics(CARDANO_NODE_HOST, CARDANO_NODE_PORT)
    prometheus.add_metric(Metric('cardano_node_metrics_Forge_forged_int', 'Leader'))
    prometheus.add_metric(Metric('cardano_node_metrics_Forge_adopted_int', 'Adopted'))
    prometheus.add_metric(Metric('cardano_node_metrics_Forge_forge_about_to_lead_int', 'Checked', kind='normal', increment = float('inf')))
    prometheus.add_metric(Metric('cardano_node_metrics_slotsMissedNum_int', 'Missed'))
    prometheus.add_metric(Metric('cardano_node_metrics_blockfetchclient_blockdelay_cdfOne', 'Fetch 1s', kind='probability', increment = 0.05))
    prometheus.add_metric(Metric('cardano_node_metrics_RTS_gcLiveBytes_int', 'Live', kind='size', increment = 256 * 2**20))
    prometheus.add_metric(Metric('cardano_node_metrics_RTS_gcHeapBytes_int', 'Heap', kind='size', increment = 256 * 2**20))
    prometheus.add_metric(Metric('cardano_node_metrics_RTS_gcMajorNum_int', 'Major #GC'))
    prometheus.add_metric(Metric('rts_gc_gc_wall_ms', 'GC Wall', kind='time', increment = float('inf')))

    while True:
        time.sleep(QUERY_INTERVAL)
        now = datetime.datetime.now().strftime("[%d/%m/%Y %H:%M:%S]")
        if pid == None:
            for proc in psutil.process_iter():
                if 'cardano-node' in proc.name():
                    pid = proc.pid
            if pid != None:
                print("%s Node up, new pid %d" % (now, pid), flush=True)
            else:
                continue
        else:
            if not psutil.pid_exists(pid):
                print("%s Node down, last pid: %d" % (now, pid), flush=True)
                pid = None
                continue
        metrics_str = str(prometheus)
        if metrics_str != "":
            print("%s %s" % (now, metrics_str), flush=True)
