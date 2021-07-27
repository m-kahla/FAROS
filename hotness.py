import subprocess
from subprocess import PIPE
import os
import operator
import yaml

import sys
sys.path.append('../opt-viewer')
import optrecord


# reads a perf report that is a product of the following command:
# perf report -b --sort symbol
# this report contains the symbols sorted by their % of usage
# it outputs a dict that has keys as symbols and vals as % of usage
def get_hot_symbols(report_path):
    symbols_usage = {}
    with open(report_path) as report_file:
        for line in report_file:
            if line[0] == '#':  # skip the header
                continue

            if line.strip() == '':  # skip empty lines
                continue
            # print(line)
            words = line.strip().split()
            percentage = words[0]
            symbol = ' '.join(words[3:])

            percentage = float(percentage[:-1])  # remove % and convert to float
            symbols_usage[symbol] = percentage

    return symbols_usage


# read perf annotate -P -l symbol and get hot lines in src file
# hot lines are lines that have more than 0.5%(0.005) of execution time of the function
# the function outputs a dict with key "srcfile:line" and value of percentage of time
def get_hotness_from_anno_file(anno_path, hotlines={}, symbol_percentage=100):
    skip_keywords = ['Sorted summary for file', '----------------------------']
    with open(anno_path) as anno_file:
        for line in anno_file:
            if line[0] == '#':  # skip the header
                continue

            if line.strip() == '':  # skip empty lines
                continue

            if 'Percent |	Source code & Disassembly of' in line:  # we only capture src code and terminate before disassembly code
                break

            # skip predefined lines
            skip_line = False
            for skip in skip_keywords:
                if skip in line:
                    skip_line = True
            # we cant use continue above because it will escape the inner loop
            if skip_line:
                continue

            # print(line)
            words = line.strip().split()
            percentage = float(words[0])
            srccode = ' '.join(words[1:])
            line_hotness = round(percentage * symbol_percentage / 100, 3)
            if srccode in hotlines:
                hotlines[srccode] += line_hotness
            else:
                hotlines[srccode] = line_hotness

    return hotlines


# @TODO add cwd as a , ALSO ADD relative and absolute percentages
# return the hotlines in the secfile of a symbol. Return only lines with usage time 0.5% or more
def get_symbol_hotness_in_srcfiles(symbol, symbol_percentage, hotlines={}, cwd=''):
    # create annotation file of the symbol
    annotation_file_name = "perf-annotate.tmp"
    exe = "perf annotate {} -P -l > {}".format(symbol, annotation_file_name)
    #print("executing command: {}".format(exe))
    p = subprocess.run(exe, cwd=cwd, shell=True, stdout=PIPE, stderr=PIPE)
    out = str(p.stdout.decode('utf-8', errors='ignore'))
    err = str(p.stderr.decode('utf-8', errors='ignore'))
    print(out, '\n\n', err)
    annotation_file_name = os.path.join(cwd, annotation_file_name)
    hotlines = get_hotness_from_anno_file(annotation_file_name, hotlines=hotlines, symbol_percentage=symbol_percentage)
    return hotlines


# generate report from perf data and return the hot symbols with their percentages
def get_hot_symbols_from_perf_data(binfile, perf_data_file='perf.data', cwd=''):
    report_file_name = "perf-report.tmp"
    exe = 'perf report --no-child -d {} -i {} --percentage "relative"  > {}'.format(binfile, perf_data_file,
                                                                                    report_file_name)
    print("executing command: {}".format(exe))
    p = subprocess.run(exe, cwd=cwd, shell=True, stdout=PIPE, stderr=PIPE)
    out = str(p.stdout.decode('utf-8', errors='ignore'))
    err = str(p.stderr.decode('utf-8', errors='ignore'))
    print(out, '\n\n', err)
    report_file_name = os.path.join(cwd, report_file_name)
    hot_symbols = get_hot_symbols(report_file_name)
    return hot_symbols


def get_hot_lines_percentage(binfile, cwd):
    symbols = get_hot_symbols_from_perf_data(binfile, cwd=cwd)
    print(symbols)
    print('\n\n\n\n\n\n\n')
    hotlines = {}
    for symbol in symbols:
        # hotlines=get_hotness_from_anno_file('trial')
        # skip symbols that are not in the main app
        if '@' in symbol:
            continue
        symbol_percentage = symbols[symbol]
        hotlines = get_symbol_hotness_in_srcfiles(symbol, symbol_percentage, hotlines=hotlines, cwd=cwd)

    return hotlines
    

# return the top k hottest functions according to perf.    
def top_k_hottest_funcs(k,bin_dir):
    report_file_name = os.path.join(bin_dir, "perf-report.tmp")
    hot_symbols = get_hot_symbols(report_file_name)
    k= min(k,len(hot_symbols))
    return sorted(hot_symbols.items(), key=operator.itemgetter(1),reverse=True)[:k]

