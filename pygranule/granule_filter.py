
from collections import OrderedDict
from datetime import datetime, timedelta
from .time_tools import floor_granule_datetime
from .file_name_parser import FileNameParser, file_name_translator
from .local_file_access_layer import LocalFileAccessLayer
from .ssh_file_access_layer import SSHFileAccessLayer
from .bidict import BiDict
from .granule_bidict import GranuleBiDict

from abc import ABCMeta, abstractmethod

import os


class GranuleFilter(object):
    id = 0 # object id. - static class var.
    """
    class that holds acquisition definitions
    filters satellite granules.
    """
    __metaclass__ = ABCMeta
    def __init__(self,input_config):
        GranuleFilter.id += 1
        # declare config attributes
        self.config = OrderedDict([
            ('id',self.id),
            ('config_name',None),
            ('sat_name',None),
            ('sat_id',None),
            ('instrument',None),
            ('type',None),
            ('protocol',None),
            ('server',None),
            ('file_source_pattern',None),
            ('time_stamp_alignment',0.0),
            ('granule_time_step',None),
            ('granule_time_offset',None),
            ('time_step',None),
            ('time_step_offset',None),
            ('subsets',None),
            ('area_of_interest',None),
            ('point_of_interest',None),
            ('pass_time_duration',None),
            ('file_destination_pattern',None)
            ])

        # set configuration
        for key in input_config:
            if key in self.config:
                if input_config[key] !=  "": 
                    self.config[key] = input_config[key]
            else:
                raise KeyError("Invalid configuration key '%s'"%(key))

        # if destination pattern is directory,
        # fill out with file source patter
        if self.config['file_destination_pattern'] is not None:
            if self.config['file_destination_pattern'][-1] == '/':
                self.config['file_destination_pattern'] = self.config['file_destination_pattern'] + os.path.basename(self.config['file_source_pattern'])
            

        # instanciate source file name parser
        self.source_file_name_parser = None
        self.file_name_parser = None
        if self.config['file_source_pattern'] is not None:
            self.file_name_parser = FileNameParser(self.config['file_source_pattern'],
                                                   self.config['subsets'])
            self.source_file_name_parser = self.file_name_parser

        # instanciate destination file name parser
        self.destin_file_name_parser = None
        if self.config['file_destination_pattern'] is not None:
            self.destin_file_name_parser = FileNameParser(self.config['file_destination_pattern'],
                                                          self.config['subsets'])

        # instanciate file access parser, if set
        if self.config['protocol'] == "local":
            self.file_access_layer = LocalFileAccessLayer()
        elif self.config['protocol'] == "sftp":
            server = self.config['server']
            host, user, passwd = _parser_server_string(server)
            self.file_access_layer = SSHFileAccessLayer(host,user,passwd)
        
    def validate(self,filename, with_aoi=True):
        """
        Checks if filename matches source file name patter,
        and granulation pattern
        and area of interest intersect.
        Returns True or False.
        """
        # check file name pattern
        if not self.file_name_parser.validate_filename(filename):
            return False
        # check granulation
        t = self.file_name_parser.time_from_filename(filename)
        t_flrd = floor_granule_datetime(t, self.get_time_step(), self.get_time_step_offset())
        if t_flrd != t:
            return False
        # check aoi intersect
        if with_aoi:
            if not self.check_sampling_from_time(t):
                return False
        # success
        return True


    def filter(self, filepaths, with_aoi=True):
        """
        Filters a list of input file paths, returning
        only those that pass the validator test (see validate).
        Returns a GranuleBiDict object.
        """
        reduced_list = []
        for path in filepaths:
            if self.validate(path, with_aoi=with_aoi):
                reduced_list.append(path)

        # returned GranuleBiDict
        return self.translate(reduced_list)
        
    def translate(self, filepaths, reverse=False):
        """
        Translate input list of filepaths to destination.
        Return result as GranuleBiDict.
        """
        destin_list = self._translate(filepaths, reverse=reverse)
        if destin_list is None:
            pairs = dict( (x,None) for i, x in enumerate(filepaths) )
        else:
            pairs = dict( (x,destin_list[i]) for i, x in enumerate(filepaths) )   
        return GranuleBiDict(pairs, gf_parent=self)


    def _translate(self, filepaths, reverse=False):
        """
        Translate source file name to destination filename list
        """
        if self.destin_file_name_parser is not None and self.source_file_name_parser is not None:
            if reverse:
                return file_name_translator(filepaths, 
                                            self.destin_file_name_parser,
                                            self.source_file_name_parser)
            else:
                return file_name_translator(filepaths, 
                                            self.source_file_name_parser,
                                            self.destin_file_name_parser)
        else:
            return None

    @abstractmethod
    def fill_sampling(self, filepath):
        """
        Function to be overridden by extended versions of this class.
        For a valid input filepath, it should fill in the filepaths
        that complete the sampling as defined by the config.
        
        NOTE: In case of orbital type filters, it would fill in all missing 
        subsets, and granule that complete a satellite pass over the AOI.
        """
        pass

    @abstractmethod
    def show(self, filepaths):
        """
        If provided, shows an image for the area extent of the granules,
        and the target area.
        """
        pass

    @abstractmethod
    def check_sampling_from_time(self, start, period=None):
        """
        Function to be overridden by extended an orbital granule version of this class.
        Returns True or False
        """
        pass

    def list_source(self, t = datetime.now(), with_aoi=True):
        """
        Lists source directorie(s) 'remote filesystem'.
        Returns validated filename paths as
        BiDict object, mapping source file names
        to the equivalent destination file names.

        If directory pattern contains a date, then
        the datetime argument must be used.
        """
        # expand pattern to list of source directories
        directories = self.source_file_name_parser.directories(t = t)

        filelist = []
        # check files in the directories
        for d in directories:
            filelist += self.file_access_layer.list_source_directory(d)

        # filter filelist
        filtered_bidict = self.filter(filelist, with_aoi=with_aoi)

        return filtered_bidict


    def list_destination(self, t = datetime.now()):
        """
        Lists destination directorie(s).
        Returns filename paths as BiDict object, 
        mapping destination file paths to the 
        assosiated destination file names.

        If directory pattern contains a date, then
        the datetime argument must be used.
        """
        # expand pattern to list of source directories
        directories = self.destin_file_name_parser.directories(t = t)

        destin_list = []
        # check files in the directories
        for d in directories:
            destin_list += self.file_access_layer.list_local_directory(d)

        # map file names to source file name paths
        source_list = file_name_translator(destin_list, 
                                           self.destin_file_name_parser,
                                           self.source_file_name_parser)
        # return BiDict
        return BiDict(dict(zip(destin_list, source_list)))

    def list_new(self, t = datetime.now() ):
        """
        Checks source folders for validated granules and 
        returns a BiDict of all 'new files', 
        not found in destination folder. 

        This method is particularly useful in periodic 
        triggering of fetching any new data.
        """
        # check source
        source_files = self.list_source(t = t)

        # check if files at destination
        for sfile in source_files:
            dfile = source_files[sfile]
            if self.file_access_layer.check_for_local_file(dfile):
                source_files.remove(sfile)

        # return remaining files as BiDict
        return source_files

    def __call__(self,fileset=None):
        if fileset is None:
            return self.list_source()
        else:
            return self.filter(fileset)

    def __getitem__(self,key):
        return self.config[key]

    def __str__(self):
        string=""
        string+="GranuleFilter:\n"
        for key in self.config:
            string+="   %s: %s\n"%(key,str(self.config[key]))
        return string

    def _validated_config(self,key):
        """ use this function to get validated data from the config dict """
        if key == 'somekey':
            #if self.config[key] is not None and _is_balanced_braces(self.config[key]) is False:
            #    raise SyntaxError("Unbalanced braces in config key %s: %s"%(key,self.config[key]))
            #else:
            return self.config[key]
        else:
            return self.config[key]

    def get_time_step(self):
        str_splt = self._validated_config("time_step").split(":")
        h = int(str_splt[0])
        m = int(str_splt[1])
        s = int(str_splt[2])
        return timedelta(hours=h,minutes=m,seconds=s)

    def get_time_step_offset(self):
        str_splt = self._validated_config("time_step_offset").split(":")
        h = int(str_splt[0])
        m = int(str_splt[1])
        s = int(str_splt[2])
        return timedelta(hours=h,minutes=m,seconds=s)

    def get_area_of_interest(self):
        aoi=[]
        if self._validated_config("area_of_interest") is not None:
            for s in self._validated_config("area_of_interest").replace(" ","").replace("),",");").split(";"):
                splt = s.strip().split(",")
                aoi.append(( float(splt[0][1:]), float(splt[1][:-1]) ))
        return aoi

    get_aoi = get_area_of_interest



class GranuleFilterError(Exception):
    def __init__(self,value):
        self.value = value
    def __str__(self):
        return repr(self.value)


def _parser_server_string(s):
    host = s.split("@")[-1]
    user = s.split("@")[0].split(':')[0]
    try: 
        passwd = s.split("@")[0].split(':')[1]
    except IndexError:
        passwd = None
    return host, user, passwd
    
