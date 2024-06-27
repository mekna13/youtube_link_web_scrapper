import os
import re
import json
import requests
from bs4 import BeautifulSoup
import xlsxwriter
from dotenv import load_dotenv

load_dotenv()

BASE_URL = os.getenv('BASE_URL')
CHANNEL_ID = os.getenv('CHANNEL_ID')
CHANNEL_NAME = os.getenv('CHANNEL_NAME')
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/107.0.0.0 Safari/537.36'
}

# endpoints = ['https://lms.tamu.edu/course-management', 'https://lms.tamu.edu/training']

#finding all pages of the website
endpoint_list = []
endpoint_list.append(BASE_URL)


def getting_endpoints(site):
    page = requests.get(site, headers=headers)

    soup = BeautifulSoup(page.text, 'html.parser')

    # links = soup.findAll(['a'], href=re.compile(r'^\/.{2,}$'))

    for link in soup.find_all('a'):

        try:
            href = link.attrs['href']
        except KeyError:
            break
        if href.startswith('/') and len(href) > 1:
            test_site = BASE_URL + href

            if test_site not in endpoint_list:
                endpoint_list.append(test_site)
                # print(test_site)

                #calling itself ( recursive )
                getting_endpoints(test_site)


getting_endpoints(BASE_URL)

print("ENDPOINT LIST LENGTH ", len(endpoint_list))

workbook = xlsxwriter.Workbook('Testing_Youtube_Links.xlsx')
worksheet = workbook.add_worksheet()
row = 0

worksheet.write_row(row, 0, ["Endpoint", "Tag", "Channel Name", "Channel Id"])
row += 1


def check_channel_info(endpoint):
    global row
    page = requests.get(endpoint, headers=headers)

    soup = BeautifulSoup(page.text, 'html.parser')

    links = soup.findAll(['a'], href=re.compile("youtu"))
    links.extend(soup.findAll(['iframe'], src=re.compile("youtu")))

    for link in links:

        if link.has_attr('href'):
            youtube_page = requests.get(link['href'], headers=headers)
        elif link.has_attr('src'):
            youtube_page = requests.get(link['src'], headers=headers)

        youtube_soup = BeautifulSoup(youtube_page.text, 'html.parser')

        # in the case of embedded videos
        if link.has_attr('src'):
            # channel data is present in embed youtube page but data is obfuscated
            # embed_data = re.search(r"ytcfg.set({.*});", str(youtube_soup.prettify())).group(1)
            # with open("embed.json", "w") as outfile:
            #     outfile.write(json.dumps(json.loads(embed_data)))

            # extracting link of og youtube page
            real_link = youtube_soup.find('a', href=re.compile("youtu"))

            # requesting og youtube page of embeded video
            real_youtube = requests.get(real_link['href'], headers=headers)
            youtube_soup = BeautifulSoup(real_youtube.text, 'html.parser')

        data = re.search(r"var ytInitialData = ({.*});", str(youtube_soup.prettify())).group(1)
        json_data = json.loads(data)
        # final_data = json.dumps(json_data, indent=4)

        try:
            Channel_Name = json_data["contents"]["twoColumnWatchNextResults"]["results"]["results"]["contents"][1][
                "videoSecondaryInfoRenderer"]["owner"]["videoOwnerRenderer"]["title"]["runs"][0]["text"]
            Channel_Id = json_data["contents"]["twoColumnWatchNextResults"]["results"]["results"]["contents"][1][
                "videoSecondaryInfoRenderer"]["subscribeButton"]["subscribeButtonRenderer"]["channelId"]
        except KeyError as ke:
            # some json for the youtube channel is structured different causing a key error
            print("Key Not Found ", ke, "for", link)
            print("Type of ", type(str(ke)), )
            if str(ke) == 'videoSecondaryInfoRenderer':
                Channel_Name = json_data["contents"]["twoColumnWatchNextResults"]["results"]["results"]["contents"][2][
                    "videoSecondaryInfoRenderer"]["owner"]["videoOwnerRenderer"]["title"]["runs"][0]["text"]
                Channel_Id = json_data["contents"]["twoColumnWatchNextResults"]["results"]["results"]["contents"][2][
                    "videoSecondaryInfoRenderer"]["subscribeButton"]["subscribeButtonRenderer"]["channelId"]
            # Some links are youtube playlists so the webpage is structured differently
            if str(ke) == "'twoColumnWatchNextResults'":
                # print("Playlist")
                # with open("error_channel_data.json", "w") as outfile:
                #     outfile.write(json.dumps(json_data, indent=4))
                try:
                    Channel_Name = \
                        json_data["sidebar"]["playlistSidebarRenderer"]["items"][1][
                            "playlistSidebarSecondaryInfoRenderer"][
                            "videoOwner"]["videoOwnerRenderer"]["title"]["runs"][0]["text"]
                    Channel_Id = \
                        json_data["sidebar"]["playlistSidebarRenderer"]["items"][1][
                            "playlistSidebarSecondaryInfoRenderer"][
                            "videoOwner"]["videoOwnerRenderer"]["title"]["runs"][0]["navigationEndpoint"][
                            "browseEndpoint"][
                            "browseId"]
                except:
                    print("Error occured while getting channel info")
                    break
        if Channel_Name != CHANNEL_NAME or Channel_Id != CHANNEL_ID:
            data = [endpoint, str(link), Channel_Name, Channel_Id]
            worksheet.write_row(row, 0, data)
            row += 1


for endpoint in endpoint_list:
    check_channel_info(endpoint)

workbook.close()
