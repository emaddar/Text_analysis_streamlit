import streamlit as st
import datetime
import smtplib #pip install secure-smtplib
import ssl
import time
from datetime import date, timedelta
import functions
import re
import matplotlib.pyplot as plt
import numpy as np
import random
import pandas as pd
import altair as alt
import numpy as np

  


st.set_page_config(
    page_title="Text Analysis",
    page_icon=":bird:",
    layout="wide",
    initial_sidebar_state="expanded",
)



m = st.markdown("""
<style>
div.stButton > button:first-child {
    background-color: rgb(29, 161, 242);
    justify-content: center;
    align-items: center;
    display: flex;
    height:40px; 
    width:150px; 
    margin: -0px -50px; 
    position:relative;
    top:200%; 
    left:50%;
}
</style>""", unsafe_allow_html=True)

with st.sidebar:
    user_api_key = st.text_input('User API key :')
    st.success("Click [here](https://emaddar-text-analysis-streamlit-twitter-analysis-oi3ds2.streamlit.app/Get_your_API_Key) if you don't have an API Key")

    
    


st.markdown(""" # Twitter Analysis """)
st.info("This application searches for the latest Tweets in a defined period. Then an AI model analyzes and summarizes the tweets to give the general sentiment on the subject or the person in question.")


# make any grid with a function
# https://towardsdatascience.com/how-to-create-a-grid-layout-in-streamlit-7aff16b94508
def make_grid(cols,rows):
    grid = [0]*cols
    for i in range(cols):
        with st.container():
            grid[i] = st.columns(rows)
    return grid

mygrid = make_grid(2,3)    
all_words = mygrid[0][1].text_input('Words you want to search for* (Ex : PSG club)')

mygrid0 = make_grid(2,2)    
limit = mygrid0[0][0].number_input('Maximum number of tweets*', value=30)
Minimum_likes = mygrid0[0][1].number_input('Minimum likes*', value=1)
# for i in range(2):
#     for j in range(2):
#         mygrid0[i][j].write(f'{i},{j}')

compare = st.checkbox("Compare results with tweets 365 before selected dates ?")


# st expander
# https://github.com/imnileshd/nlp-sentence-transformer/blob/master/streamlit_app.py
form_expander = st.expander(label='➕ Additionals research options')
with form_expander:
    mygrid1 = make_grid(1,2)   
    exact_phrase = mygrid1[0][0].text_input('This exact phrase (Ex : Result of the PSG match tonight)')
    None_of_these_words = mygrid1[0][1].text_input('None of these word(s) (Ex : racisme)')

    mygrid2 = make_grid(2,3)
    These_hastags = mygrid2[0][0].text_input('These hashtags (Ex : #lega1)')
    From_acounts = mygrid2[0][1].text_input('From accounts (Ex : @KMbappe)')
    To_acounts = mygrid2[0][2].text_input('Accounts mentionned (Ex : @PSGClub)')

    today = date.today()
    default_date_lastweek = today - timedelta(days=7)

    from_date = mygrid2[1][0].date_input('From date',default_date_lastweek)
    to_date = mygrid2[1][1].date_input('To date')
    lang = mygrid2[1][2].selectbox('Language',('fr', 'en', 'ar', 'bn', 'cs', 'da', 'de', 'el', 'es', 'fa', 'fil', 'he', 'hi', 'hu', 'id', 'it', 'ja', 'ko', 'msa', 'no', 'pl', 'pt', 'ro',
                                                 'ru', 'sv', 'th', 'tr', 'uk', 'ur', 'zh-cn', 'zh-tw'))
 


    
mygrid3 = make_grid(1,3)
submitted = mygrid3[0][1].button('Submit')

