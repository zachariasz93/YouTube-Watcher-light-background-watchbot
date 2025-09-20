#!/usr/bin/env python3
"""
YouTube Bot - Headless version for Docker
Headless GUI-free version dedicated for Docker environment
"""

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
import time
import sys
import argparse
import os

def get_chrome_driver():
    """Configure Chrome driver for headless environment"""
    chrome_options = Options()
    
    # Headless environment options
    chrome_options.add_argument('--headless')
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')
    chrome_options.add_argument('--disable-gpu')
    chrome_options.add_argument('--remote-debugging-port=9222')
    chrome_options.add_argument('--window-size=1920,1080')
    
    # Anti-detection options
    chrome_options.add_argument('--disable-blink-features=AutomationControlled')
    chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
    chrome_options.add_experimental_option('useAutomationExtension', False)
    chrome_options.add_argument('--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/140.0.7339.185 Safari/537.36')
    
    # Options for better video playback
    chrome_options.add_argument('--autoplay-policy=no-user-gesture-required')
    chrome_options.add_argument('--disable-features=VizDisplayCompositor')
    chrome_options.add_argument('--allow-running-insecure-content')
    chrome_options.add_argument('--disable-extensions')
    chrome_options.add_argument('--disable-plugins')
    chrome_options.add_argument('--disable-web-security')
    chrome_options.add_argument('--allow-cross-origin-auth-prompt')
    
    # Media preferences
    prefs = {
        "profile.default_content_setting_values": {
            "media_stream": 1,
            "media_stream_mic": 1,
            "media_stream_camera": 1,
            "notifications": 2
        }
    }
    chrome_options.add_experimental_option("prefs", prefs)
    
    # Use ChromeDriverManager to automatically download and manage chromedriver
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=chrome_options)
    driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
    return driver

def accept_cookies_and_prepare(driver):
    """Accepts cookies and prepares page for playback"""
    print("🍪 Checking and accepting cookies...")
    
    try:
        # Wait for page to load
        WebDriverWait(driver, 10).until(
            lambda d: d.execute_script("return document.readyState") == "complete"
        )
        
        # Try to find and click cookie acceptance button
        cookie_selectors = [
            'button[aria-label*="Accept"]',
            'button[aria-label*="Zaakceptuj"]', 
            'button[aria-label*="Akceptuj"]',
            '.VfPpkd-LgbsSe[jsname="tWT92d"]',  # Google's accept button
            'button[jsname="tWT92d"]',
            '[data-testid="accept-button"]'
        ]
        
        for selector in cookie_selectors:
            try:
                cookie_button = WebDriverWait(driver, 3).until(
                    EC.element_to_be_clickable((By.CSS_SELECTOR, selector))
                )
                cookie_button.click()
                print("✅ Zaakceptowano cookies")
                time.sleep(2)
                return True
            except:
                continue
        
        # Try with XPath for buttons containing text
        xpath_selectors = [
            "//button[contains(text(), 'Accept all')]",
            "//button[contains(text(), 'Zaakceptuj wszystkie')]",
            "//button[contains(text(), 'Accept')]",
            "//button[contains(text(), 'Akceptuj')]"
        ]
        
        for xpath in xpath_selectors:
            try:
                cookie_button = WebDriverWait(driver, 3).until(
                    EC.element_to_be_clickable((By.XPATH, xpath))
                )
                cookie_button.click()
                print("✅ Zaakceptowano cookies (XPath)")
                time.sleep(2)
                return True
            except:
                continue
                
        print("ℹ️ Cookie button not found or already accepted")
        return False
        
    except Exception as e:
        print(f"⚠️ Error while accepting cookies: {e}")
        return False


def duration_to_seconds(duration_str):
    """Converts time in HH:MM:SS format to seconds"""
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
    """Checks if URL is a valid YouTube link"""
    youtube_domains = ['youtube.com', 'youtu.be', 'www.youtube.com']
    return any(domain in url for domain in youtube_domains)

