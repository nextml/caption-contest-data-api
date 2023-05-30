import numpy as np
from typing import List, Dict, Any

# R is half of the range of possible values. Here, it's (3-1)/2 = 2/2 = 1.
R = 1.0

# delta is the failure probability -- i.e. set delta = 0.05 for 1-delta = 95% success probability.
delta = 0.05

# ------------------- DEFINE CLASSES FOR DIFFERENT SAMPLERS -------------------

class Random:
    def __init__(self, n:int):
        """
        Parameters
        ----------
        - n:int, number of targets (captions/videos/etc)
        
        Vars in function
        ----------------
        - self._initialized tracks whether some lists, other variables have been created yet
        - self.name gives the model a name for purposes of tracking simulation results,
            in case we want to plot simulation results for multiple models 
        """
        self.n = n
        self.name = self.model_name() + " " + str(n)
        self._initialized = False
        
    def model_name(self):
        return "Random"
    
    def get_queries(self, n_queries=100):
        """
        Parameters
        ----------
        n_queries: int
            Number of queries to queue up for a user
        
        Returns
        -------
        indices:List[int], len(indices) = n
            uniformly random permutation of values from 0 to "number of targets - 1" (i.e. n-1)
        scores:List[float], len(scores) = n
            List of n scores (where the score at index i corresponds to caption i) between 0 and 1.
            Represents quality of the query that can be posed to the user.
            Note that, for class Random, scores are just assigned randomly, so they don't really represent quality here.
        """
        indices = np.arange(self.n).astype(int)
        scores = np.random.uniform(0, 1, size=len(indices))
        
        return indices, scores

    def _initialize(self):
        """
        Initializes lists for storing info about user ratings of captions.
            Index i of self._reward_ stores the sum of user-provided ratings for caption i.
            Index i of self._reward_squared_ stores the sum of the squares of user-provided ratings for caption i.
            Index i of self._hits_ stores the number of times users have rated caption i.
            Set self._initialized = True so this initialization does not overwrite things every time.
            Index i of self.emp_avg_ratings_ stores the average user-provided rating for caption i.
            Index i of self.ucbs_ stores the distance from caption i to its upper (lower) "delta"-width confidence bound.
        """
        self._reward_ = np.zeros(self.n)
        self._reward_squared_ = np.zeros(self.n)
        self._hits_ = np.zeros(self.n)
        self.emp_avg_ratings_ = self._reward_ / np.maximum(self._hits_, 1)
        self.ucbs_ = self.calculate_ucbs(self._hits_,self.emp_avg_ratings_,np.arange(self.n),np.zeros(self.n))
        self.cis_ = self.calculate_95_ci(self._reward_squared_, self.emp_avg_ratings_, self._hits_)
        self._initialized = True
    
    def partial_fit(self, answers:List[Dict[str, int]]):
        """
        Parameters
        ----------
        answers:List[Dict[str, int]]
            A list of user-provided ratings of captions; each dict stores a single rating.
            Format of each dictionary is {"index": caption index, "rating": 1 <= rating <= 3}.
            
        Returns
        -------
        self, which is the model
            self.emp_avg_ratings_ is a list of ratings, where index i contains the average rating for caption i
            self.ucbs_ is a list of numbers related to confidence intervals, where index i contains self.ucbs_,
                where self.emp_avg_ratings_ \pm self.ucbs_ is the "delta" CI for the rating for caption i
        """
        if not self._initialized:
            self._initialize()
        for answer in answers:
            self._reward_[answer["index"]] += answer["rating"]
            self._reward_squared_[answer["index"]] += answer["rating"]**2
            self._hits_[answer["index"]] += 1
        self.emp_avg_ratings_ = self._reward_ / np.maximum(self._hits_, 1)
        answer_indices = [answer["index"] for answer in answers]
        self.ucbs_ = self.calculate_ucbs(self._hits_, self.emp_avg_ratings_, answer_indices, self.ucbs_)
        self.cis_ = self.calculate_95_ci(self._reward_squared_, self.emp_avg_ratings_, self._hits_)

        return self
    
    def calculate_ucbs(self, num_hits:List[int], emp_avg_ratings, answer_indices:List[int], old_ucbs:List[float]):
        """
        Parameters
        ----------
        num_hits:List[int]
            A list of the number of user-provided ratings for a caption, where index i contains the 
            number of user-provided ratings received for caption i.
        emp_avg_ratings
            A list of average user-provided ratings, where index i contains the average rating for caption i.
        answer_indices:List[int]
            List of caption numbers that received a user rating in the most recent round. Permits more efficient calculation
            of UCBS when using lil_KLUCB.
        old_ucbs:List[float]
            List of old ucbs, where index i refers to the old ucb for caption i. Used for more efficiently
            calculating ucbs for lil_KLUCB.
            
        Returns
        -------
        dist_to_upper:List[float]
            A list of the distances from the average ratings for captions to the upper confidence bound on each caption's rating.
            For caption i, index i is the distance from self.emp_avg_ratings_[i] to the upper confidence bound on the rating for caption i.
            Note that the calculation of the UCB depends on "delta", where we want to find the best caption w.p. 1-delta.
            This is done according to the lil-UCB algorithm.
            See https://proceedings.neurips.cc/paper/2017/file/c02f9de3c2f3040751818aacc7f60b74-Paper.pdf.
        """            
        # Formula from
        # https://github.com/nextml/NEXT/blob/4c8f4d5a66376a18c047f4c9409f73c75925bf07/apps/CardinalBanditsPureExploration/algs/LilUCB.py#L103
        dist_to_upper = np.zeros(len(num_hits)) + 1e8
        dist_to_upper[np.nonzero(num_hits)] = 2.0*R*R*np.log(4*num_hits[np.nonzero(num_hits)]*
                                                             num_hits[np.nonzero(num_hits)]/delta ) / num_hits[np.nonzero(num_hits)]
        return dist_to_upper
    
    def calculate_95_ci(self, sum_rewards_squared, empirical_mean, num_hits):
        '''
        Parameters
        ----------
        sum_rewards_squared
            A list of ints, where index j stores Sum_i(rating_i^2) for caption j.
            (We need to store this because Sum_i(rating_i^2) can't be computed directly from Sum_i(rating_i).)
        empirical_mean
            A list of floats, where index j stores [Sum_i(rating_i)]/n for caption j, where n is num_hits.
        num_hits
            A list of ints, where index j stores the number of user ratings for caption j.
            
        Returns
        -------
        A list of floats, where index j stores 1.96 times the standard deviation of the user-provided ratings for caption j.
        (The 95% CI for caption j, then, is its empirical mean \pm this value.)
        '''
           
        '''
        Want to calculate
        1.96 * sqrt{ \frac{ 1/n * (Sum_i (reward_i^2) - n * empirical_mean^2) } { (n-1) * n } }.
        See https://github.com/nextml/NEXT/blob/4c8f4d5a66376a18c047f4c9409f73c75925bf07/apps/CardinalBanditsPureExploration/algs/LilUCB.py#L73
        '''
        ci_95 = np.zeros(len(num_hits)) + 1e8
        numerator = sum_rewards_squared - num_hits * empirical_mean**2
        denominator = (num_hits - 1) * num_hits ** 2

        ci_95[np.argwhere(num_hits > 1)] = 1.96 * np.sqrt(numerator[np.argwhere(num_hits > 1)] / denominator[np.argwhere(num_hits > 1)])
        return ci_95
    
