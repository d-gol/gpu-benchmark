import subprocess
import sys

to_search = sys.argv[1]

namespaces = list()
ns_lines = subprocess.check_output(['kubectl', 'get', 'ns']).decode('UTF-8').split('\n')

for line in ns_lines[1:-1]:
        line_split = line.split()
        if line_split[0] not in ['flo', 'ricardo-rocha','renato-cardoso','cert-manager']:
            namespaces.append(line_split[0])

#print(namespaces)
for namespace in namespaces:
        pod_names = []
        pods_lines = subprocess.check_output(['kubectl', '-n', namespace, 'get', 'pods']).decode('UTF-8').split('\n')

        for line in pods_lines[1:-1]:
            pod_names.append(line.split()[0])

        for pod_name in pod_names:
            try:
                log_lines = subprocess.check_output(['kubectl', '-n', namespace, 'logs', pod_name], stderr=subprocess.STDOUT).decode('UTF-8').split('\n')
                #print(namespace, pod_name)
                for log_line in log_lines:
                    if to_search in log_line:
                        print('FOUND')
                        print(namespace)
                        print(pod_name)
                        print(log_line.encode('utf-8').strip())

            except subprocess.CalledProcessError as err:
                lines = err.output.decode('UTF-8')

                if 'error: a container name must be specified for pod' in lines:
                    indices_open = [i for i, x in enumerate(lines) if x == '[']
                    indices_closed = [i for i, x in enumerate(lines) if x == ']']
                    
                    containers = []

                    for i in range(0, len(indices_open)):
                        cur = lines[indices_open[i] + 1: indices_closed[i]]
                        conts = cur.split()

                        for c in conts:
                            containers.append(c)

                    #print(namespace, pod_name, str(containers))

                    for container in containers:
                        try:
                            log_lines_2 = subprocess.check_output(['kubectl', '-n', namespace, 'logs', pod_name, container], stderr=subprocess.STDOUT).decode('UTF-8').split('\n')
                        except subprocess.CalledProcessError as err:
                            print('ERROR', err.output)
                        for log_line in log_lines_2:
                            if to_search in log_line:
                                print('FOUND')
                                print(namespace)
                                print(pod_name)
                                print(log_line.encode('utf-8').strip())
