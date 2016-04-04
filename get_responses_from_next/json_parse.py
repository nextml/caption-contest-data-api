"""
Given a bunch of experiment data run on the Triplet experiment, this script takes that as input (well, after modifying data_file) and outputs a file called "participant-responses.csv".

Steps to run this script:

    1. Download the participant data (from some link somewhere).
    2. Change FILENAME to the name of the downloaded file, move to the right folder
    3. `python json_parse.py`
    4. The output CSV is a file called `participant-responses.csv`

This script works best under Python 3; there may be unicode characters presents.
"""

from __future__ import print_function
import json
from pprint import pprint

__author__ = {'Scott Sievert':'stsievert@wisc.edu'}

# TODO: Make FILENAME/etc command line arguments using library docopt
FILENAME = 'participants-515.json'
APP = 'cardinal' # APP in {'cardinal', 'dueling', 'triplets'}

PRINT = False
algorithms = ['LilUCB', 'RoundRobin'] # for cardinal
#algorithms = ['BR_Random'] # for round2 dueling

def format_triplet_response_json(response_dict):
    """
    Return formatted participant logs that are app specific.

    Taken from NEXT-psych gui/base/app_manager/Triplets.py[1]. This script is on
    the GUI frontend for NEXT. It pings the backend to get the same JSON
    (commented out in this function).

    :input response_dict: The raw response data as a JSON object.
    :output: The output as a list of strings, with one string per response.

    >>> x = get_formatted_participant_data(dict)
    >>> x[0:2]
    ['Participant ID,Timestamp,Center,Left,Right,Answer,Alg Label',
 u'oeJq63j...,Lewis_LAlanine.jpg,Lewis_C2H3Cl.png,Lewis_PO43-.png,Lewis_PO43-.png,Test']

    [1]:https://github.com/kgjamieson/NEXT-psych/blob/master/gui/base/app_manager/PoolBasedTripletMDS/PoolBasedTripletMDS.py#L71
    """
    # Use frontend base local url
    #url = url+"/api/experiment/"+current_experiment.exp_uid+"/"+current_experiment.exp_key+"/participants"

    ## Make a request to next_backend for the responses
    #try:
        #response = requests.get(url)
        #response_dict = eval(response.text)
    #except (requests.HTTPError, requests.ConnectionError) as e:
        #print "excepted e", e
        #raise
    #print response_dict
    # Parse them into a csv
    # The rows are participant_id, timestamp, center, left, right, target winner, alg_label
    participant_responses = []
    participant_responses.append(",".join(["Participant ID", "Timestamp","Center", "Left", "Right", "Answer", "Alg Label"]))
    for participant_id, response_list in response_dict['participant_responses'].items():
        exp_uid, participant_id = participant_id.split('_')
        for response in response_list:
            line = [participant_id, response['timestamp_query_generated']]
            targets = {}
            # This index is not a backend index! It is just one of the target_indices
            target_winner = None
            print(response)
            for index in response['target_indices']:
                targets[index['label']] = index
                # Check for the index winner in this response
                # Shouldn't we check for target_winner?
                if 'index_winner' in list(response.keys()) and response["index_winner"] == index['index']:
                        target_winner = index
            if target_winner:
                # Append the center, left, right targets
                line.extend([targets['center']['target']['target_id'], targets['left']['target']['target_id'], targets['right']['target']['target_id']])
                # Append the target winner
                line.append(target_winner['target']['target_id'])
                # Append the alg_label
                line.append(response['alg_label'])
                participant_responses.append(",".join(line))

    return participant_responses

def format_carindal_response_json(response_dict):
    """
    Does the same thing as format_triplet_response_json but does it for the app
    cardinals instead.
    """
    participant_responses = [",".join(['Partipipant ID', 'Response Time (s)',
                                       'Network Delay (s)', 'Timestamp',
                                       'Rating', 'Alg label', 'Target'])]

    for participant_id, response_list in response_dict['participant_responses'].items():
        exp_uid, participant_uid = participant_id.split('_')

        for response in response_list:
            keys = ['participant_uid', 'response_time', 'network_delay',
                    'timestamp_query_generated', 'target_reward', 'alg_label']
            if set(keys).issubset(response.keys()):
                keys += ['target']
                line = []
                for key in keys:
                    if key == 'target':
                        line += [response['target_indices'][0]['target']\
                                 ['primary_description']]
                    elif key == 'participant_uid':
                        line += [participant_uid]
                    else:
                        line += ['{}'.format(response[key])]
                line = ",".join(line)

                participant_responses += [line]

    return participant_responses

def format_dueling_response(response_dict):
    """
    Return formatted participant logs that are app specific.

    Taken from NEXT-psych,
    gui/base/app_manager/DuelingBanditsExploration/DuelingBanditsExploration.py
    """
    participant_responses = []
    participant_responses.append(",".join(["Participant Id", "Timestamp","Left","Right","Answer","Alg Label"]))
    for participant_id, response_list in response_dict['participant_responses'].items():
        exp_uid, participant_id = participant_id.split('_')

        for response in response_list:
            line = [participant_id, response['timestamp_query_generated']]
            targets = {}
            target_winner = None
            for index in response['target_indices']:
                targets[index['label']] = index
                # Check for the index winner in this response
                # Shouldn't there be a target_winner? This is weird.
                if 'index_winner' in response.keys() and response["index_winner"] == index['index']:
                        target_winner = index

            # Some questions may not get answered; this makes sure that
            # we're looking at an answered question (GitHub issue #15)
            # --Scott Sievert, 2015-10-28
            if target_winner:
                # Append the left and right targets
                line.extend([targets['left']['target']['target_id'], targets['right']['target']['target_id']])
                # Append the index winner
                line.append(target_winner['target']['target_id'])
                # Append the alg_label
                line.append(response['alg_label'])
                participant_responses.append(",".join(line))

    return participant_responses

def plot_time_histogram(df):
    import numpy as np
    import matplotlib.pyplot as plt

    times = np.array(df['Response Time (s)'], dtype=float)
    times = np.sort(times)

    plt.figure()
    plt.hist(times[:-1500], bins=50)
    plt.show()

if __name__ == '__main__':
    functions_to_format_data = {'triplets': format_triplet_response_json,
                                'cardinal': format_carindal_response_json,
                                'dueling': format_dueling_response}

    with open(FILENAME) as data_file:
        data = json.load(data_file)

    csv = functions_to_format_data[APP](data)
    if PRINT: print("\n".join(csv))
    print(csv[0])

    f = open('participant-responses.csv', 'wt')
    print("\n".join(csv), file=f)
    f.close()


    import pandas as pd
    df = pd.DataFrame([line.split(',', maxsplit=6) for line in csv[1:]],
            columns=csv[0].split(','))

    # for sepearating individual algorithms
    if algorithms:
        for algorithm in algorithms:
            filename = 'participant_responses_'+algorithm+'.csv'
            key = 'Alg label'# if APP != 'dueling' else 'alg_label'
            df[df[key] == algorithm].to_csv(filename)
