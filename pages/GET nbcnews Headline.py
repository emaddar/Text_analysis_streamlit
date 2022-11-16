import requests
from bs4 import BeautifulSoup
import streamlit as st
url = "https://www.nbcnews.com/"
response = requests.get(url)
html = BeautifulSoup(response.text, "html.parser")
st.header("test")
for news in html.find_all("h3")[:4]:
    st.header(f"Headline: {news.text}")
    st.subheader(f"Link:  {news.find('a')['href']}")