class Active(Random):
    def model_name(self):
        return "Active"
        
    def get_queries(self, n_queries=100):
        """
        Parameters
        ----------
        n_queries:int
            Number of queries to queue up for a user
        
        Returns
        -------
        indices:List[int], len(indices) = min(n_queries, n)
            uniformly random permutation of values from 0 to "number of targets - 1" (i.e. n-1)
        scores:List[float], len(scores) = n_queries
            list of n_queries decimal values between 0 and 1. Represents quality of the query that can be posed to the user
        """
        if not self._initialized:
            self._initialize()
        
        indices = np.arange(self.n).astype(int)
        scores = self.emp_avg_ratings_ + self.ucbs_
        
        return indices, scores
    
class lil_KLUCB(Active):
    def model_name(self):
        return "lil_KLUCB"
    
    def calculate_ucbs(self, num_hits:List[int], emp_avg_ratings, answer_indices:List[int], old_ucbs:List[float]):
        """
        Parameters
        ----------
        num_hits:List[int]
            A list of the number of user-provided ratings for a caption, where index i contains the 
            number of user-provided ratings received for caption i.
        emp_avg_ratings
            A list of average user-provided ratings, where index i contains the average rating for caption i.
        answer_indices:List[int]
            List of caption numbers that received a user rating in the most recent round. Permits more efficient calculation
            of UCBS when using lil_KLUCB.
        old_ucbs:List[float]
            List of old ucbs, where index i refers to the old ucb for caption i. Used for more efficiently
            calculating ucbs for lil_KLUCB.            
            
        Returns
        -------
        dist_to_upper:List[float]
            A list of the distances from the average ratings for captions to the upper "delta"-width confidence bound on each caption's rating.
            For caption i, index i is the distance from self.emp_avg_ratings_[i] to the upper "delta"-width
            confidence bound on the rating for caption i.
            This is done according to the lil-KLUCB algorithm as stated in
                https://proceedings.neurips.cc/paper/2017/file/c02f9de3c2f3040751818aacc7f60b74-Paper.pdf.
        """
        mu = emp_avg_ratings
        UCB = old_ucbs
        for i in answer_indices:
            if num_hits[i]==0:
                # mu[i] = float('inf')
                UCB[i] = 1e8
            else:
                # UCB[i] = mu[i] + np.sqrt( 2.0*R*R*np.log( 4*T[i]*T[i]/delta ) / T[i] )
                # Note that the line below only makes sense when the responses take values in {1,2,3}
                # UCB[i] = self.computeUCB(muhat=(mu[i]-1)/2,threshold=(np.log(2*num_hits[i]*num_hits[i]/delta)/num_hits[i]))
                UCB[i] = ( self.computeUCB(muhat=(mu[i]-1)/2,threshold=(np.log(2*num_hits[i]*num_hits[i]/delta)/num_hits[i])) )*2+1 - mu[i]
        return UCB# - emp_avg_ratings  
    
    # Inspired by code at
    # https://github.com/nextml/NEXT/blob/4c8f4d5a66376a18c047f4c9409f73c75925bf07/apps/CardinalBanditsPureExploration/algs/KLUCB.py#L128-L157
    def computeUCB(self,muhat,threshold,accuracy=(10**(-6))):
        lower=muhat
        upper=1
        UCB=(lower+upper)/2
        while (upper-lower)>accuracy:
            new=self.leftright(muhat,lower,upper,threshold)
            lower=new[0]
            upper=new[1]
            UCB=new[2]
        return UCB
    
    # Also inspired by code at
    # https://github.com/nextml/NEXT/blob/4c8f4d5a66376a18c047f4c9409f73c75925bf07/apps/CardinalBanditsPureExploration/algs/KLUCB.py#L128-L157
    def leftright(self,muhat,lower,upper,threshold):
        if muhat*(1-muhat)!=0:
            silly=(upper+lower)/2
            KL=(muhat*np.log(muhat/silly))+((1-muhat)*np.log((1-muhat)/(1-silly)))
            if KL>=threshold:
                return [lower,silly,(silly+lower)/2]
            if KL<threshold:
                return [silly,upper,(silly+upper)/2]
        if muhat==0:
            silly=(upper+lower)/2
            KL=(1-muhat)*np.log((1-muhat)/(1-silly))
            if KL>=threshold:
                return [lower,silly,(silly+lower)/2]
            if KL<threshold:
                return [silly,upper,(silly+upper)/2]
        if muhat==1:
            return [1,1,1]
        
