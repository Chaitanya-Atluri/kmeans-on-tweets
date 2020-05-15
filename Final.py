import random as rd
import re
import math
import string
def remove_pattern(input_txt, pattern):
    r = re.findall(pattern,input_txt)
    for i in r:
        input_txt = re.sub(i,'', input_txt)
    return input_txt

def pre_process_tweets(loc):

    f = open(loc, "r", encoding="utf8")
    tweets = list(f)
    list_of_tweets = []

    for i in range(len(tweets)):
        # for mention
        tweets[i] = remove_pattern(tweets[i], "@[\w]*")
        # for hashtag
        tweets[i] = remove_pattern(tweets[i], "#")
        # for url
        tweets[i] = remove_pattern(tweets[i], "https?://[A-Za-z0-9./]+")
        # to lower
        tweets[i] = tweets[i].lower()
        # remove punctuations
        tweets[i] = re.sub("[^a-zA-Z]", " ", tweets[i])
        # trim extra spaces
        tweets[i] = " ".join(tweets[i].split())

        # convert each tweet from string type to as list<string> using " " as a delimiter
        list_of_tweets.append(tweets[i].split(' '))

    f.close()

    return list_of_tweets


def k_means(tweets, k=4, max_iterations=50):

    centroids = []

    # initialization, assign random tweets as centroids
    count = 0
    hash_map = dict()
    while count < k:
        random_tweet_idx = rd.randint(0, len(tweets) - 1)
        if random_tweet_idx not in hash_map:
            count += 1
            hash_map[random_tweet_idx] = True
            centroids.append(tweets[random_tweet_idx])

    iter_count = 0
    prev_centroids = []

    while (is_converged(prev_centroids, centroids)) == False and (iter_count < max_iterations):

        # assigning tweets to the closest centroids
        clusters = assign_cluster(tweets, centroids)

        # to check if k-means converges
        prev_centroids = centroids

        #  update centroid
        centroids = update_centroids(clusters)
        iter_count = iter_count + 1


    sse = compute_SSE(clusters)

    return clusters, sse


def is_converged(prev_centroid, new_centroids):

    if len(prev_centroid) != len(new_centroids):
        return False

    for c in range(len(new_centroids)):
        if " ".join(new_centroids[c]) != " ".join(prev_centroid[c]):
            return False

    return True


def assign_cluster(tweets, centroids):

    clusters = dict()

    for t in range(len(tweets)):
        min_dis = math.inf
        cluster_idx = -1;
        for c in range(len(centroids)):
            dis = jaccard(centroids[c], tweets[t])
            # look for a closest centroid for a tweet

            if centroids[c] == tweets[t]:
                cluster_idx = c
                min_dis = 0
                break

            if dis < min_dis:
                cluster_idx = c
                min_dis = dis

        if min_dis == 1:
            cluster_idx = rd.randint(0, len(centroids) - 1)

        clusters.setdefault(cluster_idx, []).append([tweets[t]])

        last_tweet_idx = len(clusters.setdefault(cluster_idx, [])) - 1
        clusters.setdefault(cluster_idx, [])[last_tweet_idx].append(min_dis)

    return clusters


def update_centroids(clusters):

    centroids = []
    for c in range(len(clusters)):
        min_dis_sum = math.inf
        centroid_idx = -1

        min_dis_dp = []

        for t1 in range(len(clusters[c])):
            min_dis_dp.append([])
            dis_sum = 0
            # get distances sum for every of tweet t1 with every tweet t2 in a same cluster
            for t2 in range(len(clusters[c])):
                if t1 != t2:
                    if t2 < t1:
                        dis = min_dis_dp[t2][t1]
                    else:
                        dis = jaccard(clusters[c][t1][0], clusters[c][t2][0])

                    min_dis_dp[t1].append(dis)
                    dis_sum += dis
                else:
                    min_dis_dp[t1].append(0)

            # select the tweet with the minimum distances sum as the centroid for the cluster
            if dis_sum < min_dis_sum:
                min_dis_sum = dis_sum
                centroid_idx = t1
        centroids.append(clusters[c][centroid_idx][0])

    return centroids


def jaccard(tweet1, tweet2):

    intersection = set(tweet1).intersection(tweet2)
    union = set().union(tweet1, tweet2)
    return 1 - (len(intersection) / len(union))


def compute_SSE(clusters):

    sse = 0
    for c in range(len(clusters)):
        for t in range(len(clusters[c])):
            sse = sse + (clusters[c][t][1] * clusters[c][t][1])
    sse=sse/10;
    return sse


if __name__ == '__main__':

    data_loc = 'cnnhealth.txt'

    tweets = pre_process_tweets(data_loc)

    #  values of K for K-means
    k =[10,15,20,25,30]

    # for every experiment 'e', run K-means
    for i in range(len(k)):

        print("Clusters and SSE when for k = " + str(k[i]))

        clusters, sse = k_means(tweets, k[i])

        for c in range(len(clusters)):
            print("cluster" + str(c+1) + ": ", str(len(clusters[c])) + " tweets")
        print("--> SSE : " + str(sse))
        print('\n')
