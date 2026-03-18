import webbrowser
import yt_dlp

PROMPT = "You can ask me to play any video or song on YouTube. For example, say 'Play Despacito' or 'Play technical guruji'."
ANSWER = "I use `yt-dlp` to search for the best match on YouTube and open it in your default browser."

def play_youtube(query, open_in_browser=True, prefer_invidious=False):
    """
    Searches YouTube for the query and opens the top result.
    
    Args:
        query (str): The search term.
        open_in_browser (bool): Whether to open the link automatically.
        prefer_invidious (bool): Use Invidious frontend (not implemented fully here, placeholder).
        
    Returns:
        dict: {'status': 'success'/'error', 'url': str, 'title': str}
    """
    print(f"🔎 Searching YouTube for: {query}")
    
    ydl_opts = {
        'format': 'best',
        'noplaylist': True,
        'quiet': True,
        'no_warnings': True,
        'logger': None,
        'default_search': 'ytsearch1:',  # limit to 1 result
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            # We don't need to download, just extract info
            info = ydl.extract_info(query, download=False)
            
            if 'entries' in info:
                # It's a search result
                video = info['entries'][0]
            else:
                # Direct link or single result
                video = info

            video_url = video.get('webpage_url')
            video_title = video.get('title')
            
            print(f"🎯 Found: {video_title}")
            
            if open_in_browser and video_url:
                webbrowser.open(video_url)
                
            return {
                'status': 'success',
                'url': video_url,
                'title': video_title
            }
            
    except Exception as e:
        print(f"❌ Error searching YouTube: {e}")
        return {
            'status': 'error',
            'error': str(e)
        }

if __name__ == "__main__":
    # Test
    play_youtube("never gonna give you up")
