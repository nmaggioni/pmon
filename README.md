# pmon
A simple performance monitor for Unix processes that outputs scaled graphs.

```
usage: pmon.py [-h] [-v] [-t TIMEOUT] PID

positional arguments:
  PID                   The PID to monitor.

optional arguments:
  -h, --help            show this help message and exit
  -v, --verbose         Increase output verbosity.
  -t TIMEOUT, --timeout TIMEOUT
                        The duration of the monitoring in seconds.
```

![Sample output](https://raw.githubusercontent.com/nmaggioni/pmon/master/example.png)