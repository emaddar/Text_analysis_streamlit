import snscrape.modules.twitter as sntwitter                            # For scrapping twitter
import pandas as pd
import re
import requests
import json
import time 
from datetime import date, timedelta
from stop_words import get_stop_words                                   # For cleaning text
from wordcloud import WordCloud  
import matplotlib.pyplot as plt
import numpy as np
import random
from PIL import Image

def join_with(mylist, operator):
    return f' {operator} '.join(mylist)

# Create a single text for analysis
def getQuery(searsh_query):
    query = searsh_query[0] + " lang:" + searsh_query[10] + " " 
    if searsh_query[2] != "":
        query += '"' + searsh_query[2] + '"' + " "
    if searsh_query[3] != "":
        query +=  ' '.join(['-'+i for i in searsh_query[3].split()]) + " "
    if searsh_query[4] != "":
        query += '(' + join_with(searsh_query[4].split(), 'OR') + ')'  + " "
    if searsh_query[5] != "":
        query += '(from:' + join_with(searsh_query[5].split(), 'OR from:') + ')'  + " "
    if searsh_query[6] != "":
        query += '(to:' + join_with(searsh_query[6].split(), 'OR to:') + ')'  + " "
    if searsh_query[7] != "" :
        query += 'min_faves:' + searsh_query[7] + " "
    if searsh_query[8] != "" :
        query += 'since:' + searsh_query[8] + " "
    if searsh_query[9] != "" :
        query += 'until:' + searsh_query[9] + " "
    return query



def get_tweets(query, limit):
    tweets = []
    for tweet in sntwitter.TwitterSearchScraper(query).get_items():
        if len(tweets) == limit:
            break
        else:
            tweets.append([tweet.date, tweet.username, tweet.content, tweet.likeCount, tweet.replyCount, tweet.retweetCount, tweet.url])
    df = pd.DataFrame(tweets, columns=['Date', 'User', 'Tweet', 'Like', 'Replay', 'Retweet', 'Url'])
    return df


# Removal the text fog
def clean_text(x):
    x = re.sub(r'http\S+', '', x)                   # Remove URL
    x = re.sub(r'@\S+', '', x)                      # Remove mentions
    x = re.sub(r'#\S+', '', x)                      # Remove Hashtags
    x = re.sub('\n+', '', x)
    x = re.sub("\'\w+", '', x)                      # Remove ticks and the next character
    x = re.sub(r'\w*\d+\w*', '', x)                 # Remove numbers
    x = re.sub('\s{2,}', " ", x)                    # Replace the over spaces
    x = x.replace('()', '')                         # Remove ()
    x = x.replace('>>>','')
    x = x.replace('#', '')
    return x


###_____________________________Get API_____________________________###
def get_api(text_only_limited, lang, key):
    
    headers = {"Authorization": "Bearer "+key}
    lang = "fr"
    url ="https://api.edenai.run/v2/text/sentiment_analysis"

    n = len(text_only_limited)
    if n >= 4000:
        text_only_limited = text_only_limited[:4000]
        n = len(text_only_limited)

    API_status = 1
    payload={"providers": "amazon", 'language': lang, 'text': text_only_limited}
    response = requests.post(url, json=payload, headers=headers)
    result = json.loads(response.text)

    if result['amazon']['status'] == 'fail':
        for i in range(20):
            n -= 1000
            if  n<=0 :
                API_status = 0
                break
            else:
                text_only_limited = text_only_limited[:n]
                payload={"providers": "amazon", 'language': lang, 'text': text_only_limited}
                response = requests.post(url, json=payload, headers=headers)
                result = json.loads(response.text)
                if result['amazon']['status'] != 'fail':
                    API_status = 1
                    break

    if API_status == 1:
        x = result['amazon']['items']

    # Create a dataframe of the API result
        api_dico = {}
        for i in range(len(x)):
            api_dico[x[i]['sentiment']] = round(x[i]['sentiment_rate'],4)*100
        api_df = pd.DataFrame(list(api_dico.items()), columns=['sentiment', 'sentiment_rate'])

    # Formatting of the sentimental analysis graph
        labels = api_df['sentiment'].tolist()
        data = api_df['sentiment_rate'].tolist()

    # Remove "Mixed" sentiment
        labels.remove('Mixed')
        del data[-1]
        return(data, labels, n, API_status)
    else:
        return API_status



def get_from_to_date_k_days_ago(df,k):
    df_date_sorted = df.sort_values(by='Date')
    df_date_sorted_time_type = df_date_sorted 
    
    from_date = df_date_sorted_time_type.iloc[0]['Date']
    to_date = df_date_sorted_time_type.iloc[-1]['Date']

    from_date_1_year_ago = (pd.to_datetime(from_date.strftime('%Y-%m-%d')) - timedelta(days=k)).strftime('%Y-%m-%d')
    to_date_1_year_ago = (pd.to_datetime(to_date.strftime('%Y-%m-%d')) - timedelta(days=k-1)).strftime('%Y-%m-%d')
    return (from_date_1_year_ago, to_date_1_year_ago)











def our_get_stop_words(lang):
    stop_words = get_stop_words(lang)               # Possible to add words
    if lang == "fr":
        ma_list_fr = ["bcp", "Bcp", "trkl", "c'est", "est","s'en","j'ai","etc", "ça", "n'a","n'as","ca","va", "après", "qu'","c","C","lors","s","S","a","b","c","d","e","f","g","h","i","j","k","l","m","n","o","p","q","r","s","t","u","v","w","x","y","z","A","B","C","D","E","F","G","H","I","J","K","L","M","N","O","P","Q","R","S","T","U","V","W","X","Y","Z","qu'il","qu'elle","vs","bcp","mdr", "d'un", "d'une", "s'il", "s'ils", "ya", "n'est"]
        for mot in ma_list_fr:
             if mot not in stop_words:
                 stop_words.append(mot)
    elif lang == "en":
        ma_list_en = ["day","a","b","c","d","e","f","g","h","i","j","k","l","m","n","o","p","q","r","s","t","u","v","w","x","y","z","A","B","C","D","E","F","G","H","I","J","K","L","M","N","O","P","Q","R","S","T","U","V","W","X","Y","Z"]
        for mot in ma_list_en:
             if mot not in stop_words:
                 stop_words.append(mot)
    return stop_words



# Word cloud's color
def couleur_red(*args, **kwargs):
    return "rgb(255, 0, {})".format(random.randint(0, 170))

def couleur_blue(*args, **kwargs):
    return "rgb({}, 0, 255)".format(random.randint(0, 170))



# Create Word cloud
def get_word_cloud(stop_words, text_only, status):
    mask = np.array(Image.open("resc/mask_bird.jpg"))
    mask[mask == 1] = 255
    wordcloud = WordCloud(background_color = 'white', stopwords = stop_words, max_words = 75, mask=mask).generate(text_only)
    if status == "Positive" or status == "Neutral":
        fig = plt.figure(figsize=(30,30) , dpi=400) 
        plt.imshow(wordcloud.recolor(color_func = couleur_blue))
        plt.axis("off")
        fig.tight_layout(pad=0, w_pad=0, h_pad=0)
        fig.savefig('resc/mypic.png') 
    else : 
        fig = plt.figure(figsize=(30,30) , dpi=400) 
        plt.imshow(wordcloud.recolor(color_func = couleur_red))
        plt.axis("off")
        fig.tight_layout(pad=0, w_pad=0, h_pad=0)
        fig.savefig('resc/mypic.png')  