# ------------------- END OF CLASSES FOR DIFFERENT SAMPLERS -------------------
        
    
# ------------------- FUNCTIONS FOR RUNNING THE SIMULATION -------------------

from typing import List

def simulate_human_answer(index:int, captions:List[List[int]]) -> int:
    """
    Parameters
    -----------
    index:int
        Which index do we want the score for?
    captions:List[List[int]]
        A list of caption scores. For any `i`, `len(captions[i]) == 3` because
        it represents the number of unfunny, somewhat funny and funny ratings.

    Returns
    -------
    rating:int
        A rating of 1, 2 or 3 representing the "funniness" of a caption.
    """
    assert 0 <= index < len(captions)
    ratings = np.asarray(captions[index]).astype(float)
    ratings /= ratings.sum()
    return np.random.choice([1, 2, 3], p=ratings)

def num_potential_funniest(emp_avg_ratings, ucbs):
    """
    Parameters
    ----------
    emp_avg_ratings
        Index i of emp_avg_ratings stores the average user-provided rating for caption i.
    ucbs
        Index i of ucbs stores the distance from caption i to its upper confidence bound for finding the best caption w.p. 1-delta.
        
    Returns
    -------
    Let j be the index of the caption with the highest empirical average rating.
        This returns $Sum_i (emp_avg_ratings[i] + ucbs[i] > emp_avg_ratings[j] - ucbs[j])$
    """
    best_caption_index = np.argmax(emp_avg_ratings)
    c = 1
    best_avg_lower = emp_avg_ratings[best_caption_index] - c * ucbs[best_caption_index]
    upper_bounds = emp_avg_ratings + c * ucbs
    return (upper_bounds > best_avg_lower).sum()
            
