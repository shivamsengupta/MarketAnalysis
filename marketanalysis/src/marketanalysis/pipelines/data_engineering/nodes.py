"""
This is a boilerplate pipeline 'data_engineering'
generated using Kedro 0.19.3
"""

import requests
import random
from requests_html import HTMLSession
from bs4 import BeautifulSoup
import html2text
from duckduckgo_search import DDGS
from googlesearch import search
from urllib.parse import urlparse
import pandas as pd
import os
import json
import google.generativeai as genai
from youtube_transcript_api import YouTubeTranscriptApi
from youtube_transcript_api.formatters import TextFormatter
from zenrows import ZenRowsClient

GOOGLE_API_KEY = "YOUR_API_KEY"
genai.configure(api_key=GOOGLE_API_KEY)
gemini = genai.GenerativeModel('gemini-pro')
generation_config = genai.GenerationConfig(
  temperature=0.9
)


def clean_markdown(content):
    prompt3="""
# Role 
Your role is to transform raw HTML markdown content into a polished and concise format,
including a summary section only at last that captures the main points. You excel at structuring information 
effectively using Markdown elements and ensuring clarity and readability.

## Instructions
1. Analyze the provided HTML markdown content to identify key information.
2. Remove irrelevant links, advertisements, and repetitive content that 
detract from the main message.
3. Focus on preserving essential details while condensing the content to its most 
important elements.
4. Ensure that the final Markdown output is well-structured, easy to navigate, and 
communicates the main points clearly.
5. Strive for a professional and polished presentation of the content in Markdown format.
6. Please remove all pdf links if present in the markdown content.
7. Please understand that you have to remove all the pipe (|) symbol in the markdown content.
8. Return the cleaned Markdown content with enhanced structure, improved readability, and 
an informative summary section only at last.
9. Please understand that all the above 8 points are for your understanding only. Do not include 
any of the above instructions as markdown text in the output neither include summary of the 
instructions. 
"""
    prompt4="""
# Role 
Your task is to refine the provided HTML markdown content by focusing on the key information and presenting it in a polished Markdown format. Your goal is to enhance readability, structure the content effectively, and create an informative summary section.

## Instructions
1. Review the HTML markdown content to identify essential details.
2. Eliminate irrelevant links, advertisements, and repetitive content.
3. Focus on preserving critical information while condensing the content.
4. Create a well-structured Markdown output that is easy to navigate and communicates the main points clearly.
5. Ensure a professional and polished presentation of the content in Markdown format.
6. Exclude any PDF links present in the markdown content.
7. Avoid using the pipe (|) symbol in the Markdown output.
8. Return the cleaned Markdown content with enhanced structure, improved readability, and 
an informative summary section only at last.
9. Do not include big descriptions, just give results in point wise manner
10. Please understand that all the above 9 points are for your understanding only. Do not include 
any of the above instructions as markdown text in the output neither include summary of the 
instructions.
"""
    message=content+"\n"+"Use this prompt to clean the above markdown content "+prompt4
    full_message = gemini.generate_content(contents = message,
                                            generation_config=generation_config,
                                            stream=False)
    #print(full_message.text)
    return full_message.text


def get_input():
    print("Enter the company urls (preferred) or names one line at a time:")
    names = []
    while True:
        name = input()
        if name == "":
            break
        names.append(name)

    guidance_keywords = input(
        "Enter any guidance keywords to improve search (comma separated, press Enter if none): "
    ).split(",")
    guidance_keywords = [keyword.strip() for keyword in guidance_keywords if keyword.strip()]

    return names, guidance_keywords

def get_domain(url):
    result = urlparse(url)
    domain = result.netloc
    if domain.startswith("www."):
        domain = domain[4:]
    domain_name = domain.split(".")[0]
    return domain_name

