from urllib.parse import parse_qsl, urlencode, quote_plus, unquote_plus
import xbmcgui
import xbmcplugin
import xbmc
import csv
from collections import defaultdict
import subprocess
import os
import xbmcaddon
print(os.getcwd())



addon_handle = int(sys.argv[1])
xbmcplugin.setContent(addon_handle, 'videos')
base_url = sys.argv[0]

#Set current filepath as variable (used for accessing .csv later)
addon = xbmcaddon.Addon(id='plugin.video.expandedwhoniverse')
addon_path = addon.getAddonInfo('path')
#Retrieve path of .csv database
Serials_path = os.path.join(addon_path, 'resources', 'Serials.csv')
Episodes_path = os.path.join(addon_path, 'resources', 'Episodes.csv')
Seasons_path = os.path.join(addon_path, 'resources', 'Seasons.csv')
Bonus_path = os.path.join(addon_path, 'resources', 'Bonus.csv')
content_paths = [Episodes_path, Bonus_path]

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
                }
                log(f"passed query where query = {query}")
                add_directory_item(
                    name=row['Episode_Title'],  # Assuming you want to use the series name here
                    query=query,
                    iconimage=row.get('Image_URL', ''),
                    is_folder=True
                )
    log(f"finished add_directory item supposedly")
    xbmcplugin.endOfDirectory(addon_handle)


def list_episodes_total(serial):
    for path in content_paths:
        with open(path, mode='r', encoding='utf-8') as csv_file:
            csv_reader = csv.DictReader(csv_file)
            for row in csv_reader:
                if row['Serial'] == serial or (serial == 'everything'):
                    # Determine action based on Mode
                    if row['Mode'] == 'Iplayer':
                        action = 'play_iplayer_www_directly'
                    elif row['Mode'] == 'Youtube':
                        action = 'play_youtube_directly'
                    elif row['Mode'] == 'None':
                        # Display popup dialog
                        action = 'unavailable'
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
    
                    # Determine display name
                    display_name = row['Episode_Title']
    
                    airdate = row.get('airdate', '')
                    log(f"Airdate format for {row['Episode_Title']}: {airdate}")
                    log(airdate)
                    runtime = row.get('runtime')  # Assuming 'runtime' is the name of the column in your CSV
                    episode_number = row.get('Number')
                    if row['Visibility'] == 'Shown':
                        add_directory_item(
                            name=display_name,
                            query=query,
                            iconimage=row.get('Image_URL', ''),
                            description=row.get('Description', ''),
                            is_folder=False,
                            runtime=runtime,  # Pass runtime to add_directory_item
                            airdate=airdate,
                            episode_number=episode_number
                        )



    xbmcplugin.addSortMethod(addon_handle, xbmcplugin.SORT_METHOD_UNSORTED)
    xbmcplugin.addSortMethod(addon_handle, xbmcplugin.SORT_METHOD_LABEL)
    if xbmcaddon.Addon().getSetting('debug_sortdate') == 'true':
        xbmcplugin.addSortMethod(addon_handle, xbmcplugin.SORT_METHOD_DATE)
    xbmcplugin.addSortMethod(addon_handle, xbmcplugin.SORT_METHOD_VIDEO_RUNTIME)
    xbmcplugin.endOfDirectory(addon_handle)

def play_youtube_directly(url):
	xbmc.executebuiltin(f"PlayMedia(plugin://plugin.video.youtube/play/?video_id={url})")
	log("Attempted to playback via Youtube")

def play_iplayer_www_directly(name, url, iconimage, description):

    log(name)

    if name is None:
        name = "Unknown"  # Provide a default name or handle it as you see fit
    else:
        name = name.replace("_", " ")
    # Decode the URL to ensure it's in a standard format for comparison
    decoded_url = unquote_plus(url)
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

def add_directory_item(name, query, iconimage=None, description=None, is_folder=True, runtime=None, episode_number=None, airdate=None, mode=None, url=None):
    url = base_url + '?' + urlencode(query)
    li = xbmcgui.ListItem(label=name)
    settings_display_images = xbmcaddon.Addon().getSetting('settings_display_images') == 'true'
    year = airdate[:4] if airdate and len(airdate) >= 4 else ""
    if xbmcaddon.Addon().getSetting('debug_givedate1900') == 'true':
        if airdate:
            airdate = airdate
        else:
            airdate = "1900-01-01" 
    if not settings_display_images:
        iconimage = None
    if iconimage:
        li.setArt({'thumb': iconimage, 'icon': iconimage})
    if description:
        # Safely convert episode_number only if it's not None and is a digit
        episode_num = 0  # Default episode number
        if episode_number and str(episode_number).isdigit():
            episode_num = int(episode_number)
        li.setInfo('video', {'title': name, 'plot': description, 'premiered': airdate, 'duration': runtime, 'episode': episode_number, 'year': int(year) if year.isdigit() else None})
    # Add context menu for all items
    encoded_url = quote_plus(query.get('url', ''))
    context_menu_action = f"RunPlugin({base_url}?action=view_source_url&url={encoded_url})"
    context_menu = [("Copy Source URL to Clipboard", context_menu_action)]
    li.addContextMenuItems(context_menu)

    info = {}
    if runtime:
        try:
            info['duration'] = int(runtime)
        except ValueError:
            log("Invalid runtime value: {}".format(runtime))


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
                if row['Visibility'] == 'Shown':
                    add_directory_item(
                        name=row['Name'],
                        query=query,
                        iconimage=row['Image_url'],
                        description=row.get('Description', ''),
                        is_folder=row.get('Is_folder', 'true') == 'true'  # Assuming 'Is_folder' is a string 'True' or 'False'
                    )
    xbmcplugin.endOfDirectory(addon_handle)


