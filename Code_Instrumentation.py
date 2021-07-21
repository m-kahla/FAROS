import yaml
from hotness import *

# Takes 1- list of python dict each has line_start,line_end,function_start,function_end keys and their vals
# 		2- new file path after adding instrumentations, this is a value for "outfile" value in yaml file
#		3- path for the output yaml file
#		4- OPTIONAL: the value for the "header" field in the yaml file, which is header of instrumentation lib
# Outputs a YAML file that is used by a FAROS clang tool to insert instrumentation funcs
def generate_instrumentation_regions_single_yaml_file(instrumentation_regions, new_instrumented_file_path, yaml_outfile_path, include_file="FarosInstrument.h"):
	
	# no instrumentation regions to dump
	if len(instrumentation_regions) == 0:
		return

	yaml_out_dict={}  
 
	yaml_out_dict["outfile"] = new_instrumented_file_path
	yaml_out_dict["header"] = include_file
	yaml_out_dict["instrumentations"] = instrumentation_regions
	
	# dump yaml to file
	f = open(yaml_outfile_path,'w')
	yaml.dump(yaml_out_dict,f, default_flow_style=False)
	f.close()


# get list of instrumentation regions, each represented by dict, for certain (one and only one) cpp file
# input is a dict of missed optimizations for one file
def get_instrumentation_regions_list():
	return

# takes missed optimzations yaml file for single build (or multi builds?) and generate yaml files that contains instrumentation
# configuration for each instrumented file
# returns a list of paths of generated yaml file
# OUTPATH OF A FILE AFTER INSTRUMENTATION SHOULD BE THE FILE ITSELF. We dont need the mainfile anymore in this build.
# THE GENERATION REPORTS SHOULD HAVE THE OLD FILES. right? yes but is this the right decision?
def gen_instrumentations_yaml_files():
	# get each file separately
	# make dict [
	return





def dict_to_list_discard_keys(someDict):
    someList = []
    for key in someDict:
        someList.append(someDict[key])
    
    return someList

def insert_instrumentations(original_build_dir, instrumented_build_dir, config, program):

    report_dir = './reports/' + program + '/' + 'instrumentations' + '/'
    os.makedirs(report_dir, exist_ok=True)
    

    # get a dict where each key is a file name, and each value is dict of hot missed optimizations in this file
    # hot missed opts are opts that were missed in hottest functions
    hottest_opts_dict = get_hottest_opts_dict(config, program)
    

    for source_file_path in hottest_opts_dict:

        # skip the files that are not in the build dir
        if original_build_dir not in source_file_path:
            continue
        
        new_source_file_path = source_file_path.replace(original_build_dir, instrumented_build_dir,1)
        #turn the dict to list to ease the writing/reading of yaml file, and also because we dont need the keys
        instrumentation_regions = dict_to_list_discard_keys(hottest_opts_dict[source_file_path])
        
        source_file_name = source_file_path.split('/')[-1] 
        instrumentation_regions_yaml_file_path = report_dir + source_file_name + '-instrumented-regions.yaml'
        
        generate_instrumentation_regions_single_yaml_file(instrumentation_regions, new_source_file_path, instrumentation_regions_yaml_file_path)
        
        # call the clang action
        
        
        
        
        
    







def test_generate_instrumentation_regions_single_yaml_file():
	instrumentation_regions = [{"line_start":3, "line_end":4,"function_start":"custum_s1()","function_end":"custum_end1()"},
						{"line_start":8, "line_end":8,"function_start":"custum_s2()","function_end":"custum_end2()"},
						{"line_start":15, "line_end":20,"function_start":"custum_s3()","function_end":"custum_end3()"}]

	new_instrumented_file_path= "newfile.cpp"
	yaml_outfile_path = "trial1.yaml"

	generate_instrumentation_regions_single_yaml_file(instrumentation_regions, new_instrumented_file_path, yaml_outfile_path)

