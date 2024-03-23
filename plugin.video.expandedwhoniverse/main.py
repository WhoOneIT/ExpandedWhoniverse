from urllib.parse import parse_qsl, urlencode, quote_plus, unquote_plus
import xbmcgui
import xbmcplugin
import xbmc
import csv
from collections import defaultdict
import os
import xbmcaddon
print(os.getcwd())



addon_handle = int(sys.argv[1])
base_url = sys.argv[0]

#Set current filepath as variable (used for accessing .csv later)
addon = xbmcaddon.Addon(id='plugin.video.expandedwhoniverse')
addon_path = addon.getAddonInfo('path')
#Retrieve path of .csv database
Serials_path = os.path.join(addon_path, 'resources', 'Serials.csv')
Episodes_path = os.path.join(addon_path, 'resources', 'Episodes.csv')
Seasons_path = os.path.join(addon_path, 'resources', 'Seasons.csv')

#Define Log for Debugging
def log(message):
    xbmc.log(f"ExpandedWhoniverse Addon: {message}", xbmc.LOGINFO)

#Open Serials.csv to filter each serial - Classic Who Only
def list_classic_serials(series):
    log(f"list_classic_serials({series})has started")
    with open(Serials_path, mode='r', encoding='utf-8') as csv_file:
        csv_reader = csv.DictReader(csv_file)
        for row in csv_reader:
            if row['Series'] == series:  # Ensuring we use the correct key as per the CSV
                query = {
                    'action': 'list_episodes_total',
                    'serial': row['Episode_Title'],  # Passing the correct series name
                    'ep_title': row['Episode_Title'],
                    'linked': row['linked'] # Does series link to anything e.g. DW confidential's corresponding episode
                }
                log(f"passed query where query = {query}")
                add_directory_item(
                    name=row['Episode_Title'],  # Assuming you want to use the series name here
                    query=query,
                    iconimage='',  # Placeholder for an icon image if available
                    is_folder=True
                )
    log(f"finished add_directory item supposedly")
    xbmcplugin.endOfDirectory(addon_handle)


def list_episodes_total(serial):
    with open(Episodes_path, mode='r', encoding='utf-8') as csv_file:
        csv_reader = csv.DictReader(csv_file)
        for row in csv_reader:
            if row['Serial'] == serial:
                # Determine action based on Mode
                if row['Mode'] == 'Iplayer':
                    action = 'play_iplayer_www_directly'
                elif row['Mode'] == 'Sounds':
                    action = 'play_sounds_directly'
                elif row['Mode'] == 'Youtube':
                    action = 'play_youtube_directly'
                else:
                    action = 'play_video_direct'
                
                # Prepare query
                query = {
                    'action': action,
                    'url': row['Video_URL'],
                    'description': row['Description'],
                    'icon_image': row['Image_URL'],
                    str('name'): str(row['Serial']) + ": " + str(row['Episode_Title'])
                }

                # Handle linked episodes
                log("handling linked episodes")
                linked_num = (row['linked_num'])
                linked_name = get_linked_name(linked_num)
                log("Finished Handling Linked Episodes")
                # Determine display name
                display_name = row['Episode_Title']
                if linked_name:
                    display_name = f"{linked_name} - {row['Episode_Title']}"

                runtime = row.get('runtime')  # Assuming 'runtime' is the name of the column in your CSV
                year = row.get('year')
                add_directory_item(
                    name=display_name,
                    query=query,
                    iconimage=row.get('Image_URL', ''),
                    description=row.get('Description', ''),
                    is_folder=False,
                    runtime=runtime,  # Pass runtime to add_directory_item
                    year=year
                )
    xbmcplugin.endOfDirectory(addon_handle)


def get_linked_name(linked_num):
    try:
        linked_num = int(linked_num)
        with open(Episodes_path, mode='r', encoding='utf-8') as csv_file:
            # We do not need to adjust for header as csv.DictReader already skips it
            for i, row in enumerate(csv.DictReader(csv_file), start=2):
                # Check if the current row number matches the linked_num
                if i == linked_num:
                    # Assuming 'Episode_Title' is the correct column for the name
                    return row.get('Episode_Title', "Unnamed Episode")
    except ValueError:
        log(f"Error: linked_num '{linked_num}' is not a valid integer")
        return None
    except Exception as e:
        log(f"Unexpected error occurred: {str(e)}")
        return None