def run_youtube_bot(url, duration_seconds, loops):
    """Main YouTube bot function"""
    print(f"Starting YouTube Bot")
    print(f"URL: {url}")
    print(f"Duration: {duration_seconds} seconds")
    print(f"Loops: {loops}")
    print("-" * 50)
    
    for i in range(loops):
        try:
            print(f"Starting loop {i+1}/{loops}")
            
            # Create new browser instance for each loop
            driver = get_chrome_driver()
            driver.get(url)
            
            # Accept cookies if required
            accept_cookies_and_prepare(driver)
            
            # Wait for page to load and try to start video
            wait = WebDriverWait(driver, 15)
            
            print("Waiting for page to load...")
            time.sleep(5)
                
            # Try different methods to start video
            video_started = False
            
            # Method 1: Video element interaction
            try:
                video_element = wait.until(EC.presence_of_element_located((By.TAG_NAME, "video")))
                print("🎥 Found video element")
                
                # Check if video is paused
                is_paused = driver.execute_script("return arguments[0].paused;", video_element)
                current_time = driver.execute_script("return arguments[0].currentTime;", video_element)
                print(f"📊 Video state - Paused: {is_paused}, Time: {current_time}")
                
                if is_paused:
                    print("⏸️ Video is paused, trying multiple activation methods...")
                    
                    # Attempt 1: Click on video
                    try:
                        driver.execute_script("arguments[0].click();", video_element)
                        time.sleep(1)
                        print("🖱️ Clicked video element")
                    except Exception as e:
                        print(f"⚠️ Video click failed: {e}")
                    
                    # Attempt 2: Programmatic start
                    try:
                        driver.execute_script("arguments[0].play();", video_element)
                        time.sleep(1)
                        print("🎬 Executed video.play()")
                    except Exception as e:
                        print(f"⚠️ Programmatic play failed: {e}")
                    
                    # Attempt 3: Muted autoplay event
                    try:
                        driver.execute_script("""
                            arguments[0].muted = true;
                            arguments[0].play().then(() => {
                                console.log('Video started with muted autoplay');
                            }).catch(e => {
                                console.log('Muted autoplay failed:', e);
                            });
                        """, video_element)
                        time.sleep(1)
                        print("🔇 Tried muted autoplay")
                    except Exception as e:
                        print(f"⚠️ Muted autoplay failed: {e}")
                    
                    # Check result
                    is_paused_after = driver.execute_script("return arguments[0].paused;", video_element)
                    time_after = driver.execute_script("return arguments[0].currentTime;", video_element)
                    
                    if not is_paused_after or time_after > current_time:
                        print("✅ Video started successfully!")
                        video_started = True
                    else:
                        print("⚠️ Video still paused after attempts")
                else:
                    print("▶️ Video is already playing")
                    video_started = True
                    
            except Exception as e:
                print(f"❌ Video element interaction failed: {e}")
            
            # Method 2: Try to find and click play button
            if not video_started:
                print("🔍 Searching for play button...")
                try:
                    # Extended selectors for the play button
                    play_selectors = [
                        (By.CLASS_NAME, "ytp-play-button"),
                        (By.CSS_SELECTOR, ".ytp-play-button"),
                        (By.CSS_SELECTOR, ".ytp-large-play-button"),
                        (By.CSS_SELECTOR, "button[aria-label*='Play']"),
                        (By.CSS_SELECTOR, "button[aria-label*='Odtwórz']"),
                        (By.CSS_SELECTOR, "button[title*='Play']"),
                        (By.CSS_SELECTOR, "button[title*='Odtwórz']"),
                        (By.CSS_SELECTOR, "[data-title-no-tooltip='Play']"),
                        (By.CSS_SELECTOR, "[data-title-no-tooltip='Odtwórz']"),
                        (By.XPATH, "//button[contains(@aria-label, 'Play')]"),
                        (By.XPATH, "//button[contains(@aria-label, 'Odtwórz')]")
                    ]
                    
                    for selector_type, selector in play_selectors:
                        try:
                            play_button = WebDriverWait(driver, 2).until(
                                EC.element_to_be_clickable((selector_type, selector))
                            )
                            play_button.click()
                            print(f"✅ Clicked play button: {selector}")
                            time.sleep(2)
                            
                            # Check if video started
                            try:
                                video_element = driver.find_element(By.TAG_NAME, "video")
                                is_paused = driver.execute_script("return arguments[0].paused;", video_element)
                                if not is_paused:
                                    print("✅ Video started via play button")
                                    video_started = True
                                    break
                            except:
                                pass
                        except:
                            continue
                            
                except Exception as e:
                    print(f"⚠️ Play button search failed: {e}")
            
            # Method 3: User simulation - click and space
            if not video_started:
                print("⌨️ Trying user simulation methods...")
                try:
                    # First click on video area
                    video_container = driver.find_element(By.ID, "player")
                    if video_container:
                        driver.execute_script("arguments[0].focus();", video_container)
                        video_container.click()
                        print("🖱️ Clicked video container")
                        time.sleep(1)
                    
                    # Then use space
                    body = driver.find_element(By.TAG_NAME, "body")
                    body.send_keys(Keys.SPACE)
                    print("⌨️ Pressed spacebar")
                    time.sleep(2)
                    
                    # Check result
                    try:
                        video_element = driver.find_element(By.TAG_NAME, "video")
                        is_paused = driver.execute_script("return arguments[0].paused;", video_element)
                        if not is_paused:
                            print("✅ Video started with user simulation")
                            video_started = True
                    except:
                        pass
                        
                except Exception as e:
                    print(f"⚠️ User simulation failed: {e}")
            
            # Method 4: Final attempt - JavaScript injection
            if not video_started:
                print("🔧 Trying JavaScript injection method...")
                try:
                    # Try to find and start video through various JavaScript methods
                    driver.execute_script("""
                        // Method 1: Find all video elements
                        const videos = document.querySelectorAll('video');
                        for (let video of videos) {
                            if (video.paused) {
                                video.muted = true;
                                video.play().catch(e => console.log('Play failed:', e));
                            }
                        }
                        
                        // Method 2: Simulate click on player
                        const player = document.querySelector('#player');
                        if (player) {
                            player.click();
                        }
                        
                        // Method 3: Simulate spacebar
                        document.body.dispatchEvent(new KeyboardEvent('keydown', {
                            key: ' ',
                            code: 'Space',
                            keyCode: 32,
                            bubbles: true
                        }));
                        
                        // Method 4: Try to click play button
                        const playButtons = document.querySelectorAll(
                            '.ytp-play-button, .ytp-large-play-button, button[aria-label*="Play"], button[aria-label*="Odtwórz"]'
                        );
                        for (let button of playButtons) {
                            button.click();
                        }
                    """)
                    time.sleep(3)
                    
                    # Check result
                    try:
                        video_element = driver.find_element(By.TAG_NAME, "video")
                        is_paused = driver.execute_script("return arguments[0].paused;", video_element)
                        current_time = driver.execute_script("return arguments[0].currentTime;", video_element)
                        
                        if not is_paused and current_time > 0:
                            print("✅ Video started with JavaScript injection")
                            video_started = True
                        else:
                            print(f"⚠️ JS injection result - Paused: {is_paused}, Time: {current_time}")
                    except Exception as e:
                        print(f"⚠️ Could not verify JS injection result: {e}")
                        
                except Exception as e:
                    print(f"⚠️ JavaScript injection failed: {e}")
            
            # Check final status
            if video_started:
                print("✅ Video successfully started")
            else:
                print("⚠️ Could not confirm video started, but continuing...")
            
            # Simulate user activity
            driver.execute_script("window.scrollTo(0, 300);")
            time.sleep(2)
            driver.execute_script("window.scrollTo(0, 0);")
            
            print(f"Watching video for {duration_seconds} seconds...")
            
            # Wait for specified time with periodic checks
            check_interval = min(30, duration_seconds // 4)  # Check every 30s or every 1/4 of time
            elapsed = 0
            
            while elapsed < duration_seconds:
                sleep_time = min(check_interval, duration_seconds - elapsed)
                time.sleep(sleep_time)
                elapsed += sleep_time
                
                # Check if the page is still active
                try:
                    driver.current_url
                    if elapsed % 60 == 0:  # Every minute
                        print(f"Progress: {elapsed}/{duration_seconds} seconds")
                except:
                    print("Browser connection lost")
                    break
            
            print(f"Loop {i+1} completed successfully")
            
        except Exception as e:
            print(f"Error in loop {i+1}: {e}")
        finally:
            try:
                driver.quit()
            except:
                pass
        
        # Break between loops (if not the last loop)
        if i < loops - 1:
            print("Waiting 10 seconds before next loop...")
            time.sleep(10)
    
    print("YouTube Bot finished!")

def main():
    parser = argparse.ArgumentParser(description='YouTube Bot - Headless version')
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
    
    # Start the bot
    try:
        run_youtube_bot(args.url, duration_seconds, loops)
    except KeyboardInterrupt:
        print("\nBot stopped by user")
    except Exception as e:
        print(f"Unexpected error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()