if submitted:
    if all_words == "":
        st.warning('Please write words you want to search for', icon="⚠️")
    elif limit == 0 :
        st.warning('Maximum number of tweets must be greater than 0', icon="⚠️")
    elif Minimum_likes == 0 :
        st.warning('Minimum likes must be greater or equal 1', icon="⚠️")
    elif user_api_key == "":
        st.warning("Pleas Enter your API Key")
    elif len(user_api_key) != 173 :
        st.warning("User API Key's length must be = 173 characters", icon="⚠️")
    elif all_words != "" and limit > 0 and Minimum_likes >= 1 and user_api_key != "" and len(user_api_key) == 173 :
        query = functions.getQuery(searsh_query = [all_words,                   # 0
                                                     limit,                     # 1
                                                      exact_phrase,             # 2
                                                       None_of_these_words,     # 3
                                                        These_hastags,          # 4
                                                         From_acounts,          # 5
                                                          To_acounts,           # 6
                                                            str(Minimum_likes), # 7
                                                             str(from_date),    # 8
                                                              str(to_date),     # 9
                                                               lang])           # 10
        # st.write(query)
        df = functions.get_tweets(query, int(limit))
        df = df.sort_values(['Like', 'Retweet','Replay'],ascending=False)
        # st.dataframe(df)
        x = " ".join(list(df['Tweet']))
        text_only = functions.clean_text(x)

        All_text = text_only

        if text_only == "":
            st.warning(f'No results found for this query : {query}', icon="⚠️")
        else :

            #### API ####
            # user_api_key                              # Get User Api Key
            x = functions.get_api(text_only, lang, user_api_key)
            
            if len(x) == 4 :                              # When get_api return False then len(get_API) = 1 else len(get_API) = 4
                data = x[0]
                labels = x[1]
                n = x[2]
                max_data = max(data)
                max_data_index = data.index(max(data))
                max_labels = labels[max_data_index]
            else :
                data = [0, 0, 0]   # This means wa can not do setiment analysis
                labels = ["Positive", "Negative", "Neutral"]

            # st.write(data)
            # st.write(labels)
                
                # st.write(data_365_days_ago)
                # st.write(labels_365_days_ago)


            stop_words = functions.our_get_stop_words(lang)

            # Word cloud's color
            def couleur_red(*args, **kwargs):
                return "rgb(255, 0, {})".format(random.randint(0, 170))

            def couleur_blue(*args, **kwargs):
                return "rgb({}, 0, 255)".format(random.randint(0, 170))

            def couleur_grey(*args, **kwargs):
                return "rgb({}, 170, 170)".format(random.randint(116, 130))

            # functions.get_word_cloud(stop_words, All_text, max_labels)

            from wordcloud import WordCloud  
            import matplotlib.pyplot as plt
            from PIL import Image

            st.markdown("___")
            if max_labels == 'Positive':
                st.markdown(f"### 😃 RESULTS : {max_labels} {round(max_data,2)} %")
            elif max_labels == 'Negative':
                st.markdown(f"### 😡 RESULTS : {max_labels} {round(max_data,2)} %")
            else :
                st.markdown(f"### 😶 RESULTS : {max_labels} {round(max_data,2)} %")
            col1, col2 = st.columns(2)


            mask = np.array(Image.open("resc/mask_bird.jpg"))
            mask[mask == 1] = 255
            wordcloud = WordCloud(background_color = 'white', stopwords = stop_words, max_words = 75, mask=mask).generate(All_text)
            if max_labels == "Positive":
                fig = plt.figure(figsize=(30,30) , dpi=400) 
                plt.imshow(wordcloud.recolor(color_func = couleur_blue))
                plt.axis("off")
                # plt.show()
                col1.pyplot(fig)
            elif max_labels == "Neutral":
                fig = plt.figure(figsize=(30,30) , dpi=400) 
                plt.imshow(wordcloud.recolor(color_func = couleur_grey))
                plt.axis("off")
                # plt.show()
                col1.pyplot(fig)
            else : 
                fig = plt.figure(figsize=(30,30) , dpi=400) 
                plt.imshow(wordcloud.recolor(color_func = couleur_red))
                plt.axis("off")
                # plt.show()
                col1.pyplot(fig)



            
            # col1.image('resc/mypic.png')


            with col2:
                for i in range(5):
                    st.markdown("")

                fig = plt.figure(figsize = (8   ,6))
    
                # creating the bar plot
                plt.bar(labels, data, color =['green', 'red', 'gray'],
                        width = 0.7)
                
                plt.xlabel(f"This analysis was performed on the {n} first characters \n of the tweets retrieved and classified according \nto the number of likes (from most liked to least liked)")
                plt.ylabel("Probabilities")
                plt.title("Sentimental analysis")
            
                st.pyplot(fig)


            st.markdown("___")
            st.markdown("### TWEETS MOST LIKED 👍")

            if len(df)>=3:
                tweet_1_date = df.iloc[0]['Date']
                tweet_2_date = df.iloc[1]['Date']
                tweet_3_date = df.iloc[2]['Date']

                tweet_1_User = df.iloc[0]['User']
                tweet_2_User = df.iloc[1]['User']
                tweet_3_User = df.iloc[2]['User']


                tweet_1_Tweet = df.iloc[0]['Tweet']
                tweet_2_Tweet = df.iloc[1]['Tweet']
                tweet_3_Tweet = df.iloc[2]['Tweet']  

                tweet_1_Like = df.iloc[0]['Like']
                tweet_2_Like = df.iloc[1]['Like']
                tweet_3_Like = df.iloc[2]['Like']    

                tweet_1_Replay = df.iloc[0]['Replay']
                tweet_2_Replay = df.iloc[1]['Replay']
                tweet_3_Replay = df.iloc[2]['Replay'] 

                tweet_1_Retweet = df.iloc[0]['Retweet']
                tweet_2_Retweet = df.iloc[1]['Retweet']
                tweet_3_Retweet = df.iloc[2]['Retweet']    

                tweet_1_Url = df.iloc[0]['Url']
                tweet_2_Url = df.iloc[1]['Url']
                tweet_3_Url = df.iloc[2]['Url']    
           
           
                mygrid4 = make_grid(1,3)
                mygrid4[0][0].markdown("___")
                mygrid4[0][0].write(f'{tweet_1_date}')
                mygrid4[0][0].write(f'👍 {tweet_1_Like} 💬 {tweet_1_Replay} 🔄 {tweet_1_Retweet}')
                mygrid4[0][0].write(f'User :    @{tweet_1_User}')
                mygrid4[0][0].text_area(label="", value = f'{tweet_1_Tweet}', height=150, key = "t1")
                mygrid4[0][0].write(f'[See the tweet in Twitter]({tweet_1_Url})')


                mygrid4[0][1].markdown("___")
                mygrid4[0][1].write(f'{tweet_2_date}')
                mygrid4[0][1].write(f'👍 {tweet_2_Like} 💬 {tweet_2_Replay} 🔄 {tweet_2_Retweet}')
                mygrid4[0][1].write(f'User :    @{tweet_2_User}')
                mygrid4[0][1].text_area(label="", value = f'{tweet_2_Tweet}', height=150, key = "t2")
                mygrid4[0][1].write(f'[See the tweet in Twitter]({tweet_2_Url})')


                mygrid4[0][2].markdown("___")
                mygrid4[0][2].write(f'{tweet_3_date}')
                mygrid4[0][2].write(f'👍 {tweet_3_Like} 💬 {tweet_3_Replay} 🔄 {tweet_3_Retweet}')
                mygrid4[0][2].write(f'User :    @{tweet_3_User}')
                mygrid4[0][2].text_area(label="", value = f'{tweet_3_Tweet}', height=150, key = "t3")
                mygrid4[0][2].write(f'[See the tweet in Twitter]({tweet_3_Url})')
            else :
                st.warning(f"sorry, can't find three tweets on twitter with this query : {query}. Try to change query parameters",  icon="⚠️")
                


            all_tweets_expander = st.expander(label='➕ Show all tweets found')

            with all_tweets_expander :
                
                st.dataframe(df)
                                    
                @st.cache
                def convert_df(df):
                    # IMPORTANT: Cache the conversion to prevent computation on every rerun
                    return df.to_csv().encode('utf-8')
                
                csv = convert_df(df)
                st.download_button(
                    label="Download data as CSV",
                    data=csv,
                    file_name=f'Twitter {query}.csv',
                    mime='text/csv',
                )





            if compare:
                df_date_sorted = df.sort_values(['Date'],ascending=True)
                from_date = df_date_sorted.iloc[0]['Date'].strftime("%Y-%m-%d") # get date of 1st tweet in result
                to_date = df_date_sorted.iloc[-1]['Date'].strftime("%Y-%m-%d")  # get date of last tweet in result
                phrase = f"from {from_date} to {to_date}"

                 ### 365 days ago ###
                from_to_365_days_ago = functions.get_from_to_date_k_days_ago(df,365)
                from_date_1_year_ago = str(from_to_365_days_ago[0])
                to_date_1_year_ago = str(from_to_365_days_ago[1])
                query = re.sub(r'until:\S+', '', query)   # Remove URL
                query = re.sub(r'since:\S+', '', query)   # Remove mentions
                query += ' until:'+to_date_1_year_ago
                query += ' since:'+from_date_1_year_ago

                df_365_days_ago = functions.get_tweets(query, int(limit))
                df_365_days_ago = df_365_days_ago.sort_values(['Like', 'Retweet','Replay'],ascending=False)

                x_365_days_ago = " ".join(list(df_365_days_ago['Tweet']))
                text_only_365_days_ago = functions.clean_text(x_365_days_ago)

        #### API 365_days_ago ####
                
                api_365_days_ago = functions.get_api(text_only_365_days_ago, lang, user_api_key)
                
                
                if len(api_365_days_ago) == 4 :   # Whet get_api return False then len(get_API) = 1 else len(get_API) = 4
                    data_365_days_ago = api_365_days_ago[0]
                    labels_365_days_ago = api_365_days_ago[1]
                    n_365_days_ago = api_365_days_ago[2]
                else :
                    data_365_days_ago = [0, 0, 0]   # This means wa can not do setiment analysis
                    labels_365_days_ago = ["Positive", "Negative", "Neutral"]
                
                phrase_365 = f"from {from_date_1_year_ago} to {to_date_1_year_ago}"
                

                result_df_api = pd.DataFrame({
                "Period" : [phrase, phrase_365]  ,
                "Positive" : [data[0], data_365_days_ago[0]],
                "Negative" :[data[1], data_365_days_ago[1]],
                "Neutral" : [data[2], data_365_days_ago[2]]
                })

                # st.dataframe(result_df_api)
                # # plt.rcParams["figure.figsize"] = (10,3)
                # fig1 = plt.figure(figsize = (1   ,12))
                # result_df_api.plot(x="Period",
                #                         y=["Positive", "Negative", "Neutral"],
                #                         kind="bar",
                #                         color=[(75/255, 192/255, 192/255, 0.5),
                #                             (255/255, 99/255, 132/255, 0.5),
                #                             (255/255, 206/255, 86/255, 0.5)])
                # plt.xticks(rotation=0)
                # # plt.savefig('./base/static/base/images/copmared_365_days.png',bbox_inches='tight')
                # st.set_option('deprecation.showPyplotGlobalUse', False)
                # st.pyplot()  
                # st.bar_chart(result_df_api)



                prediction_table = pd.melt(result_df_api, id_vars=['Period'], value_vars=['Positive', 'Negative', 'Neutral'])
                # st.dataframe(prediction_table)

                # https://github.com/altair-viz/altair/issues/2002
                range_ = ['red', 'green', 'blue']
                chart = alt.Chart(prediction_table, title='Compare results from the same period last year').mark_bar(
                    opacity=1,
                    ).encode(
                    column = alt.Column('Period:O', spacing = 50, header = alt.Header(labelOrient = "bottom")),
                    x =alt.X('variable', sort = ["Positive", "Negative", "Neutral"],  axis=None),
                    y =alt.Y('value:Q'),
                    color= alt.Color('variable', scale=alt.Scale(domain=labels, range=range_))
                ).configure_view(stroke='transparent')


                mygrid5 = make_grid(1,3)
                mygrid5[0][0].altair_chart(chart, use_container_width=True)
                mygrid5[0][0].markdown(f"This graphic compares the sentiment analysis in period {phrase} and the period {phrase_365}.  Be carefull, you may not find any Tweet for the same query 365 ago.")



