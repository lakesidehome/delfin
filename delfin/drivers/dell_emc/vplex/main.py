import sys
import argparse
import util
from delfin.drivers.dell_emc.vplex.vplexapi import VPlexApi

__author__ = "Farooq Khan"
__copyright__ = "Copyright (c) 2012 EMC Corporation"
__version__ = "D20.0.0.0"
__status__ = "Sample Code"
SETTINGS_FILE = "settings.cfg"


def configureSettings(args):
    config = util.readConfig(SETTINGS_FILE)
    existing_host = None
    existing_port = None
    existing_username = None
    existing_outputas = None
    if config:
        existing_host = config.host
        existing_port = config.port
        existing_username = config.username
        existing_outputas = config.outputas
        new_host = util.promptConfig('VPLEX Management Server Address', existing_host)
        new_port = util.promptConfig('VPLEX Management Server Port', existing_port)
        new_username = util.promptConfig('VPLEX User Account', existing_username)
        new_password = util.promptConfig('VPLEX User Password', None)
        new_outputas = util.promptConfig('Output Response as XML/JSON', existing_outputas)
        util.writeConfig(SETTINGS_FILE, new_host, new_port, new_username, new_password,
                         new_outputas)
        print("Successfully created settings.cfg")


# Cluster Subcommands
def clusterListAll(args):
    config = util.readConfigOrFail(SETTINGS_FILE)
    vplexapi = VPlexApi(config)
    vplexapi.clusterListAll()


def clusterStatus(args):
    config = util.readConfigOrFail(SETTINGS_FILE)
    vplexapi = VPlexApi(config)
    vplexapi.clusterStatus()


# Canned Subcommands
def autoProvision(args):
    config = util.readConfigOrFail()
    vplexapi = VPlexApi(config)
    storageVolName = args.useStorageFrom
    deviceSuffix = args.deviceSuffix
    vplexapi.autoProvision(storageVolName, deviceSuffix)


#########################################################
# The main function
#########################################################
def main(argv):
    p = argparse.ArgumentParser(description='Enables Remote Execution of VPLEX CLI Commands via VPLEX Restful API')
    sp = p.add_subparsers()
    # General Commands
    p.add_argument('--version', action='version', version='%(prog)s ' + __version__)
    p_config = sp.add_parser('configuresettings', help='Configures various settings required by other commands')
    p_config.set_defaults(func=configureSettings)
    # Cluster Subcommands

    sp_cluster = sp.add_parser('cluster')
    ssp_cluster = sp_cluster.add_subparsers()
    sp_clusterlistall = ssp_cluster.add_parser('listall', help='List all available clusters')
    sp_clusterlistall.set_defaults(func=clusterListAll)
    sp_clusterstatus = ssp_cluster.add_parser('status',
                                              help='Displays a cluster\'s operational status and health state.')
    sp_clusterstatus.set_defaults(func=clusterStatus)
    # Canned Subcommands
    p_autoprovision = sp.add_parser('autoprovision', help='autoprovision the specified storage volume')
    p_autoprovision.add_argument('-s', '--useStorageFrom')
    p_autoprovision.add_argument('-d', '--deviceSuffix')
    p_autoprovision.set_defaults(func=autoProvision)
    args = p.parse_args()
    args.func(args)


    if __name__ == "__main__":
        main(sys.argv[1:])
