from __future__ import print_function, division
import json
from pprint import pprint
import numpy as np
import pandas as pd


def format_dueling_responses(response_dict):
    participant_responses = []
    for participant_id, response_list in response_dict['participant_responses'].items():
        for response in response_list:
            line = {'participant_id': participant_id,
                    'timestamp_query_generated': response['timestamp_query_generated']}
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
                line['left_target_id'] = targets['left']['target']['target_id']
                line['right_target_id'] = targets['right']['target']['target_id']
                line['winner_target_id'] = target_winner['target']['target_id']

                line['left_target'] = targets['left']['target']['primary_description']
                line['right_target'] = targets['right']['target']['primary_description']
                line['winner_target'] = target_winner['target']['primary_description']

                keys = ['participant_uid', 'response_time', 'network_delay',
                        'timestamp_query_generated', 'alg_label']
                for key in keys:
                    line[key] = response[key]

                # Append the alg_label
                participant_responses += [line]

    return participant_responses

def format_carindal_responses(response_dict):
    participant_responses = []

    total_responses = 0
    unanswered = 0
    for participant_id, response_list in response_dict['participant_responses'].items():
        splits = participant_id.split('_')
        exp_uid, participant_uid = splits[:2]
        if len(participant_uid) == 0:
            print("Woah! ID = {}".format(participant_uid))
        participant_uid = "_".join(splits[:2])

        if len(splits) == 3:
            ip = splits[2]

        total_responses += len(response_list)

        global response
        for response in response_list:
            keys = ['participant_uid', 'response_time', 'network_delay',
                    'timestamp_query_generated', 'target_reward', 'alg_label']
            if 'target_reward' not in response.keys():
                unanswered += 1
            line = {}
            if set(keys).issubset(response.keys()):
                line['target_id'] = response['target_id'] if 'target_id' in response.keys() else response['target_indices'][0]['index']
                keys += ['target']
                for key in keys:
                    if key == 'target':
                        line[key] = response['target_indices'][0]['target']\
                                         ['primary_description']
                    elif key == 'participant_uid':
                        line[key] = participant_uid
                    else:
                        line[key] = response[key]

                participant_responses += [line]

    print("total responses = {}".format(total_responses))
    # print("unanswered responses = {}".format(unanswered))
    print("percent unanswered = {}".format(unanswered / total_responses))
    if unanswered / total_responses - 0.9 > 0:
        print('**** WARNING!')

    return participant_responses

if __name__ == '__main__':
    functions_to_format_data = {'cardinal': format_carindal_responses,
                                'dueling': format_dueling_responses}
    filename = 'responses.json'
    app = 'cardinal'

    dfs = []
    for filename in ['responses-adaptive.json', 'responses-random.json']:
        with open(filename) as data_file:
            data = json.load(data_file)

        responses = functions_to_format_data[app](data)
        dfs += [pd.DataFrame(responses)]

    df = pd.concat(dfs)
    df.to_csv('responses.csv')