def get_description_from_iframe_url(iframe_url):
    try:
        print(f"Fetching URL for Iframe {iframe_url}")
        response = requests.get(iframe_url)
        if response.status_code != 200:
            print(f"Failed to fetch URL for Iframe {iframe_url}")
            return " "
    
        soup = BeautifulSoup(response.content, "html.parser")

        # Locate the description or other content you want to extract
        # (this will depend on the specific structure of the target page)
        description_tag = soup.find("meta", attrs={"name": "description"})
        if description_tag and description_tag.get("content"):
            return description_tag.get("content")

        # return domain name without the tld
        return get_domain(iframe_url)
    except Exception as e:
        print(e)
        return None


def scrape_and_convert_to_markdown(url, smart_mode=False):
    try:
        l=[]
        # make url whole
        if not url.startswith("http"):
            url = "http://" + url

        user_agents =[
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36',
    'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36'
    ]
        HEADERS = {
        "User-Agent": random.choice(user_agents),
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.5",
        "Accept-Encoding": "gzip, deflate",
        "Connection": "keep-alive",
        "Upgrade-Insecure-Requests": "1",
        "Sec-Fetch-Dest": "document",
        "Sec-Fetch-Mode": "navigate",
        "Sec-Fetch-Site": "none",
        "Sec-Fetch-User": "?1",
        "Cache-Control": "max-age=0",
    }
        request_headers = {
    'referer': 'https://scrapeme.live/shop/',
    'accept-language': 'en-US,en;q=0.9',
    'content-type': 'application/json',
    'accept-encoding': 'gzip, deflate, br',
    'sec-ch-device-memory': '8',
    'sec-ch-ua': '"Google Chrome";v="119", "Chromium";v="119", "Not?A_Brand";v="24"',
    'sec-ch-ua-platform': "Windows",
    'sec-ch-ua-platform-version': '"10.0.0"',
    'sec-ch-viewport-width': '792',
    'user-agent': random.choice(user_agents)
  }   
    #     proxy = (
    # 'http://b920a2e084b89364ea058245f033c97a896e8973:'
    # 'js_render=true&antibot=true&premium_proxy=true@proxy.zenrows.com:8001'
    # )
    #     proxies = {"http": proxy, "https": proxy}
    #     response = requests.get(url, proxies=proxies, verify=False)   

        response = requests.get(url, headers={"User-Agent":random.choice(user_agents)}) 
        #response = requests.get(url, headers=HEADERS)
        if response.status_code != 200:
            print(f"Failed to fetch URL {url}")
            print(f"Error: {response.status_code}")
            return " "
            #return f"Failed to fetch URL {url}"
        
        soup = BeautifulSoup(response.content, "html.parser")
            
        for tag in soup.find_all(["style", "script"]):
            tag.decompose()

        # Remove all image tags or links
        for img_tag in soup.find_all("img"):
            img_tag.decompose()

        iframes = soup.find_all("iframe")

        for iframe in iframes:
            # Get the src attribute from the iframe tag
            src = iframe.get("src")

            # Replace the iframe tag with a Markdown link to the URL
            if src:
                description = get_description_from_iframe_url(src)
                iframe_link = f"[Iframe Link: {src}]({src})"
                if description:
                    iframe_link += f" - Description: {description}"
                iframe.replace_with(iframe_link)

        # Using html2text to convert HTML to Markdown
        
        converter = html2text.HTML2Text()
        converter.ignore_links = False
        markdown = converter.handle(str(soup.body))
        if smart_mode:
            print("Cleaning markdown")
            markdown = clean_markdown(markdown)
        return markdown
    except Exception as e:
        print(e)
        return None



#.....................................DUCKDUCKGO SEARCH ENGINE.......................................
# def search_urls_and_preview(keywords, limit=None):
#     num_results = 0
#     with DDGS(timeout=20) as ddgs:
#         try:
#             for r in ddgs.text(keywords):
#                 yield r
#                 num_results += 1
#                 if limit and num_results >= limit:  
#                     break
#         except Exception as e:
#             print("ERROR:- ",e)



