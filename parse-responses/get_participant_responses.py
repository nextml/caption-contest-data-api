from __future__ import print_function
import requests
import pickle

__author__ = {'Scott Sievert': ['scottsievert.com', 'stsievert@wisc.edu']}

"""
This script grabs the data from NEXT.


URL variable is manually grabbed from the NEXT dashboard (copying and pasting
the link to "participant responses" and removing the ?zip=True
"""

URL = 'http://ec2-52-33-184-31.us-west-2.compute.amazonaws.com:8000/api/experiment/36c29d890aa4b5b993033d512a8496/7e461b94b833746ecd402a6f23165a/participants'

URL = 'http://ec2-52-36-195-23.us-west-2.compute.amazonaws.com:8000/api/experiment/4cb5ff8c7ef68e60f0c3abcff450a0/participants'
URL = 'http://ec2-50-112-214-12.us-west-2.compute.amazonaws.com:8000/api/experiment/923271bee502d152b164f92a44ced0/participants'

r = requests.get(URL, 'wb')

pickle.dump(r.text, open("request.pkl", "wb"))


json_responses = r.text

f = open('responses.json', 'w')
print(json_responses, file=f)
f.close()
