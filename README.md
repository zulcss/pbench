# Pbench
A Benchmarking and Performance Analysis Framework

The code base includes three sub-systems. The first is the collection agent,
`pbench-agent`, responsible for providing commands for running benchmarks
across one or more systems, while properly collecting the configuration data
for those systems, and specified telemetry or data from various tools (`sar`,
`vmstat`, `perf`, etc.).

The second sub-system is the `pbench-server`, which is responsible for
archiving result tar balls, indexing them, and unpacking them for display.

The third sub-system is the `dashboard`, and `web-server` JS and CSS files,
used to display various graphs and results, and any other content generated by
the `pbench-server`, or by the `pbench-agent` during benchmark and tool
post-processing steps.

## How is it installed?
Instructions on installing `pbench-agent`, can be found
in the [PBench agent installation](http://distributed-system-analysis.github.io/pbench/doc/agent/installation.html) guide.

For Fedora, CentOS, and RHEL users, we have made available [COPR
builds](https://copr.fedoraproject.org/coprs/ndokos/pbench/) for the
`pbench-agent`, `configtools`, `pbench-server`, `pbench-web-server`
and some benchmark and tool packages.

This assumes that somebody has already installed the server bits. The
procedure to do that is described in the [PBench Server
Installation](http://distributed-system-analysis.github.io/pbench/doc/server/installation.html)
guide.

You can install the `web-server` sub-system on the machine from where you
want to run the `pbench-agent`. That allows you to view the graphs before
sending the results to the server, or even if there is no server to which to
send the results. See the [PBench web server installation](http://distributed-system-analysis.github.io/pbench/doc/server/pbench-web-server.html) guide.

You might want to browse through the [rest of the documentation](http://distributed-system-analysis.github.io/pbench/doc/).

## How do I use pbench?
Refer to the [PBench User Guide](http://distributed-system-analysis.github.io/pbench/doc/agent/user-guide.html).

TL;DR? See [TL;DR - How to set up pbench and run a benchmark
](http://distributed-system-analysis.github.io/pbench/doc/agent/user-guide.html#org9c5bc26) of the
[PBench User
Guide](http://distributed-system-analysis.github.io/pbench/doc/agent/user-guide.html) for a
super quick set of introductory steps.

## Where is the source kept?
The latest source code is at
https://github.com/distributed-system-analysis/pbench.

## Is there a mailing list for discussions?

Yes, we use [Google Groups](https://groups.google.com/forum/#!forum/pbench)

## Is there a place to track current and future work items?
Yes, we are using GitHub [Projects](https://github.com/distributed-system-analysis/pbench/projects).
Please find projects covering the [Agent](https://github.com/distributed-system-analysis/pbench/projects/2),
[Server](https://github.com/distributed-system-analysis/pbench/projects/3),
[Dashboard](https://github.com/distributed-system-analysis/pbench/projects/1), and a project that is named
the same as the current [milestone](https://github.com/distributed-system-analysis/pbench/milestones).
