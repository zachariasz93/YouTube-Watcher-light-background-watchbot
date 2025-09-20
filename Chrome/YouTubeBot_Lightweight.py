#!/usr/bin/env python3
"""
YouTube Bot - Lightweight version without browser
Ultra-efficient version using only HTTP requests
"""

import requests
import time
import random
import re
import json
import argparse
import sys
from urllib.parse import urlparse, parse_qs
from datetime import datetime

class LightweightYouTubeWatcher:
    def __init__(self):
        self.session = requests.Session()
        self.setup_headers()
        
    def setup_headers(self):
        """Setup realistic browser headers"""
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/140.0.7339.185 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
            'Accept-Language': 'pl-PL,pl;q=0.9,en;q=0.8',
            'Accept-Encoding': 'gzip, deflate, br',
            'DNT': '1',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'none',
            'Cache-Control': 'max-age=0'
        })
    
    def extract_video_id(self, url):
        """Extract video ID from YouTube URL"""
        patterns = [
            r'(?:youtube\.com\/watch\?v=|youtu\.be\/|youtube\.com\/embed\/)([^&\n?#]+)',
            r'youtube\.com\/watch\?.*v=([^&\n?#]+)',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, url)
            if match:
                return match.group(1)
        
        raise ValueError("Invalid YouTube URL")
    
    def get_video_page(self, video_id):
        """Get YouTube video page and extract necessary data"""
        url = f"https://www.youtube.com/watch?v={video_id}"
        
        print(f"🌐 Pobieranie strony: {url}")
        response = self.session.get(url)
        
        if response.status_code != 200:
            raise Exception(f"Failed to load video page: {response.status_code}")
        
        html_content = response.text
        
        # Extract video metadata
        video_data = self.extract_video_metadata(html_content)
        
        # Extract tracking parameters
        tracking_data = self.extract_tracking_data(html_content)
        
        return {
            'video_data': video_data,
            'tracking_data': tracking_data,
            'cookies': dict(response.cookies)
        }
    
    def extract_video_metadata(self, html_content):
        """Extract video metadata from page"""
        video_data = {}
        
        # Extract title
        title_match = re.search(r'"title":"([^"]+)"', html_content)
        if title_match:
            video_data['title'] = title_match.group(1).replace('\\u0026', '&')
        
        # Extract duration
        duration_match = re.search(r'"lengthSeconds":"(\d+)"', html_content)
        if duration_match:
            video_data['duration'] = int(duration_match.group(1))
        
        # Extract view count
        view_match = re.search(r'"viewCount":"(\d+)"', html_content)
        if view_match:
            video_data['views'] = int(view_match.group(1))
        
        return video_data
    
    def extract_tracking_data(self, html_content):
        """Extract tracking parameters needed for watch requests"""
        tracking_data = {}
        
        # Extract visitor data
        visitor_match = re.search(r'"VISITOR_DATA":"([^"]+)"', html_content)
        if visitor_match:
            tracking_data['visitor_data'] = visitor_match.group(1)
        
        # Extract session token
        session_match = re.search(r'"XSRF_TOKEN":"([^"]+)"', html_content)
        if session_match:
            tracking_data['session_token'] = session_match.group(1)
        
        # Extract client version
        client_match = re.search(r'"INNERTUBE_CLIENT_VERSION":"([^"]+)"', html_content)
        if client_match:
            tracking_data['client_version'] = client_match.group(1)
        
        return tracking_data
    
    def simulate_watch_session(self, video_id, duration_seconds, video_info):
        """Simulate watching the video by sending periodic requests"""
        print(f"🎬 Rozpoczynam symulację oglądania na {duration_seconds} sekund")
        
        if 'video_data' in video_info and 'title' in video_info['video_data']:
            print(f"📺 Video: {video_info['video_data']['title'][:50]}...")
        
        # Initial watch request
        self.send_watch_request(video_id, 0, video_info)
        
        # Periodic heartbeat requests
        heartbeat_interval = random.uniform(5, 15)  # Every 5-15 seconds
        next_heartbeat = heartbeat_interval
        
        start_time = time.time()
        
        for elapsed in range(1, duration_seconds + 1):
            current_time = time.time()
            
            # Send heartbeat request periodically
            if elapsed >= next_heartbeat:
                self.send_heartbeat_request(video_id, elapsed, video_info)
                next_heartbeat += random.uniform(8, 20)
            
            # Send watch time update
            if elapsed % 10 == 0:  # Every 10 seconds
                self.send_watch_time_update(video_id, elapsed, video_info)
            
            # Progress indicator
            if elapsed % 10 == 0 or elapsed == duration_seconds:
                print(f"⏱️  Progress: {elapsed}/{duration_seconds} seconds")
            
            # Realistic sleep with small variations
            sleep_time = max(0.1, 1.0 + random.uniform(-0.2, 0.2))
            time.sleep(sleep_time)
        
        # Final watch completion request
        self.send_watch_completion(video_id, duration_seconds, video_info)
        
        print(f"✅ Zakończono oglądanie po {duration_seconds} sekundach")
    
    def send_watch_request(self, video_id, current_time, video_info):
        """Send initial watch request"""
        try:
            url = "https://www.youtube.com/youtubei/v1/player/heartbeat"
            
            payload = {
                "videoId": video_id,
                "currentTime": current_time,
                "context": {
                    "client": {
                        "clientName": "WEB",
                        "clientVersion": video_info.get('tracking_data', {}).get('client_version', '2.0')
                    }
                }
            }
            
            headers = {
                'Content-Type': 'application/json',
                'X-YouTube-Client-Name': '1',
                'X-YouTube-Client-Version': '2.0'
            }
            
            response = self.session.post(url, json=payload, headers=headers, timeout=10)
            print(f"🔄 Watch request: {response.status_code}")
            
        except Exception as e:
            print(f"⚠️  Watch request error: {e}")
    
    def send_heartbeat_request(self, video_id, current_time, video_info):
        """Send heartbeat to maintain session"""
        try:
            url = "https://www.youtube.com/api/stats/watchtime"
            
            params = {
                'ns': 'yt',
                'el': 'detailpage',
                'cpn': self.generate_cpn(),
                'docid': video_id,
                'ver': '2',
                'cmt': str(current_time),
                'ei': self.generate_ei(),
                'fmt': '243',
                'fs': '0',
                'rt': str(random.randint(50, 200)),
                'of': 'EiQSFhMpqFnCBVUe8ZdS44IlGhgA',
                'euri': '',
                'lact': str(random.randint(100, 5000)),
                'live': 'dvr',
                'cl': '123456789',
                'state': 'playing',
                'vm': 'CAEQAA',
                'volume': '100',
                'c': 'WEB',
                'cver': '2.0',
                'cplayer': 'UNIPLAYER',
                'cbr': 'Chrome',
                'cbrver': '140.0.7339.185',
                'cos': 'Windows',
                'cosver': '10.0',
                'hl': 'pl_PL',
                'cr': 'PL',
                'rtn': str(current_time)
            }
            
            response = self.session.get(url, params=params, timeout=10)
            
        except Exception as e:
            print(f"⚠️  Heartbeat error: {e}")
    
    def send_watch_time_update(self, video_id, current_time, video_info):
        """Send watch time update"""
        try:
            url = "https://www.youtube.com/api/stats/qoe"
            
            params = {
                'ns': 'yt',
                'cpn': self.generate_cpn(),
                'docid': video_id,
                'ver': '2',
                'cmt': str(current_time),
                'ei': self.generate_ei(),
                'of': 'EiQSFhMpqFnCBVUe8ZdS44IlGhgA',
                'uga': 'f1',
                'len': str(current_time),
                'rtn': str(current_time),
                'ml': '20.0',
                'mt': str(current_time),
                'pl': '0.0',
                'rti': str(random.randint(50, 200)),
                'qoe_fmt': 'sd',
                'hl': 'pl_PL',
                'c': 'WEB',
                'cver': '2.0'
            }
            
            response = self.session.get(url, params=params, timeout=10)
            
        except Exception as e:
            print(f"⚠️  Watch time update error: {e}")
    
    def send_watch_completion(self, video_id, total_time, video_info):
        """Send completion signal"""
        try:
            url = "https://www.youtube.com/api/stats/playback"
            
            params = {
                'ns': 'yt',
                'cpn': self.generate_cpn(),
                'docid': video_id,
                'ei': self.generate_ei(),
                'event': 'complete',
                'len': str(total_time),
                'cmt': str(total_time),
                'rtn': str(total_time),
                'hl': 'pl_PL',
                'c': 'WEB',
                'cver': '2.0'
            }
            
            response = self.session.get(url, params=params, timeout=10)
            print(f"🏁 Completion signal: {response.status_code}")
            
        except Exception as e:
            print(f"⚠️  Completion error: {e}")
    
    def generate_cpn(self):
        """Generate Client Playback Nonce"""
        import string
        return ''.join(random.choices(string.ascii_letters + string.digits, k=16))
    
    def generate_ei(self):
        """Generate Event ID"""
        import string
        return ''.join(random.choices(string.ascii_letters + string.digits + '-_', k=11))

