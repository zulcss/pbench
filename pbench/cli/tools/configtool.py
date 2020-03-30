#!/usr/bin/env python

import os
import sys

from pbench.common import configtools


def get_pbench_environment():
    if os.environ.get("_PBENCH_SERVER_CONFIG"):
        return "_PBENCH_SERVER_CONFIG"
    if os.environ.get("_PBENCH_AGENT_CONFIG"):
        return "_PBENCH_AGENT_CONFIG"
    else:
        sys.exit(1)


def main():
    opts, args = configtools.parse_args(
        configtools.options,
        usage="Usage: getconf.py [options] <item>|-a <section> [<section> ...]",
    )
    cfg = get_pbench_environment()
    conf, files = configtools.init(opts, cfg)
    status = configtools.main(conf, args, opts, files)
    sys.exit(status)


if __name__ == "__main__":
    main()
