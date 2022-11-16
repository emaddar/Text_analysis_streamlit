import requests
from bs4 import BeautifulSoup
import streamlit as st
url = "https://www.nbcnews.com/"
response = requests.get(url)
html = BeautifulSoup(response.text, "html.parser")
st.header("NBC news headlines")
i = 1
for news in html.find_all("h3"):
    st.write(f"{i} : [{news.text}]({news.find('a')['href']})")
    i += 1
    # st.subheader(f"Link:  {news.find('a')['href']}")