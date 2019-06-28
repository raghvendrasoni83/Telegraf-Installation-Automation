import subprocess
import os
import argparse
import re

OUTPUT_KEYS = ['group', 'topic', 'partition', 'current_offset', 'log_end_offset', 'lag']


def parse_output(input_from_checker):
    output = []
    del input_from_checker[0]
    for line in input_from_checker:
        if 'TOPIC' not in line: #continue
            sep = re.compile('[\s]+')
            columns = sep.split(line)
            if columns[4]!='-':
                group = columns[5]
                topic = columns[0]
                metric_columns = [int(c) for c in columns[1:5]]
                key_and_value_pairs = zip(OUTPUT_KEYS, [group, topic] + metric_columns)
                output.append(dict(key_and_value_pairs))
    return output


def to_line_protocol(line):
        if (line!=[]):
            return "kafka.consumer_offset,topic={topic},consumer-id={group},partition={partition} current_offset={current_offset},log_end_offset={log_end_offset},lag={lag}".format(**line)

def get_kafka_cg(args):
    if args.kafka_dir[-1] != "/":
        args.kafka_dir = args.kafka_dir + "/"

    params = [
        '{}bin/kafka-consumer-groups.sh'.format(args.kafka_dir),
        '--bootstrap-server {}'.format(args.bootstrap_server),
        '--list',
       
    ]
    cmd = subprocess.Popen(" ".join(params), shell=True, stdout=subprocess.PIPE)

    return [line for line in cmd.stdout]




def get_kafka_lag(args,cg):
    if args.kafka_dir[-1] != "/":
        args.kafka_dir = args.kafka_dir + "/"
   
    params = [
        '{}bin/kafka-consumer-groups.sh'.format(args.kafka_dir),
        '--group {}'.format(cg.replace("\n","")),
        '--describe',
        '--bootstrap-server {} 2>/dev/null'.format(args.bootstrap_server)

    ]
   
    cmd = subprocess.Popen(" ".join(params), shell=True, stdout=subprocess.PIPE)

    return [line for line in cmd.stdout]




if __name__ == "__main__":
      parser = argparse.ArgumentParser(description='Process some integers.')
      parser.add_argument('--kafka-dir', help='Kafka base directory', required=True)
      parser.add_argument('--bootstrap-server', help='Which kafka to query. Used for new consumer',required=True)
      args = parser.parse_args()
      cgs = get_kafka_cg(args)
      for cg in cgs:
         output = get_kafka_lag(args,cg)
         if len(output) != 0:
             parsed_output = parse_output(output)
             for line in parsed_output:
                 kafka_consumer_lag = to_line_protocol(line)
                 print kafka_consumer_lag
