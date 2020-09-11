import subprocess

log_pods = subprocess.check_output(['kubectl', 'get', 'pods'])
pods_lines = log_pods.decode('UTF-8').split()

pod_template_name = 'dejan-tfjob-'
pod_names = []
for line in pods_lines:
    if line.startswith(pod_template_name) and 'worker' in line:
        pod_names.append(line.split('\s')[0])
        
csv_header = 'model,batch-size,replicas-ps,replicas-workers,nvidia-plugins,start-time,end-time,imgs-per-second,gpu-utilization,gpu-memory,gpu-power-usage,gpu-temperature\n'

with open('experiments.csv', 'w') as csv_file:
    csv_file.write(csv_header)

for pod_name in pod_names:
    logs = subprocess.check_output(['kubectl', 'logs', pod_name])

    lines = logs.decode('UTF-8').split('\n')
    for line in lines: 
        if '1\timages/sec' in line:
            line_split = line.split('\s')
            start_time = line_split[0].split('|')[1]
        elif 'total images/sec' in line:
            line_split = line.split()
            end_time = line_split[0].split('|')[1]
            imgs_per_second = line_split[-1]
    
    nodeName = subprocess.check_output(['kubectl', 'get', 'pod', pod_name, '-o', 'go-template="{{.spec.nodeName}}"']).decode('UTF-8')[1:-1]
    spec_option = 'spec.nodeName=' + nodeName
            
    nvidia_plugin_out = subprocess.check_output(['kubectl', 'get', 'pod', '-A', '--field-selector', spec_option]).decode('UTF-8')
    nvidia_plugin_lines = nvidia_plugin_out.split('\n')
    for line in nvidia_plugin_lines:
        if 'nvidia' in line:
            nvidia_plugin = line.split()[1]
            
    pod_name_split = pod_name.split('-')
    model = pod_name_split[2]
    batch_size = pod_name_split[3]
    ps_replicas = '1'
    worker_replicas = '1'
    
    csv_line = model + ',' + batch_size + ',' + ps_replicas + ',' + worker_replicas + ',' + nvidia_plugin + ',' + \
                start_time + ',' + end_time + ',' + imgs_per_second + ',,,,\n'
    
    with open('experiments.csv', 'a') as csv_file:
        csv_file.write(csv_line)
    
    print(model, batch_size, ps_replicas, worker_replicas, nvidia_plugin, start_time, end_time, imgs_per_second)
