import requests
from bs4 import BeautifulSoup
import streamlit as st


url = "https://www.nbcnews.com/"
response = requests.get(url)
html = BeautifulSoup(response.text, "html.parser")




for news in html.find_all("h3"):
    x = f"Headline: {news.text}"
    st.write(x)
    st.markdown("___")
    y = f"Link:  {news.find('a')['href']}"
    st.subheader(y)