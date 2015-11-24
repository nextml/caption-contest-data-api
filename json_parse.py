"""
Given a bunch of experiment data run on the Triplet experiment, this script takes that as input (well, after modifying data_file) and outputs a file called "participant-responses.csv".

Steps to run this script:

    1. Download the participant data (from some link somewhere).
    2. Change FILENAME to the name of the downloaded file, move to the right folder
    3. `python json_parse.py`
    4. The output CSV is a file called `participant-responses.csv`
"""


import json
from pprint import pprint

__author__ = {'Scott Sievert':'stsievert@wisc.edu'}


def get_formatted_participant_data(response_dict):
    """
    Return formatted participant logs that are app specific.

    Taken from NEXT-psych NEXT/gui/app_manager/Triplets.py[1]. This script is on
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

if __name__ == '__main__':
    FILENAME = 'lewis/participant_data.json'
    with open(FILENAME) as data_file:
        data = json.load(data_file)
        csv = get_formatted_participant_data(data)

        f = open('participant-responses.csv', 'wt')
        print("\n".join(csv), file=f)