def view_source_url(params):
    url = unquote_plus(params.get('url', ''))
    if url:
        if url.startswith("https:"):
            log("Processing raw url")
        else:
            url = "https://youtu.be/" + url
        if sys.platform.startswith('linux'):
            clipboard_command = 'xclip -selection clipboard'
        elif sys.platform.startswith('win'):
            clipboard_command = 'clip'
        elif sys.platform.startswith('darwin'):
            clipboard_command = 'pbcopy'
        else:
            raise Exception("Unsupported OS")
        # Placeholder: Displaying the URL in a dialog
        process = subprocess.Popen(clipboard_command, stdin=subprocess.PIPE, shell=True)
        process.communicate(input=url.encode('utf-8'))
        xbmcgui.Dialog().ok('URL Copied to Clipboard', f'URL: {url} \nhas been copied to your clipboard. \n\n(Note: This only works on supported Operating Systems e.g. Windows and Mac)')
    else:
        xbmcgui.Dialog().ok('Error', 'This content either does not exist, or is not a playable media type such as a folder.'),




#Main Menu Screen - when addon is launched
def main_menu():
    add_directory_item('All Episodes in order',
                       {'action': 'list_all_episodes'},
                       'https://theposterdb.com/api/assets/302165/view',  # Replace with an appropriate image
                       'List all episodes from the Whoniverse',
                       is_folder=True)
    add_directory_item('Doctor Who - 1963-1996', 
                   {'action': 'list_series_1963_1996'}, 
                   'https://theposterdb.com/api/assets/456737/view', 
                   'Join the original Doctors on their adventures through space and time in that famous blue box - from William Hartnell to Paul McGann.',  
                   is_folder=True)   
    add_directory_item('Doctor Who - 2005-2022', 
                   {'action': 'list_series_2005_2022'}, 
                   'https://theposterdb.com/api/assets/303375/view', 
                   'Adventures across space and time - from Christopher Eccleston to Jodie Whittaker.',  
                   is_folder=True)       
    add_directory_item('Doctor Who - 2023-Present', 
                   {'action': 'list_series_2023_present'}, 
                   'https://theposterdb.com/api/assets/470606/view', 
                   'The current era of Doctor Who - The Doctor and friends travel from the dawn of human history to distant alien worlds. And everywhere they go, they find adventure, terror, fun, chases, joy and monsters.',  
                   is_folder=True)
    add_directory_item('Spin-Offs', 
                   {'action': 'list_spin_offs'}, 
                   'https://theposterdb.com/api/assets/36725/view', 
                   'Explore the Whoniverse from an alternate perspective to the Doctor.',  
                   is_folder=True)
    add_directory_item('Documentaries and Behind the Scenes', 
                   {'action': 'list_documentaries'}, 
                   'https://theposterdb.com/api/assets/49369/view', 
                   'Documentaries and Behind the Scenes footage from Doctor Who',  
                   is_folder=True)
    add_directory_item('Audio Dramas & Audiobooks', 
                   {'action': 'list_audio'}, 
                   'https://theposterdb.com/api/assets/53252/view', 
                   'Audio Adventures within the Whoniverse',  
                   is_folder=True)
    add_directory_item('Bonus Features', 
                   {'action': 'list_bonus'}, 
                   'https://theposterdb.com/api/assets/146984/view', 
                   'Additional content from across the Whoniverse, including Trailers, Convention Footage and more',  
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
    elif action == 'view_source_url':
        view_source_url(params)
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
    elif action == 'list_bbc_radio':
        list_series_from_csv('list_bbc_radio')
    elif action == 'list_documentaries':
        list_series_from_csv('list_documentaries')
    elif action == 'list_all_episodes':
        list_episodes_total("everything")
    elif action == 'list_trailers':
        list_series_from_csv('list_trailers')
    elif action == 'list_monster_descriptions':
        list_series_from_csv('list_monster_descriptions')
    elif action == 'list_episodes':
        list_classic_serials(series)
        log(f"elif action ==list_episodes confirmed - series:{series}")
    elif action == 'unavailable':
                xbmcgui.Dialog().ok('Content Unavailable', 'Sorry, This content is currently unavailable. This is likely for legal reasons or it is a lost episode.')
    else:
        log("Router has failed - Returning to main menu")
        main_menu()

    xbmcplugin.endOfDirectory(addon_handle)



if __name__ == '__main__':
    router(sys.argv[2][1:])