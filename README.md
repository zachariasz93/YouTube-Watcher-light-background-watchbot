# YouTube Watcher (Light Background Watchbot)

A lightweight, Docker-based YouTube video watching automation tool that simulates organic viewing patterns to help increase video engagement metrics.

## Features

- **Headless Operation**: Runs efficiently in background without GUI
- **Docker Containerized**: Easy deployment and consistent environment
- **Chrome-based**: Uses latest Chrome with optimized settings for video playback
- **Cookie Handling**: Automatically accepts YouTube cookies and consent forms
- **Multiple Start Methods**: Various fallback methods to ensure video playback
- **User Activity Simulation**: Mimics natural user interactions (scrolling, focus)
- **Configurable Parameters**: Customizable watch duration and loop counts
- **Windows Batch Scripts**: Easy-to-use Windows launcher scripts

## Quick Start

### Prerequisites

- Docker installed on your system
- Windows (for batch script usage)

### Installation

1. Clone this repository
2. Build the Docker container:
   ```bash
   docker-compose build
   ```

### Usage

#### Windows Batch Script (Recommended)

```bash
# Headless mode with custom parameters
youtubebot.bat headless "https://youtu.be/VIDEO_ID" "0:01:30" 10

# GUI mode for testing
youtubebot.bat gui
```

#### Direct Docker Commands

```bash
# Headless mode
docker run --rm youtubebot-main-youtubebot:latest /app/start.sh headless --url "https://youtu.be/VIDEO_ID" --duration "00:01:30" --loops 10

# GUI mode with VNC access
docker-compose up
```

## Configuration

### Parameters

- **URL**: YouTube video URL (youtube.com or youtu.be format)
- **Duration**: Watch time in HH:MM:SS format (e.g., "00:01:30" for 90 seconds)
- **Loops**: Number of viewing cycles to execute

### Docker Compose Profiles

- **Default**: Headless mode for production use
- **VNC**: GUI mode with web-based VNC access on port 6080

## Technical Details

### Architecture

- **Base Image**: Python 3.9 slim
- **Browser**: Google Chrome 140+ with ChromeDriver
- **Display**: Xvfb virtual display for headless operation
- **Window Manager**: Fluxbox for GUI mode

### Video Playback Methods

The bot uses multiple fallback methods to ensure video starts:

1. Direct video element interaction
2. Programmatic `video.play()` calls
3. Muted autoplay for policy compliance
4. Play button detection and clicking
5. Keyboard spacebar simulation
6. JavaScript injection methods

### Anti-Detection Features

- Realistic user-agent strings
- Human-like interaction patterns
- Random scroll behaviors
- Natural timing between actions
- Cookie acceptance handling

## Docker Management

### Disk Space Management

Docker can consume significant disk space. Monitor usage:

```bash
# Check Docker disk usage
docker system df

# Clean up unused data
docker system prune -a --volumes -f
```

### Container Cleanup

Containers are automatically removed after each run (`--rm` flag). For manual cleanup:

```bash
# Remove all stopped containers
docker container prune -f

# Remove unused images
docker image prune -a -f
```

## Security Considerations

- No personal data or credentials are stored
- Uses standard YouTube public URLs only
- No authentication or login required
- Runs in isolated Docker containers
- Automatic cleanup prevents data persistence

## Legal Notice

This tool is for educational and testing purposes. Users are responsible for:

- Complying with YouTube's Terms of Service
- Respecting content creators' rights
- Following applicable laws and regulations
- Using responsibly and ethically

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## License

This project is licensed under the MIT License. See LICENSE.md for details.

## Support

For issues and questions:

1. Check the troubleshooting section below
2. Review Docker logs for error details
3. Ensure proper URL formatting
4. Verify Docker is running correctly

### Troubleshooting

**Video not starting:**
- Check if YouTube URL is accessible
- Verify Docker container has internet access
- Try shorter duration for testing

**Docker build failures:**
- Ensure sufficient disk space (5GB+ recommended)
- Check internet connection for downloads
- Clean Docker cache if needed

**Windows batch script issues:**
- Run PowerShell as Administrator
- Ensure Docker Desktop is running
- Check path formatting in commands