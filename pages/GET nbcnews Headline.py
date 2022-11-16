import requests
from bs4 import BeautifulSoup
import streamlit as st


url = "https://www.nbcnews.com/"
response = requests.get(url)
html = BeautifulSoup(response.text, "html.parser")

st.write(html.find_all("h3"))


for news in html.find_all("h3"):
    st.header(f"Headline: {news.text}")
    st.markdown("___")
    st.subheader(f"Link:  {news.find('a')['href']}")