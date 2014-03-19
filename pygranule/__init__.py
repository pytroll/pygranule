
import os
from .file_name_parser import FileNameParser

from .granule_filter import GranuleFilterError
from .orbital_granule_filter import OrbitalGranuleFilter
from .periodic_granule_filter import PeriodicGranuleFilter

from .file_set import FileSet
from .transfer_file_set import TransferFileSet

def get_granule_filters(config_file_path=None):
    """ reads config file and generates granule filters """
    if config_file_path is None:
        try:
            config_file_path = os.environ['PYGRANULE_CONFIG_PATH']
        except KeyError:
            raise GranuleFilterError( "pygranule config file path missing.  Has the 'PYGRANULE_CONFIG_PATH' environment variable been set?")

    # open config file...
    config = {}
    try:
        for filename in os.listdir(config_file_path):
            if filename.split('.')[-1] == "config":
                f = open(config_file_path+"/"+filename,"r")       
                config_sections = parse_config_file_RFC822(f)
                f.close()
                # prepare aquisition configuration objects
                for section_name in config_sections.keys():
                    if config_sections[section_name]['type'] == "orbital":
                        config[section_name] = OrbitalGranuleFilter(config_sections[section_name])
                    elif config_sections[section_name]['type'] == "periodic":
                        config[section_name] = PeriodicGranuleFilter(config_sections[section_name])
                    else:
                        raise GranuleFilterError( "pygranule config type: "
                                                      +config_sections[section_name]['type']
                                                      +" unknown")

    except IOError:
        print "failed to open config file,", config_file_path
        return []

    return config

def parse_config_file_RFC822(fstream):
    import ConfigParser
    config = ConfigParser.RawConfigParser()
    config.readfp(fstream)
    config_sections={}
    for section_name in config.sections():
        section_config = dict(config.items(section_name))
        section_config['config_name'] = section_name
        config_sections[section_name]=section_config
    return config_sections

