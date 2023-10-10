import string, os
from pytube import YouTube
from bs4 import BeautifulSoup as Soup
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By

# video url and title and the thumbnail url
def get_youtube_channel_links(channel_url):
    #start webdriver
    options = webdriver.ChromeOptions()
    options.add_argument('--ignore-ssl-errors=yes')
    options.add_argument('--ignore-certificate-errors')

    driver = webdriver.Remote(
        command_executor="http://172.17.0.2:4444/wd/hub", 
        options=options
        )
    driver.get(channel_url)
    html = driver.find_element(By.TAG_NAME, 'html')
    
    #Load the rest of the page with 'End' key
    for _ in range(100):
        html.send_keys(Keys.END)
    
    page_source = driver.page_source
    soup = Soup(page_source, 'html.parser')

    #Scrape youtube URLs
    results = []
    youtube_urls = []
    
    div = soup.find('body')
    for link in div.findAll('a'):
        href = link.get('href')
        if href and href.startswith('/watch'):
            youtube_url = "https://www.youtube.com"+href
            if youtube_url not in youtube_urls:
                youtube_urls.append(youtube_url)
                yt = YouTube(youtube_url)            
                url_info = {
                    'title':yt.title,
                    'url':youtube_url,
                    'thumbnail_url':yt.thumbnail_url,
                    'date':yt.publish_date.strftime('%Y-%m-%d')
                }
                results.append(url_info)
    driver.quit()
    return results


def download_audio(youtube_url, output_path="."):
    print("Downloading audio...")
    audio_path = os.path.join(output_path,"audio")  
    if not os.path.exists(audio_path):
        os.makedirs(audio_path)

    yt = YouTube(youtube_url)
    audio_stream = yt.streams.filter(only_audio=True).first()
    date = yt.publish_date.strftime('%Y-%m-%d')

    translating = str.maketrans('', '', string.punctuation)
    title = yt.title.translate(translating)

    audio_stream.download(audio_path, filename=date + " - " + title + ".mp4")
    print(f"{title}")
    print("Download complete...")
    
    output_file_path = os.path.join(audio_path, date + " - " + title + ".mp4")

    return output_file_path





