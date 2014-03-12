
from collections import OrderedDict
from datetime import datetime, timedelta
from .time_tools import floor_granule_datetime
from .file_name_parser import FileNameParser
from .local_file_access_layer import LocalFileAccessLayer

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
            ('destination',None)
            ])

        # set configuration
        for key in input_config:
            if key in self.config:
                if input_config[key] !=  "": 
                    self.config[key] = input_config[key]
            else:
                raise KeyError("Invalid configuration key '%s'"%(key))

        # instanciate file name parser
        self.file_name_parser = FileNameParser(self.config['file_source_pattern'],self.config['subsets'])

        # instanciate file access parser, if set
        if self.config['protocol'] == "local":
            self.file_access_layer = LocalFileAccessLayer()
        
    def validate(self,filename):
        """
        Checks if filename matches file name patter,
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


    def filter(self,filenames):
        """
        Filters a list of input filenames, returning
        only those that pass the validator test (see validate).
        """
        f = []
        for filename in filenames:
            if self.validate(filename):
                f.append(filename)
        return f

    def check_sampling_from_time(self, start, period=None):
        """
        Function to be overridden by extended orbital granule versions of this class.
        Default behaviour is to return True.
        """
        return True

    def list_source(self):
        """
        List source directories 'remote filesystem'.
        Returns a list of available filename paths.
        """
        directories = self.file_name_parser.directories()
        files = []
        for d in directories:
            files += self.file_access_layer.list_source_directory(d)
        return files

    def __call__(self,filenames):
        return self.filter(filenames)

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
        if key == 'subsets':
            if self.config[key] is not None and _is_balanced_braces(self.config[key]) is False:
                raise SyntaxError("Unbalanced braces in config key %s: %s"%(key,self.config[key]))
            else:
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
