# LocustWrapper
A wrapper for making locustio more convienient to use.

## usage

```text
$ python main.py -h
usage: main.py [-h] [-f LOCUSTFILE] [--slaves_num SLAVES_NUM]

A wrapper for making locustio more convienient to use.

optional arguments:
  -h, --help            show this help message and exit
  -f LOCUSTFILE, --locustfile LOCUSTFILE
                        Specify locust file to run test.
  --slaves_num SLAVES_NUM
                        Specify number of locust slaves.
```

## example

```text
$ python main.py -f examples/demo_task.py --slaves_num 4
[2017-02-26 10:52:04,875] Leos-MacBook-Air.local/INFO/logger: Starting Locust 0.8a2
[2017-02-26 10:52:04,897] Leos-MacBook-Air.local/INFO/logger: Starting web monitor at *:8089
[2017-02-26 01:32:15,757] Leos-MacBook-Air.local/INFO/locust.runners: Client 'Leos-MacBook-Air.local_9cfcb5acf942af4b52063c138952a999' reported as ready. Current
ly 1 clients ready to swarm.
[2017-02-26 01:32:15,757] Leos-MacBook-Air.local/INFO/locust.runners: Client 'Leos-MacBook-Air.local_0dba26cc993de413436db0f854342b9f' reported as ready. Current
ly 2 clients ready to swarm.
[2017-02-26 01:32:15,758] Leos-MacBook-Air.local/INFO/locust.runners: Client 'Leos-MacBook-Air.local_2d49585a20f6bcdca33b8c6179fa0efb' reported as ready. Current
ly 3 clients ready to swarm.
[2017-02-26 01:32:15,782] Leos-MacBook-Air.local/INFO/locust.runners: Client 'Leos-MacBook-Air.local_cc9d414341823d0e9421679b5f9dd4c4' reported as ready. Current
ly 4 clients ready to swarm.
```
