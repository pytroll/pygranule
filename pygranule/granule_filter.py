
from collections import OrderedDict
from datetime import datetime, timedelta
from .time_tools import floor_granule_datetime
from .file_name_parser import FileNameParser, file_name_translator
from .local_file_access_layer import LocalFileAccessLayer
from .file_set import FileSet

import os

class GranuleFilter(object):
    id = 0 # object id. - static class var.
    """
    class that holds acquisition definitions
    filters satellite granules.
    """
    def __init__(self,input_config):
        GranuleFilter.id += 1
        # declare config attributes
        self.config = OrderedDict([
            ('id',self.id),
            ('config_name',None),
            ('sat_name',None),
            ('sat_id',None),
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
        self.file_name_parser = FileNameParser(self.config['file_source_pattern'],
                                               self.config['subsets'])
        self.source_file_name_parser = self.file_name_parser

        # instanciate destination file name parser
        self.destin_file_name_parser = FileNameParser(self.config['file_destination_pattern'],
                                                      self.config['subsets'])

        # instanciate file access parser, if set
        if self.config['protocol'] == "local":
            self.file_access_layer = LocalFileAccessLayer()
        
    def validate(self,filename):
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
        t_flrd = floor_granule_datetime(t,self.get_time_step(),self.get_time_step_offset())
        if t_flrd != t:
            return False
        # check aoi intersect
        if not self.check_sampling_from_time(t):
            return False
        # success
        return True


    def filter(self,fileset):
        """
        Filters a FileSet of input filenames, returning
        only those that pass the validator test (see validate).
        """
        f = []
        for path in fileset.paths():
            if self.validate(path):
                f.append(path)
        return FileSet(f)

    def check_sampling_from_time(self, start, period=None):
        """
        Function to be overridden by extended orbital granule versions of this class.
        Default behaviour is to return True.
        """
        return True

    def check_source(self):
        """
        Lists source directories 'remote filesystem'.
        Returns a FileSet of valid filename paths not 
        already in destination folder.
        If destination folder not configured, then
        simply returns all valid files.
        """
        ## SOURCE
        # expand pattern to list of source directories
        directories = self.file_name_parser.directories()

        fileset = FileSet()
        # check files in the directories
        for d in directories:
            fileset += self.file_access_layer.list_source_directory(d)

        # filter fileset
        fileset = self.filter(fileset)

        # get destination granule set
        if self.config['file_destination_pattern'] is not None:
            ## DESTINATION
            # expand pattern to list of destination directories
            dest_directories = self.destin_file_name_parser.directories()

            dest_fileset = FileSet()
            # check files in the directories
            for d in dest_directories:
                dest_fileset += self.file_access_layer.list_destination_directory(d)

            # translate destin. filenames to source filenames
            dest_fileset = filename_pattern_translator(dest_fileset, 
                                                       self.destin_file_name_parser,
                                                       self.source_file_name_parser)


            # drop files already at destination
            fileset = fileset.difference( dest_fileset )

            # put data into a TransferFileSet container,
            

        return fileset

    def __call__(self,fileset=None):
        if fileset is None:
            return self.check_source()
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

    def get_subset_dict(self):
        """ returns subset strings as dictionary tree """
        conf = self._validated_config('subsets')
        if conf is None:
            return None
        else:
            subset_dict = _dict_subset_expression(conf)
            
            return subset_dict

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