def play_youtube_directly(url):
	xbmc.executebuiltin(f"PlayMedia(plugin://plugin.video.youtube/play/?video_id={url})")
	log("Attempted to playback via Youtube")

def play_iplayer_www_directly(name, url, iconimage, description):
    log(name)
    # Decode the URL to ensure it's in a standard format for comparison
    decoded_url = unquote_plus(url)
    name = str(name.replace("_", " "))
    log(name)
    # Determine the mode based on whether the URL is for BBC Sounds
    if decoded_url.startswith("https://www.bbc.co.uk/sounds"):
        full_url = f"plugin://plugin.video.iplayerwww/?url={url}&mode=212&name={name}&iconimage={iconimage}&description={description}"
    else:
        full_url = f"plugin://plugin.video.iplayerwww/?url={url}&mode=202"


    # Execute the built-in Kodi command to play the media
    xbmc.executebuiltin(f"PlayMedia({full_url})")
    log(f"Attempting to play: {full_url}")


def play_video_direct(url):
    play_item = xbmcgui.ListItem(path=url)
    xbmcplugin.setResolvedUrl(addon_handle, True, listitem=play_item)

def play_video(video_id, name, iconimage, description): # TEST URL - Need to check but I think I've replaced this functionality so this code isn't used anymore 
    # Construct the URL to play through iPlayer WWW addon with additional parameters
    play_url = f'plugin://plugin.video.iplayerwww/?url=https%3A%2F%2Fwww.bbc.co.uk%2Fiplayer%2Fepisode%2Fp00t8qnw&mode=202&name=Doctor+Who+%281963%E2%80%931996%29+-+1996+TV+Movie%3A+Doctor+Who&iconimage=https%3A%2F%2Fichef.bbci.co.uk%2Fimages%2Fic%2F832x468%2Fp0g0985j.jpg&description=As+the+21st+Century+dawns%2C+the+Seventh+Doctor+becomes+the+Eighth+in+San+Francisco.&subtitles_url='

    # Create a list item to play, setting necessary properties
    play_item = xbmcgui.ListItem(path=play_url)
    play_item.setInfo(type="Video", infoLabels={"Title": name, "Plot": description})
    if iconimage:
        play_item.setArt({'thumb': iconimage, 'icon': iconimage})
    
    # Tell Kodi to play the item
    xbmcplugin.setResolvedUrl(addon_handle, True, listitem=play_item)
    #Create Log in case playback doesn't occur
    log("Starting playback...")

def add_directory_item(name, query, iconimage=None, description=None, is_folder=True, runtime=None, year=None):
    url = base_url + '?' + urlencode(query)
    li = xbmcgui.ListItem(label=name)
    if iconimage:
        li.setArt({'thumb': iconimage, 'icon': iconimage})
    if description:
        li.setInfo('video', {'title': name, 'plot': description})

    # Dictionary to hold video info
    info = {}
    if runtime:
        try:
            info['duration'] = int(runtime)
        except ValueError:
            log("Invalid runtime value: {}".format(runtime))
    if year:
        try:
            info['year'] = int(year)
        except ValueError:
            log("Invalid year value: {}".format(year))

    if info:
        li.setInfo('video', info)

    xbmcplugin.addDirectoryItem(handle=addon_handle, url=url, listitem=li, isFolder=is_folder)



#List series numbers for each show by linking in with Seasons.csv
def list_series_from_csv(show_key):
    # Assume the Seasons_path is already defined as shown in your message
    with open(Seasons_path, mode='r', encoding='utf-8') as csv_file:
        csv_reader = csv.DictReader(csv_file)
        for row in csv_reader:
            if row['Show'] == show_key:
                query = {
                    'action': row['Action'],
                    'series': row['Name'].replace(" ", "_"),  # Ensure the series name is URL-friendly
                    'serial': row['Name'].replace(" ", "_")  # Same as above for serperate navigation
                }
                add_directory_item(
                    name=row['Name'],
                    query=query,
                    iconimage=row['Image_url'],
                    description=row.get('Description', ''),
                    is_folder=row.get('Is_folder', 'true') == 'true'  # Assuming 'Is_folder' is a string 'True' or 'False'
                )
    xbmcplugin.endOfDirectory(addon_handle)






