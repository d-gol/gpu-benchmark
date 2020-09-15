import subprocess
import sys
from os import walk

def get_experiment_name_filepaths():
    filepaths = []
    for (dirpath, dirnames, filenames) in walk(mypath):
        filepaths.extend(dirnames)
    return filepaths

def get_run_info(experiment_name_filepath):
    with open(experiment_name_filepath, 'r') as read:
        content = read.readlines()

    result = dict()
    ps = True

    for line in content:
        if 'name:' in line:
            result['name'] = line.split(':')[1]
        elif 'batch_size' in line:
            result['batch_size'] = line.split(':')[1]
        elif 'model' in line:
            result['model'] = line.split(':')[1]
        elif 'Worker' in line:
            ps = False
        elif 'replicas' in line:
            if ps == True:
                result['ps'] = line.split(':')[1]
                ps = False
            else:
                result['workers'] = line.split(':')[1]

    return result

def create_run(experiment_name_filepath):
    apply_result = ''
    while not 'created' in apply_result:
        apply_result = subprocess.check_output(['kubectl', 'apply', '-f', experiment_name_filepath])


def are_pods_created(info):
    pods = subprocess.check_output(['kubectl', 'get', 'pods'])
    pods_lines = pods.decode('UTF-8').split()

    n_workers = len([x for x in pods_lines if 'worker' in x])
    n_ps = len([x for x in pods_lines if 'ps' in x])

    return (n_workers == info['workers']) and (n_ps == info['ps'])

def get_pods(info):
    while not are_pods_created(info):
        return subprocess.check_output(['kubectl', 'get', 'pods']).decode('UTF-8').split()

def get_worker_pod_names(pod_lines):
    for line in pods_lines:
        if line.startswith(pod_template_name):
            if 'worker' in line:
                worker_pod_names.append(line.split('\s')[0])

    return worker_pod_names

def get_nvidia_plugins(pod_name):
    nodeName = subprocess.check_output(['kubectl', 'get', 'pod', pod_name, '-o', 'go-template="{{.spec.nodeName}}"']).decode('UTF-8')[1:-1]
    spec_option = 'spec.nodeName=' + nodeName
            
    nvidia_plugin_out = subprocess.check_output(['kubectl', 'get', 'pod', '-A', '--field-selector', spec_option]).decode('UTF-8')
    nvidia_plugin_lines = nvidia_plugin_out.split('\n')
    for line in nvidia_plugin_lines:
        if 'nvidia' in line:
            nvidia_plugin = line.split()[1]

    return nvidia_plugin

def is_experiment_finished(pod_name):
    logs = subprocess.check_output(['kubectl', 'logs', pod_name]).decode('UTF-8')

    return 'total images/sec' in logs:

def parse_logs_info(pod_name):
    logs = subprocess.check_output(['kubectl', 'logs', pod_name])
    lines = logs.decode('UTF-8').split('\n')

    result = dict()

    for line in lines: 
        if '1\timages/sec' in line:
            line_split = line.split('\s')
            result['start_time'] = line_split[0].split('|')[1]
        elif 'total images/sec' in line:
            line_split = line.split()
            result['end_time'] = line_split[0].split('|')[1]
            result['imgs_per_second'] = line_split[-1]

    result['nvidia_plugin'] = get_nvidia_plugins(pod_name)

    return result


output_file_name = sys.argv[1]
experiment_name_filepaths = get_experiment_name_filepaths()

for experiment_name_filepath in experiment_name_filepaths:
    create_run(experiment_name_filepath)
    experiment_info = get_run_info(experiment_name_filepath)
    pod_lines = get_pods(experiment_info)
    worker_pod_names = get_worker_pod_names(pod_lines)
            
    with open(experiment_name_filepath.replace('.yaml', '.csv'), 'w') as csv_file:
        csv_header = 'model,batch-size,replicas-ps,replicas-workers,nvidia-plugins,start-time,end-time,imgs-per-second,gpu-utilization,gpu-memory,gpu-power-usage,gpu-temperature\n'
        csv_file.write(csv_header)

    for pod_name in worker_pod_names:
        while not is_experiment_finished(pod_name):
            continue

        logs_info = parse_logs_info(pod_name)
        
        csv_line = experiment_info['model'] + ',' + experiment_info['batch_size'] + ',' + experiment_info['ps'] + ',' + experiment_info['workers'] + ',' + 
                    logs_info['nvidia_plugin'] + ',' + logs_info['start_time'] + ',' + logs_info['end_time'] + ',' + logs_info['imgs_per_second'] + ',,,,\n'
        
        with open(output_file_name, 'a') as csv_file:
            csv_file.write(csv_line)
        
        print(experiment_info['model'] + ',' + experiment_info['batch_size'] + ',' + experiment_info['ps'] + ',' + experiment_info['workers'] + ',' + 
                    logs_info['nvidia_plugin'] + ',' + logs_info['start_time'] + ',' + logs_info['end_time'] + ',' + logs_info['imgs_per_second'] + ',,,,\n')

