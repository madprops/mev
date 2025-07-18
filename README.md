# Text to Video Generator

A Python script that converts text files into video content with readable, centered text frames using FFmpeg.

## Features

- Automatically splits text into readable frames
- Customizable font size, video dimensions, and colors
- Each frame displays for 3 seconds (configurable)
- Text is centered and properly formatted
- No text cramming - ensures readability
- Uses FFmpeg for high-quality video generation

## Prerequisites

- Python 3.6+
- FFmpeg installed on your system

### Installing FFmpeg

**Ubuntu/Debian:**
```bash
sudo apt install ffmpeg
```

**macOS:**
```bash
brew install ffmpeg
```

**Windows:**
Download from [https://ffmpeg.org/download.html](https://ffmpeg.org/download.html)

## Usage

### Basic Usage

```bash
python anser.py input_text.txt
```

This will create `output_video.mp4` from `input_text.txt`.

### Advanced Usage

```bash
python anser.py input_text.txt -o my_video.mp4 --font-size 40 --width 1280 --height 720 --duration 3
```

### Command Line Options

- `input_file`: Path to the input text file (required)
- `-o, --output`: Output video file path (default: output_video.mp4)
- `--font-size`: Font size for text (default: 32)
- `--width`: Video width in pixels (default: 1920)
- `--height`: Video height in pixels (default: 1080)
- `--duration`: Duration of each frame in seconds (default: 2)
- `--background-color`: Background color (default: black)
- `--text-color`: Text color (default: white)

### Examples

**Create a 720p video with larger text:**
```bash
python anser.py story.txt -o story_video.mp4 --width 1280 --height 720 --font-size 36
```

**Create a video with white background and black text:**
```bash
python anser.py document.txt -o document.mp4 --background-color white --text-color black
```

**Create a video with longer frame duration:**
```bash
python anser.py slow_read.txt -o slow_video.mp4 --duration 4
```

## How It Works

1. **Text Processing**: The script reads your text file and intelligently splits it into chunks that fit comfortably in video frames
2. **Frame Generation**: Each text chunk is rendered as a video frame with centered, readable text
3. **Video Assembly**: All frames are concatenated into a single video file

## Text Formatting Tips

- Use double line breaks to separate paragraphs
- The script automatically wraps long lines
- Text is centered both horizontally and vertically
- Maintains readability by not cramming too much text per frame

## Example

Try the included example:
```bash
python anser.py example_text.txt -o example_output.mp4
```

## Troubleshooting

**"FFmpeg not found" error:**
- Make sure FFmpeg is installed and available in your system PATH

**"Permission denied" error:**
- Ensure you have write permissions in the output directory

**"File not found" error:**
- Check that your input text file exists and the path is correct

## License

This script is provided as-is for educational and practical use.