#Main Menu Screen - when addon is launched
def main_menu():
    add_directory_item('Doctor Who - 1963-1996', 
                   {'action': 'list_series_1963_1996'}, 
                   'https://ichef.bbci.co.uk/images/ic/1920x1080/p0gppb3f.jpg', 
                   'Classic Doctor Who - Stories from Doctors 1 though 8 - 26 Seasons and The TV Movie',  
                   is_folder=True)   
    add_directory_item('Doctor Who - 2005-2022', 
                   {'action': 'list_series_2005_2022'}, 
                   'https://ichef.bbci.co.uk/images/ic/1920x1080/p0gpxrx6.jpg', 
                   'Revival Doctor Who - Stories from Doctors 9 through 13 - 13 Series',  
                   is_folder=True)       
    add_directory_item('Doctor Who - 2023-Present', 
                   {'action': 'list_series_2023_present'}, 
                   'https://ichef.bbci.co.uk/images/ic/1920x1080/p0gz2jcy.jpg', 
                   'Disney Doctor Who - Fourteenth and Fifthteenth Doctors',  
                   is_folder=True)
    add_directory_item('Spin-Offs', 
                   {'action': 'list_spin_offs'}, 
                   'https://tardis.wiki/images/Tardis_images/2/2c/K9_MR_SMITH.JPG', 
                   'Additional content from across the Whoniverse',  
                   is_folder=True)
    add_directory_item('Non-Canon Content', 
                   {'action': 'list_standalone'}, 
                   'https://tardis.wiki/images/Tardis_images/5/58/HartnellLambertLaugh.jpg', 
                   'Stories which are not set within the Doctor Who Universe, including An Adventure in Space and Time among others',  
                   is_folder=True)  
    add_directory_item('Documentaries and Behind the Scenes', 
                   {'action': 'list_documentaries'}, 
                   'https://tardis.wiki/images/Tardis_images/2/2f/DWCLogo2005.jpg', 
                   'Documentaries and Behind the Scenes footage from Doctor Who',  
                   is_folder=True)
    add_directory_item('Audio Dramas & Audiobooks', 
                   {'action': 'list_audio'}, 
                   'https://tardis.wiki/images/Tardis_images/a/a2/Strax_Saves_the_Day.jpg', 
                   'Audio Adventures within the Whoniverse',  
                   is_folder=True)
    add_directory_item('Bonus Features', 
                   {'action': 'list_bonus'}, 
                   'https://tardis.wiki/images/Tardis_images/a/a2/Strax_Saves_the_Day.jpg', 
                   'Additional content from across the Whoniverse, including behind the scenes clips, concerts and more',  
                   is_folder=True)
    xbmcplugin.endOfDirectory(addon_handle)


def router(paramstring):
    log(f"Router called with params: {paramstring}")
    params = dict(parse_qsl(paramstring))
    action = params.get('action')
    series = params.get('series')

    # Add logging to trace the action being handled
    log(f"Handling action:{action}")

    if action == 'play_video':
        # Additional logging can be added in each branch if needed
        play_video(params['video_id'])
    elif action == 'list_episodes_total':
        list_episodes_total(params.get('serial'))
    elif action == 'play_iplayer_www_directly':
        play_iplayer_www_directly(params.get('name'),params.get('url'),params.get('icon_image'),params.get('description'))
    elif action == 'play_youtube_directly':
        play_youtube_directly(params.get('url'))
    elif action == 'play_video_direct':
        play_video_direct(params.get('url'))
    elif action == 'list_series_1963_1996':
        list_series_from_csv('list_series_1963_1996')
    elif action == 'list_series_2005_2022':
        list_series_from_csv('list_series_2005_2022')
    elif action == 'list_series_2023_present':
        list_series_from_csv('list_series_2023_present')
    elif action == 'list_spin_offs':
        list_series_from_csv('list_spin_offs')
    elif action == 'list_standalone':
        list_series_from_csv('list_standalone')
    elif action == 'list_bonus':
        list_series_from_csv('list_bonus')
    elif action == 'list_audio':
        list_series_from_csv('list_audio')
    elif action == 'list_big_finish':
        list_series_from_csv('list_big_finish')
    elif action == 'list_documentaries':
        list_series_from_csv('list_documentaries')
    elif action == 'list_episodes':
        list_classic_serials(series)
        log(f"elif action ==list_episodes confirmed - series:{series}")
    else:
        log("Router has failed - Returning to main menu")
        main_menu()

    xbmcplugin.endOfDirectory(addon_handle)

if __name__ == '__main__':
    router(sys.argv[2][1:])