import streamlit as st
import pandas as pd
from googleapiclient.discovery import build
from db import init_db, add_channel, get_all_channels, delete_channel

api_key = 'AIzaSyCQzSfcykNH1KBQsMVRjSxB9-5l1olH3Us'
youtube = build('youtube', 'v3', developerKey=api_key)

def get_channel_stats(youtube, channel_id):
    request = youtube.channels().list(
        part='snippet,contentDetails,statistics',
        id=channel_id
    )
    response = request.execute()

    if not response['items']:
        return None

    item = response['items'][0]
    data = {
        'channel_name': item['snippet']['title'],
        'subscribers': int(item['statistics'].get('subscriberCount', 0)),
        'views': int(item['statistics'].get('viewCount', 0)),
        'total_videos': int(item['statistics'].get('videoCount', 0)),
        'playlist_id': item['contentDetails']['relatedPlaylists']['uploads']
    }
    return data

def get_latest_videos(youtube, playlist_id, max_results=10):
    video_ids = []
    request = youtube.playlistItems().list(
        part='contentDetails',
        playlistId=playlist_id,
        maxResults=max_results
    )
    response = request.execute()

    for item in response['items']:
        video_ids.append(item['contentDetails']['videoId'])

    videos_data = []
    request = youtube.videos().list(
        part='snippet,statistics',
        id=','.join(video_ids)
    )
    response = request.execute()

    for video in response['items']:
        video_data = {
            'title': video['snippet']['title'],
            'published_at': video['snippet']['publishedAt'],
            'views': int(video['statistics'].get('viewCount', 0)),
            'likes': int(video['statistics'].get('likeCount', 0)),
            'comments': int(video['statistics'].get('commentCount', 0))
        }
        videos_data.append(video_data)

    return videos_data

def main():
    st.set_page_config(page_title="YouTube Analytics", layout="wide")
    st.title('YouTube Channel Analytics')

    # Initialize database
    init_db()

    # Sidebar for CRUD operations
    st.sidebar.title("Channel Management")

    # Add new channel
    with st.sidebar.expander("Add New Channel"):
        new_channel_id = st.text_input("Channel ID")
        if st.button("Add Channel"):
            if new_channel_id:
                channel_data = get_channel_stats(youtube, new_channel_id)
                if channel_data:
                    add_channel(new_channel_id, channel_data['channel_name'], "")
                    st.success(f"Added channel: {channel_data['channel_name']}")
                else:
                    st.error("Invalid channel ID")

    # Delete channel
    with st.sidebar.expander("Delete Channel"):
        channels = get_all_channels()
        if channels:
            channel_to_delete = st.selectbox(
                "Select channel to delete",
                options=[channel[1] for channel in channels],
                key="delete_channel"
            )
            if st.button("Delete"):
                channel_id = next(channel[0] for channel in channels if channel[1] == channel_to_delete)
                delete_channel(channel_id)
                st.success(f"Deleted channel: {channel_to_delete}")
                st.rerun()

    # Main content
    channels = get_all_channels()
    if not channels:
        st.info("Please add some channels using the sidebar")
        return

    # Channel selector
    selected_channel_name = st.selectbox(
        "Select a channel",
        options=[channel[1] for channel in channels]
    )

    selected_channel_id = next(channel[0] for channel in channels if channel[1] == selected_channel_name)

    # Get and display channel stats
    stats = get_channel_stats(youtube, selected_channel_id)
    if stats:
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Subscribers", f"{stats['subscribers']:,}")
        with col2:
            st.metric("Total Views", f"{stats['views']:,}")
        with col3:
            st.metric("Total Videos", f"{stats['total_videos']:,}")

        # Get and display latest videos
        st.subheader("Latest Videos")
        videos = get_latest_videos(youtube, stats['playlist_id'])

        # Convert to DataFrame for better display
        df = pd.DataFrame(videos)
        df['published_at'] = pd.to_datetime(df['published_at']).dt.strftime('%Y-%m-%d')

        # Format numbers with thousands separator
        df['views'] = df['views'].apply(lambda x: f"{x:,}")
        df['likes'] = df['likes'].apply(lambda x: f"{x:,}")
        df['comments'] = df['comments'].apply(lambda x: f"{x:,}")

        st.dataframe(
            df,
            column_config={
                "title": "Video Title",
                "published_at": "Published Date",
                "views": "Views",
                "likes": "Likes",
                "comments": "Comments"
            },
            hide_index=True
        )

if __name__ == "__main__":
    main()