# return top k hottest functions or if exisits, top N (N<K) functions that have usage more than X percent    
def top_k_or_percentage_hottest_funcs(k,percentage,bin_dir):
    report_file_name = os.path.join(bin_dir, "perf-report.tmp")
    hot_symbols = get_hot_symbols(report_file_name)
    k= min(k,len(hot_symbols))
    hot_symbols = sorted(hot_symbols.items(), key=operator.itemgetter(1),reverse=True)[:k] 
    total_usage = 0
    # search in the top k hottest functions to see if only some of them sums to  percentage or more.
    # if so, we return them
    for i in range(len(hot_symbols)):
        total_usage += hot_symbols[i][1]
        if total_usage >= percentage:
            hot_symbols = hot_symbols[:i+1]
            break
    # now convert the hot_symbols from list to dict again
    new_hot_symbols = {}
    for func in hot_symbols:
        func_name = func[0]
        new_hot_symbols[func_name] = 1
    
    return new_hot_symbols 

# function that adds optimizations from hot functions only to a dict.    
def add_hot_missed_opts(missed_opts_dict, report_file_path, hot_funcs):
    instrumentation_report_file = 'instrumentation_report' 
    captured_count = skipped_count = 0
    # read yaml_file and get the opts
    _, all_remarks, file_remarks = optrecord.get_remarks(report_file_path)
    total_count = len(all_remarks)
        
    
    # for each opt in yaml file, we get func, line, filename
    for remark in all_remarks:
        remark = all_remarks[remark]
        # only interested in Missed opts
        if remark.yaml_tag !='!Missed':
            continue
        remark_filename = remark.File
        remark_funcname = remark.DemangledFunctionName
        remark_line = remark.Line 

        # if func not in hot funcs we skip it
        if remark_funcname not in hot_funcs:
            skipped_count += 1
            continue
            
            
        # sometimes missed opts are at line 0. Skip them to avoid errors
        if remark_line < 1:
            skipped_count += 1
            continue        
    
        
        if remark_filename not in missed_opts_dict:
            missed_opts_dict[remark_filename] = {}
        #we make identifier: func:line_num and check if this identifier is already in missed_opts_dict[file]
        opt_identifier = "{}:{}:{}".format(remark_filename, remark_funcname, remark_line)
        if opt_identifier in missed_opts_dict[remark_filename]:
            skipped_count += 1
            continue
        
        # we add our opt to missed_opts_dict[opt file][opt identifier]
        single_opt = {}
        single_opt["line_start"] = int(remark_line)
        single_opt["line_end"] = int(remark_line)
        single_opt["function_start"] = 'defaultInstrumentBegin("{}", "{}")'.format(instrumentation_report_file, opt_identifier)
        single_opt["function_end"] = 'defaultInstrumentEnd("{}", "{}")'.format(instrumentation_report_file, opt_identifier)
         
        missed_opts_dict[remark_filename][opt_identifier] = single_opt
        captured_count += 1

    print('total optimizations count: {} , skipped Missed opts {}, captured Missed opts {}'.format(total_count, skipped_count, captured_count))
    return missed_opts_dict
    
# function that reads perf reports, and optimization reports, and return the hottest optimization misses    
def get_hottest_opts_dict(config, program,K=50,percentage=60):
    report_dir = './reports/' + program + '/'
    build_dicts = config[program]['build']
    
    
    # this is a dict of dicts, each key is a file path, and missed_opts_dict[file] is a dict having 
    # start and end lines and start and end functions
    missed_opts_dict={}
    for build in build_dicts:
        print (" finding hottest optimization misses in build: ",build)
        bin_dir = './bin/' + program + '/' + build + '/'
        report_file = report_dir+build+'.opt.yaml'
        #get top 50 hottest funcs or funcs that covers more than 60% of running time if they are less than 50 funcs
        hot_funcs = top_k_or_percentage_hottest_funcs(K, percentage, bin_dir)
        print('hot_funcs for build: ',build,':',hot_funcs)
        missed_opts_dict = add_hot_missed_opts(missed_opts_dict, report_file, hot_funcs)
                
    return missed_opts_dict


if __name__ == "__main__":
    #print(top_k_hottest_funcs(4,'../bin/LULESH3/seq'))
    #print(top_k_or_percentage_hottest_funcs(4,97,'../bin/LULESH3/seq'))
    '''missed_opts = add_hot_missed_opts({}, '../reports/LULESH3/omp.opt.yaml', '')
    for key in missed_opts:
        for key2 in missed_opts[key]:
            for key3 in missed_opts[key][key2]:
                print(key,':',key2,':',key3,':',missed_opts[key][key2][key3])'''
    '''hotlines=get_hot_lines_percentage('lulesh2.0')
    for key in hotlines:
        print("FILE PATH:{}\tPERCENTAGE:{}%".format(key,round(hotlines[key],3)))'''