def duration_to_seconds(duration_str):
    """Convert HH:MM:SS to seconds"""
    try:
        parts = duration_str.split(":")
        if len(parts) != 3:
            raise ValueError("Duration must be in HH:MM:SS format")
        
        hours = int(parts[0])
        minutes = int(parts[1])
        seconds = int(parts[2])
        
        return hours * 3600 + minutes * 60 + seconds
    except (ValueError, IndexError) as e:
        raise ValueError(f"Invalid duration format: {e}")

def validate_youtube_url(url):
    """Check if URL is valid YouTube link"""
    youtube_domains = ['youtube.com', 'youtu.be', 'www.youtube.com']
    return any(domain in url for domain in youtube_domains)

def main():
    parser = argparse.ArgumentParser(description='YouTube Bot - Lightweight version (no browser)')
    parser.add_argument('--url', required=True, help='YouTube video URL')
    parser.add_argument('--duration', required=True, help='Watch duration in HH:MM:SS format')
    parser.add_argument('--loops', required=True, help='Number of loops (or "inf" for infinite)')
    parser.add_argument('--delay', type=int, default=10, help='Delay between loops in seconds')
    
    args = parser.parse_args()
    
    # URL validation
    if not validate_youtube_url(args.url):
        print("Error: Invalid YouTube URL")
        sys.exit(1)
    
    # Duration conversion
    try:
        duration_seconds = duration_to_seconds(args.duration)
    except ValueError as e:
        print(f"Error: {e}")
        sys.exit(1)
    
    # Loop count conversion
    if args.loops.lower() == 'inf':
        loops = 999999999
    else:
        try:
            loops = int(args.loops)
            if loops <= 0:
                raise ValueError("Loops must be positive")
        except ValueError:
            print("Error: Loops must be a positive integer or 'inf'")
            sys.exit(1)
    
    print(f"🚀 Starting Lightweight YouTube Bot")
    print(f"📺 URL: {args.url}")
    print(f"⏱️  Duration: {duration_seconds} seconds")
    print(f"🔄 Loops: {loops}")
    print("-" * 60)
    
    # Initialize bot
    bot = LightweightYouTubeWatcher()
    
    try:
        video_id = bot.extract_video_id(args.url)
        print(f"🎬 Video ID: {video_id}")
        
        for i in range(loops):
            print(f"\n🔄 Starting loop {i+1}/{loops}")
            
            try:
                # Get video information
                video_info = bot.get_video_page(video_id)
                
                # Simulate watching
                bot.simulate_watch_session(video_id, duration_seconds, video_info)
                
                print(f"✅ Loop {i+1} completed successfully")
                
                # Delay between loops
                if i < loops - 1:
                    print(f"⏳ Waiting {args.delay} seconds before next loop...")
                    time.sleep(args.delay)
                    
            except Exception as e:
                print(f"❌ Error in loop {i+1}: {e}")
                continue
        
        print(f"\n🎉 All loops completed successfully!")
        
    except KeyboardInterrupt:
        print("\n⛔ Bot stopped by user")
    except Exception as e:
        print(f"❌ Fatal error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()