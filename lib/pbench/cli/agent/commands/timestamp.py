import time

import click


@click.command()
def timestamp():
    stdin = click.get_text_stream("stdin").read()
    for line in stdin.splitlines():
        print("%s:%s" % (time.time_ns(), line))