#......................................GOOGLE SEARCH ENGINE...........................................
def search_urls_and_preview(keywords, limit=None):
    num_results = 0
    try:
        for url in search(keywords, num_results=limit):
            yield url
            num_results += 1
            if limit and num_results >= limit:
                break
    except Exception as e:
        print("ERROR:- ",e)

def get_company_financials(url: str):
    l=[]
    url += " company_financials"
    for r in search_urls_and_preview(url,3):
        #url=r["href"]
        url=r
        result = scrape_and_convert_to_markdown(url,smart_mode=True)
        l.append(result)
    return l

def search_and_get_crunchbase_financials(company_name: str, keywords: str = None):
    l=[]
    search_terms = company_name + " crunchbase"
    if keywords:
        search_terms += " " + keywords
    url = ""
    for r in search_urls_and_preview(search_terms, 3):
        # url=r["href"]
        url=r
        url += "/company_financials"
        result = scrape_and_convert_to_markdown(url,smart_mode=True)
        l.append(result)
    return l


def get_youtube_transcript(url):
    """
    First retrive the youtube id and then use the youtube transcript api.
    Example urls:
    https://www.youtube.com/embed/ET822mQtO0I?rel=0&controls=1&autoplay=1&mute=1&start=0
    https://www.youtube.com/watch?v=0WGNnd3oe3Q
    """
    if "youtube.com/embed/" in url:
        youtube_id = url.split("youtube.com/embed/")[1].split("?")[0]
    elif "youtube.com/watch?v=" in url:
        youtube_id = url.split("youtube.com/watch?v=")[1].split("&")[0]
    else:
        print("Could not find youtube id in url")
        return "Could not find youtube id in url"

    try:
        transcript = YouTubeTranscriptApi.get_transcript(youtube_id)
    except Exception as e:
        print("Could not get transcript for youtube id", youtube_id)
        print(e)
        return
    text = TextFormatter().format_transcript(transcript)
    return text


def scraping():
    company_names, guidance_keywords = get_input()
    df_scraped=[]
    for company in company_names:
        keyword,searching_text=" "," "
        scraping_results=[]
        financial_results=[]
        crunchbase_financial_results=[]
        youtube_transcript_results=" "
        cleaned_markdown={}
        cleaned_markdown_list=[]
        if not company.strip():
            continue
        print("SCRAPING FOR "+company+" STARTED !!!")
        print("=" * 100)
        for k in guidance_keywords:
            keyword=keyword+" "+k
        searching_text = company + " " + keyword
        
        print("SCRAPING STARTED...................................")
        search_results = search_urls_and_preview(searching_text, 3)
        for s in search_results:
            result = scrape_and_convert_to_markdown(s,smart_mode=True)     
            scraping_results.append(result)

        print("CRUNCHBASE SCRAPING STARTED..........................")
        crunchbase_financial_results=search_and_get_crunchbase_financials(company_name=company, 
                                                               keywords=keyword)
        print("FINANCIAL SCRAPING STARTED..........................")
        financial_results=get_company_financials(company)
        print("YT SUBSCRIPT SCRAPING STARTED..........................")
        youtube_transcript_results = get_youtube_transcript(company)
        
        cleaned_markdown={'Scraping Results':scraping_results,
                          'Crunchbase Financial Results':crunchbase_financial_results,
                          'Financial Results':financial_results,
                          'Youtube Transcript': youtube_transcript_results
                          }
        cleaned_markdown_str = {key: ', '.join(map(str, value)) 
                                if isinstance(value, list) else value for key, value in 
                                cleaned_markdown.items()}
        cleaned_markdown_list = ''.join(cleaned_markdown_str.values())
        print("-----------------------------------------------------------------------------")
        df_scraped.append({'Company': company,
                         'CLEANED_MARKDOWN': "".join(cleaned_markdown_list)
                         })
        print("SCRAPING FOR "+company+" FINISHED !!!")  
        print("=" * 100)
    df = pd.DataFrame(df_scraped)
    return df

