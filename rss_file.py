import requests
import xml.etree.ElementTree as ET

def get_mp3_url_from_rss(rss_url):
    try:
        # Fetch the RSS feed
        response = requests.get(rss_url)
        response.raise_for_status()  # Raise an error for HTTP issues

        # Parse the XML content
        root = ET.fromstring(response.content)

        # Find the first <item> element
        for item in root.findall(".//item"):
            # Extract the <enclosure> element
            enclosure = item.find("enclosure")
            if enclosure is not None:
                url = enclosure.get("url")
                file_type = enclosure.get("type")

                # Check if the file is an MP3
                if file_type == "audio/mpeg" and url.endswith(".mp3"):
                    return url

        return None  # Return None if no valid MP3 URL is found

    except requests.RequestException as e:
        print(f"Error fetching RSS feed: {e}")
        return None
    except ET.ParseError as e:
        print(f"Error parsing XML: {e}")
        return None

if __name__ == "__main__":
    rss_url = "https://www.tagesschau.de/multimedia/sendung/tagesschau_in_100_sekunden/podcast-ts100-audio-100~podcast.xml"
    mp3_url = get_mp3_url_from_rss(rss_url)
    if mp3_url:
        print(f"MP3 URL: {mp3_url}")
    else:
        print("No valid MP3 URL found.")