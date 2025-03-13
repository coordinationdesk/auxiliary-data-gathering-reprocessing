

class RequestGenerator:

    def __init__(self):
        self.domain = "g"
        self._dataset = 'cams-global-atmospheric-composition-forecasts'
        # self.repres = "gg"
        # self.gaussian = "reduced"
        # self.grid = "640"
        # self.classid = "od"
        self.date_begin = "2015-06-23"
        self.date_end = "2015-06-30"
        # self.expver = "1"
        # self.levelist = "1000"
        # self.levtype = "sfc"
        self.param_list = ["206.128", "137.128", "151.128"]
        #self.step = ["9","12","15","18","21",
        #   "24","27","30","33","36","39","42","45","48"]
        #self.stream = "oper"
        self.time_list = ["00:00:00","12:00:00"]
        #self.type = "fc"
        self.type = "forecast"
        self.target = "2015-06/result1.grib"
    @property
    def dataset(self):
        return self._dataset
    
    def request_as_dict(self):
        # TODO Build string for Date interval
        # '2023-03-27/2023-03-28'
        # TODO: Check that dates are string in correct format
        date_range="{0}/{1}".format(self.date_begin, self.date_end) if self.date_end is not None else self.date_begin
        return {
            'date': date_range,
            'type': self.type,
            'data_format': 'grib',
            'variable': self.param_list,
            'time': self.time_list, # TODO: check that passed time values are correct
            'leadtime_hour': '0',
        }

    def concat_list(lst):
        # "/".join(lst)
        if len(lst) == 0:
            return ""
        else:
            res = lst[0]
            for f in range(1,len(lst)):
                res = res + "/"+lst[f]
            return res

    def write_to_file(self, filename):
        with open(filename,"w") as f:
            f.write("retrieve,")
            f.write("\n")
            if self.domain:
                f.write("  domain="+self.domain+",")
                f.write("\n")
                f.write("  repres="+self.repres+",")
                f.write("\n")
                f.write("  gaussian="+self.gaussian+",")
                f.write("\n")
            if self.dataset:
                f.write("  dataset=" + self.dataset + ",")
                f.write("\n")
            f.write("  grid="+self.grid+",")
            f.write("\n")
            f.write("  class="+self.classid+",")
            f.write("\n")
            if self.date_end:
                f.write("  date="+self.date_begin+"/to/"+self.date_end+",")
            else:
                f.write("  date=" + self.date_begin + ",")
            f.write("\n")
            f.write("  expver="+self.expver+",")
            f.write("\n")
            f.write("  levelist="+self.levelist+",")
            f.write("\n")
            f.write("  levtype="+self.levtype+",")
            f.write("\n")
            f.write("  param="+RequestGenerator.concat_list(self.param_list)+",")
            f.write("\n")
            if self.step:
                f.write("  step="+RequestGenerator.concat_list(self.step)+",")
                f.write("\n")
            f.write("  stream="+self.stream+",")
            f.write("\n")
            f.write("  time="+RequestGenerator.concat_list(self.time_list)+",")
            f.write("\n")
            f.write("  type="+self.type+",")
            f.write("\n")
            f.write("  target=\""+self.target+"\"")
            f.write("\n")
            f.close()



