# Stormer

Wrappers for making load test more convienient.

## Features

- Start locust master and specified number of slaves at once.
- Overwrite test scripts on all remote machines with ease.
- Download remote file/directory to local path.

## Dependencies

Stormer is mainly based on [`locustio`](https://github.com/locustio/locust) and [`paramiko`](https://github.com/paramiko/paramiko/), you can install all dependencies through `requirements.txt`.

```bash
$ pip install -r requirements.txt --upgrade
```

## Usages

Currently, Stormer supports two subcommands.

```text
$ python main.py -h
usage: main.py [-h] {locust,sput} ...

Wrappers for making load test more convienient.

positional arguments:
  {locust,sput}  sub-command help
    locust       locust wrapper.
    sput         scp wrapper for putting files.

optional arguments:
  -h, --help     show this help message and exit
```

`locust` usage: Start locust master and specified number of slaves with one command.

```text
$ usage: main.py locust [-h] [-f LOCUSTFILE] [-P PORT] [--slaves_num SLAVES_NUM]

Start locust master and specified number of slaves with one command.

optional arguments:
  -h, --help            show this help message and exit
  -f LOCUSTFILE, --locustfile LOCUSTFILE
                        Specify locust file to run test.
  -P PORT, --port PORT, --web-port PORT
                        Port on which to run web host.
  --slaves_num SLAVES_NUM
                        Specify number of locust slaves.
```

`sput` usage: Copy local file/directory to remote machines and overwrite.

```text
$ python main.py sput -h
usage: main.py sput [-h] [--hostsfile HOSTSFILE] [--localpath LOCALPATH] [--remotepath REMOTEPATH]

Copy local file/directory to remote machines and overwrite.

optional arguments:
  -h, --help            show this help message and exit
  --hostsfile HOSTSFILE
                        Specify hosts file to handle.
  --localpath LOCALPATH
                        Specify localpath of file or directory to transfer.
  --remotepath REMOTEPATH
                        Specify remotepath of file or directory to transfer.
```

## Examples

Start locust master and 4 locust slaves.

```text
$ python main.py locust -f examples/demo_task.py --slaves_num 4
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

Copy local directory to all remote hosts.

```text
$ python main.py sput --hostsfile examples/hosts.yml --localpath examples --remotepa
th /root/examples
```