def num_geq_funniest(emp_avg_ratings):
    """
    Parameters
    ----------
    emp_avg_ratings
        Index i of emp_avg_ratings stores the average user-provided rating for caption i.
        
    Returns
    -------
    Let j be the index of the caption with the highest empirical average rating.
        This returns $Sum_i (emp_avg_ratings[i] + ucbs[i] > emp_avg_ratings[j] - ucbs[j])$
    """
    return (emp_avg_ratings >= emp_avg_ratings[0]).sum()

# simulation as a function
def simulate_model(model_name, top_n_scores:int, total_queries:int):
    '''
    Parameters
    ----------
    model_name:str
        The name with which we want to associate simulation results for that model.
    top_n_scores:int
        The number of captions each user should respond to. For example, top_n_scores = 5 simulates
        the case in which each user rates 5 captions.
    total_queries:int
        The number of ratings to collect from users in a given caption contest. For example, total_queries = 400_000
        simulates a caption contest with a total of 400,000 user-provided ratings.
    
    Returns
    -------
    A list of flat data with the items listed below in 'datum'
    '''
    data = []
    for query_batch_num in range(total_queries//top_n_scores):
        list_of_dicts = []
        query_indices, query_scores = the_model.get_queries()

        top_score_indices = np.argpartition(query_scores, -top_n_scores)[-top_n_scores:]

        # pose queries to the human, and store in dict_ans
        for index in query_indices[top_score_indices]:
            # dictionary of answers
            dict_ans = {}
            index_rating = simulate_human_answer(index, no_header[:,-3:])
            dict_ans["index"] = index
            dict_ans["rating"] = index_rating
            list_of_dicts.append(dict_ans)

        the_model.partial_fit(list_of_dicts) 
        datum = {"num_funniest":  num_potential_funniest(the_model.emp_avg_ratings_, the_model.cis_),
                 "num_queries": (query_batch_num+1)*top_n_scores,
                 "query_batch": query_batch_num,
                 "top_n_scores": top_n_scores,
                 "sampler": the_model.name,
                 "num_geq_funniest": num_geq_funniest(the_model.emp_avg_ratings_)
                }
        data.append(datum)
        
    return data

# ------------------- END OF FUNCTIONS FOR RUNNING THE SIMULATION -------------------

# ------------------- RUN THE SIMULATION -------------------

# Read CSV
import pandas as pd
# # Read dataset from download
# df = pd.read_csv('803.csv')

# Read dataset from online
contest = 803
dfs = pd.read_html(f"https://nextml.github.io/caption-contest-data/dashboards/{contest}.html")
# Get the last table in the webpage
df = dfs[-1]

# .values removes the header row. (In this specific case, also want to remove first column.)
no_header = df.values[:,1:]

# PARAMETRIZE THE SIMULATION

total_queries = 400_000

# Create model and get queries
the_model = lil_KLUCB(len(no_header))

list_of_models = [lil_KLUCB(len(no_header)), Active(len(no_header)), Random(len(no_header))]
list_of_models = ["lil_KLUCB", "Active", "Random"]

top_n_scores = 5

data = []
num_samples = 10
for _ in range(num_samples):
    the_model = 0
    for model_name in list_of_models:
        if model_name == "lil_KLUCB":
            the_model = lil_KLUCB(len(no_header))
        elif model_name == "Active":
            the_model = Active(len(no_header))
        elif model_name == "Random":
            the_model = Random(len(no_header))
        data = data + simulate_model(the_model, top_n_scores, total_queries)
        
# WRITE SIMULATION RESULTS TO CSV

import pandas as pd
def list_to_csv(input_list, save_name):
    df = pd.DataFrame(input_list)
    df.to_csv(save_name)
    
def csv_to_dataframe(input_csv):
    return pd.read_csv(input_csv)

import datetime

current_datetime = datetime.datetime.now()
current_datetime = current_datetime.strftime('%Y%m%d%T').replace(":","")
# list_to_csv(data, "seaborn" + str(current_datetime) + ".csv")
list_to_csv(data, "seaborn_test_huge2.csv")
