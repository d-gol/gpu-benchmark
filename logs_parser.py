import subprocess

log_pods = subprocess.check_output(['kubectl', 'get', 'pods'])
pods_lines = log_pods.decode('UTF-8').split('\n')

pod_template_name = 'dejan-tfjob-'
pod_names = []
for line in pods_lines:
    if line.startswith(pod_template_name):
        pod_names.append(line.split('\t')[0])
        
print('pods:')
for pod in pod_names:
    print(pod)

res = subprocess.check_output(['kubectl', 'logs', 'dejan-tfjob-resnet50-256-worker-0'])

lines = res.decode('UTF-8').split('\n')
for line in lines:
    print(line)
    if '1\timages/sec' in line:
        line_split = line.split('\s')
        start_time = line_split[0].split('|')[1]
    elif 'total images/sec' in line:
        line_split = line.split('\s')
        end_time = line_split[0].split('|')[1]

print(start_time, end_time)
