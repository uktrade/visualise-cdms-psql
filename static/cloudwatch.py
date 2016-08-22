import json
import os
import subprocess

def get_day_data(n):
  if os.path.isfile(n):
    with open(n, 'rb') as fh:
      return json.loads(fh.read().decode('utf8'))
  data_str = subprocess.check_output([
    'aws',
    'cloudwatch',
    'get-metric-statistics',
    '--namespace',
    'AWS/EC2',
    '--metric-name',
    'NetworkIn',
    '--start-time',
    "2016-08-{0}T00:00:00Z".format(n),
    '--end-time',
    "2016-08-{0}T00:00:00Z".format(n + 1),
    '--period',
    '120',
    '--statistics',
    'Average',
    '--dimensions',
    'Name=InstanceId,Value=i-7ac31cef',
  ])
  with open(str(n), 'wb') as fh:
    fh.write(data_str)
  return json.loads(data_str.decode('utf8'))['Datapoints']

def main():
  datapoints = []
  for n in map(int, range(16, 23)):
    datapoints.extend(get_day_data(n))
  print(json.dumps(datapoints, indent=2))


if __name__ == '__main__':
  main()
