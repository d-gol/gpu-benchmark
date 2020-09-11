import subprocess

log_pods = subprocess.check_output(['kubectl', 'get', 'pods'])
pods_lines = log_pods.decode('UTF-8').split()

pod_template_name = 'dejan-tfjob-'
pod_names = []
for line in pods_lines:
    if line.startswith(pod_template_name) and 'worker' in line:
        pod_names.append(line.split('\s')[0])

res = subprocess.check_output(['kubectl', 'logs', pod_name])

lines = res.decode('UTF-8').split('\n')
for line in lines: 
    if '1\timages/sec' in line:
        line_split = line.split('\s')
        start_time = line_split[0].split('|')[1]
    elif 'total images/sec' in line:
        line_split = line.split('\s')
        end_time = line_split[0].split('|')[1]

print(start_time, end_time)
