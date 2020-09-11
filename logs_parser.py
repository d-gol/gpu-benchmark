import subprocess

res = subprocess.check_output(['kubectl', 'logs', 'dejan-tfjob-resnet50-256-worker-0'])

lines = str(res).split('\\')
for line in lines:
    if '1\timages/sec' in line:
        line_split = line.split('\s')
        start_time = line_split[0].split('|')
    elif 'total images/sec' in line:
        line_split = line.split('\s')
        end_time = line_split[0].split('|')

print(start_time, end_time)