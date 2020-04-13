import click


def tool_clear_options(f):
    f = click.option(
        "-g",
        "--group",
        help="the group from which tools should be remvoed "
        "(the default group is 'default')",
    )(f)
    f = click.option(
        "-n",
        "--name",
        help="a specific tool to be removed. If no tool is specifed "
        "all toool in the group are removed",
    )(f)
    return f
