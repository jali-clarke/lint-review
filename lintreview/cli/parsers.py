import argparse

from lintreview.cli.handlers import (
    register_hook,
    remove_hook,
    register_org_hook,
    remove_org_hook
)


def create_parser():
    desc = """
    Command line utilities for lintreview.
    """
    parser = argparse.ArgumentParser(description=desc)

    commands = parser.add_subparsers(
        title="Subcommands",
        description="Valid subcommands")

    add_register_command(commands)
    add_unregister_command(commands)
    add_org_register_command(commands)
    add_org_unregister_command(commands)

    return parser


def add_register_command(subcommands_parser):
    desc = (
        "Register webhooks for a given user & repo\n"
        "The installed webhook will be used to trigger lint\n"
        "reviews as pull requests are opened/updated.\n"
    )

    register = subcommands_parser.add_parser('register', help=desc)
    register.add_argument(
        '-u',
        '--user',
        dest='login_user',
        help="The OAuth token of the user that has admin rights to the repo "
             "you are adding hooks to. Useful when the user "
             "in settings is not the administrator of "
             "your repositories.")
    register.add_argument('user',
                          help="The user or organization the repo is under.")
    register.add_argument('repo',
                          help="The repository to install a hook into.")
    register.set_defaults(func=register_hook)


def add_unregister_command(subcommands_parser):
    desc = "Unregister webhooks for a given user & repo.\n"

    remove = subcommands_parser.add_parser('unregister', help=desc)
    remove.add_argument(
        '-u', '--user',
        dest='login_user',
        help="The OAuth token of the user that has admin rights to the repo "
             "you are removing hooks from. Useful when the "
             "user in settings is not the administrator of "
             "your repositories.")
    remove.add_argument('user',
                        help="The user or organization the repo is under.")
    remove.add_argument('repo',
                        help="The repository to remove a hook from.")
    remove.set_defaults(func=remove_hook)


def add_org_register_command(subcommands_parser):
    desc = (
        "Register webhook for a given organization\n"
        "The installed webhook will be used to trigger lint\n"
        "reviews as pull requests are opened/updated.\n"
    )

    register = subcommands_parser.add_parser('org-register', help=desc)
    register.add_argument(
        '-u',
        '--user',
        dest='login_user',
        help="The OAuth token of the user that has admin rights to the org "
             "you are adding hooks to. Useful when the user "
             "in settings is not the administrator of "
             "your organization.")
    register.add_argument('org_name',
                          help="The login name of the organization.")
    register.set_defaults(func=register_org_hook)


def add_org_unregister_command(subcommands_parser):
    desc = "Unregister webhooks for a given organization.\n"

    remove = subcommands_parser.add_parser('org-unregister', help=desc)
    remove.add_argument(
        '-u', '--user',
        dest='login_user',
        help="The OAuth token of the user that has admin rights to the org "
             "you are removing hooks from. Useful when the "
             "user in settings is not the administrator of "
             "your organization.")
    remove.add_argument('org_name',
                        help="The login name of the organization.")
    remove.set_defaults(func=remove_org_hook)
