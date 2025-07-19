#!/usr/bin/env python
"""
Text to Video Generator
Converts text files into video frames with readable, centered text.
Each frame displays a portion of text and lasts 2 seconds.
Improved with emoji support.
"""

import os
import sys
import argparse
import subprocess
import tempfile
import textwrap
import unicodedata
from pathlib import Path


class TextToVideoGenerator:
    def __init__(self, font_size=32, font_family="Arial", width=1920, height=1080,
                 background_color="black", text_color="white", frame_duration=2,
                 convert_emojis=True):
        """
        Initialize the text to video generator.

        Args:
            font_size (int): Size of the font
            font_family (str): Font family name
            width (int): Video width in pixels
            height (int): Video height in pixels
            background_color (str): Background color
            text_color (str): Text color
            frame_duration (int): Duration of each frame in seconds
            convert_emojis (bool): Convert emojis to text descriptions
        """
        self.font_size = font_size
        self.font_family = font_family
        self.width = width
        self.height = height
        self.background_color = background_color
        self.text_color = text_color
        self.frame_duration = frame_duration
        self.convert_emojis = convert_emojis

        # Calculate text area dimensions (leaving margins)
        self.text_width = int(self.width * 0.8)  # 80% of video width
        self.text_height = int(self.height * 0.8)  # 80% of video height

        # Estimate characters per line and lines per frame
        # Use more conservative estimate for emoji support
        self.chars_per_line = max(1, self.text_width // (self.font_size // 1.5))
        self.lines_per_frame = max(1, self.text_height // (self.font_size + 10))

    def read_text_file(self, file_path):
        """Read and return the content of a text file."""
        try:
            with open(file_path, "r", encoding="utf-8") as file:
                return file.read()
        except FileNotFoundError:
            print(f"Error: File '{file_path}' not found.")
            sys.exit(1)
        except UnicodeDecodeError:
            print(f"Error: Unable to decode '{file_path}'. Please ensure it's a valid text file.")
            sys.exit(1)

    def convert_emojis_to_text(self, text):
        """Convert common emojis to text descriptions for better compatibility."""
        emoji_map = {
            '👋': '[wave]',
            '😀': '[smile]',
            '😃': '[grin]',
            '😄': '[happy]',
            '😊': '[smile]',
            '🚀': '[rocket]',
            '🌟': '[star]',
            '💻': '[computer]',
            '🎉': '[party]',
            '🎨': '[art]',
            '🎭': '[theater]',
            '🎪': '[circus]',
            '🎯': '[target]',
            '🎲': '[dice]',
            '🎸': '[guitar]',
            '🎺': '[trumpet]',
            '🎻': '[violin]',
            '🔥': '[fire]',
            '💡': '[lightbulb]',
            '📱': '[phone]',
            '📧': '[email]',
            '📅': '[calendar]',
            '📈': '[chart]',
            '🏆': '[trophy]',
            '💧': '[water]',
            '☀️': '[sun]',
            '🌙': '[moon]',
            '⭐': '[star]',
            '❤️': '[heart]',
            '💛': '[yellow heart]',
            '💚': '[green heart]',
            '💙': '[blue heart]',
            '💜': '[purple heart]',
            '🌳': '[tree]',
            '🌲': '[evergreen]',
            '🍎': '[apple]',
            '🥪': '[sandwich]',
            '✨': '[sparkles]',
            '🖼️': '[picture]',
            '👨‍💻': '[man technologist]',
            '👩‍🚀': '[woman astronaut]',
            '🏳️‍🌈': '[rainbow flag]',
        }

        for emoji, replacement in emoji_map.items():
            text = text.replace(emoji, replacement)

        return text

    def find_emoji_compatible_font(self):
        """Find a font that supports emojis and works with FFmpeg."""
        # Use fonts that work well with FFmpeg's drawtext filter
        # Order by Unicode/international character support
        emoji_fonts = [
            '/usr/share/fonts/noto/NotoSans-Regular.ttf',         # Best overall Unicode support
            '/usr/share/fonts/noto/NotoSansSymbols-Regular.ttf',  # Good symbol support
            '/usr/share/fonts/noto/NotoSansSymbols2-Regular.ttf', # Additional symbols
            '/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf',
            '/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',
            '/usr/share/fonts/TTF/DejaVuSans.ttf'
        ]

        for font in emoji_fonts:
            if os.path.exists(font):
                print(f"Using font: {font}")
                return font

        # Fallback
        fallback = '/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf'
        print(f"Using fallback font: {fallback}")
        return fallback

    def wrap_text_with_emoji_support(self, text, width):
        """
        Wrap text with better emoji support.
        Emojis are treated as wider characters to prevent layout issues.
        """
        # Split text into words
        words = text.split()
        lines = []
        current_line = []
        current_width = 0

        for word in words:
            # Estimate visual width of the word
            word_width = 0

            for char in word:
                # Count emojis and wide characters as taking more space
                if unicodedata.category(char) == 'So':  # Symbol, other (includes many emojis)
                    word_width += 2  # Emojis take roughly 2 character widths
                elif unicodedata.east_asian_width(char) in ('F', 'W'):  # Full-width or Wide
                    word_width += 2
                else:
                    word_width += 1

            # Add space between words (except for first word in line)
            space_width = 1 if current_line else 0

            # Check if we need to start a new line
            if current_width + word_width + space_width > width and current_line:
                lines.append(' '.join(current_line))
                current_line = [word]
                current_width = word_width
            else:
                current_line.append(word)
                current_width += word_width + space_width

        # Add the last line if it has content
        if current_line:
            lines.append(' '.join(current_line))

        return lines

    def split_text_into_frames(self, text):
        """
        Split text into chunks that fit nicely in video frames.

        Args:
            text (str): The input text

        Returns:
            list: List of text chunks for each frame
        """
        # Clean and prepare text
        text = text.strip()

        if not text:
            return [""]

        # Convert emojis to text if enabled
        if self.convert_emojis:
            text = self.convert_emojis_to_text(text)
            print("Converted emojis to text descriptions for better compatibility")

        # Split into paragraphs first
        paragraphs = [p.strip() for p in text.split("\n\n") if p.strip()]

        frames = []
        current_frame_lines = []
        current_line_count = 0

        for paragraph in paragraphs:
            # Use emoji-aware text wrapping
            wrapped_lines = self.wrap_text_with_emoji_support(paragraph, self.chars_per_line)

            for line in wrapped_lines:
                # Check if adding this line would exceed frame capacity
                if current_line_count + 1 > self.lines_per_frame and current_frame_lines:
                    # Save current frame and start a new one
                    frames.append("\n".join(current_frame_lines))
                    current_frame_lines = []
                    current_line_count = 0

                current_frame_lines.append(line)
                current_line_count += 1

            # Add empty line after paragraph if there's room
            if current_line_count < self.lines_per_frame:
                current_frame_lines.append("")
                current_line_count += 1

        # Add the last frame if it has content
        if current_frame_lines:
            frames.append('\n'.join(current_frame_lines))

        return frames if frames else [""]

    def escape_text_for_ffmpeg(self, text):
        """Escape text for use in FFmpeg drawtext filter."""
        # Normalize the text to handle Unicode properly
        return unicodedata.normalize("NFC", text)

    def create_frame_video(self, text, output_path):
        """
        Create a video file for a single frame of text.

        Args:
            text (str): Text content for the frame
            output_path (str): Path to save the frame video
        """
        font_path = self.find_emoji_compatible_font()

        # For better emoji support, use textfile approach directly
        # This is more reliable for complex Unicode content including emojis
        self._create_frame_video_with_textfile(text, output_path, font_path)

    def _create_frame_video_with_textfile(self, text, output_path, font_path):
        """
        Create frame video using textfile approach for better Unicode support.
        """
        # Create a temporary text file with plain UTF-8 encoding
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False, encoding='utf-8') as f:
            f.write(text)
            text_file_path = f.name

        # Debug: check what we actually wrote to the file
        with open(text_file_path, 'r', encoding='utf-8') as f:
            written_text = f.read()
            print(f"Debug: Written to temp file: {repr(written_text[:100])}")

        try:
            # Use textfile parameter with explicit encoding
            cmd = [
                "ffmpeg",
                "-f", "lavfi",
                "-i", f"color=c={self.background_color}:size={self.width}x{self.height}:duration={self.frame_duration}:rate=30",
                "-vf", (
                    f"drawtext=textfile='{text_file_path}':"
                    f"fontfile={font_path}:"
                    f"fontsize={self.font_size}:"
                    f"fontcolor={self.text_color}:"
                    f"x=(w-text_w)/2:"
                    f"y=(h-text_h)/2:"
                    f"text_align=center"
                ),
                "-c:v", "libx264",
                "-pix_fmt", "yuv420p",
                "-y",
                output_path
            ]

            print(f"Debug: FFmpeg command: {' '.join(cmd)}")
            result = subprocess.run(cmd, check=True, capture_output=True, text=True)

        except subprocess.CalledProcessError as e:
            print(f"Error creating frame video: {e}")
            print(f"FFmpeg stderr: {e.stderr}")
            # Try fallback with escaped text instead of textfile
            try:
                print("Trying fallback method without textfile...")
                self._create_frame_video_fallback(text, output_path, font_path)
            except Exception as fallback_error:
                print(f"Fallback method also failed: {fallback_error}")
                raise e
        finally:
            # Clean up temporary text file
            if os.path.exists(text_file_path):
                os.unlink(text_file_path)

    def _create_frame_video_fallback(self, text, output_path, font_path):
        """Fallback method using escaped text directly."""
        escaped_text = self.escape_text_for_ffmpeg(text)
        print(f"Debug: Escaped text for fallback: {repr(escaped_text[:100])}")

        cmd = [
            "ffmpeg",
            "-f", "lavfi",
            "-i", f"color=c={self.background_color}:size={self.width}x{self.height}:duration={self.frame_duration}:rate=30",
            "-vf", (
                f"drawtext=text='{escaped_text}':"
                f"fontfile={font_path}:"
                f"fontsize={self.font_size}:"
                f"fontcolor={self.text_color}:"
                f"x=(w-text_w)/2:"
                f"y=(h-text_h)/2:"
                f"text_align=center"
            ),
            "-c:v", "libx264",
            "-pix_fmt", "yuv420p",
            "-y",
            output_path
        ]

        print(f"Debug: Fallback FFmpeg command: {' '.join(cmd)}")
        subprocess.run(cmd, check=True, capture_output=True, text=True)

    def concatenate_videos(self, video_files, output_path):
        """
        Concatenate multiple video files into one.

        Args:
            video_files (list): List of video file paths
            output_path (str): Path for the final concatenated video
        """
        # Create a temporary file list for FFmpeg concat
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
            for video_file in video_files:
                f.write(f"file '{video_file}'\n")

            concat_file = f.name

        try:
            cmd = [
                "ffmpeg",
                "-f", "concat",
                "-safe", "0",
                "-i", concat_file,
                "-c", "copy",
                "-y",  # Overwrite output file
                output_path
            ]

            subprocess.run(cmd, check=True, capture_output=True, text=True)
        except subprocess.CalledProcessError as e:
            print(f"Error concatenating videos: {e}")
            print(f"FFmpeg stderr: {e.stderr}")
            raise
        finally:
            # Clean up temporary file
            os.unlink(concat_file)

    def generate_video(self, text_file_path, output_video_path):
        """
        Generate a complete video from a text file.

        Args:
            text_file_path (str): Path to the input text file
            output_video_path (str): Path for the output video file
        """
        print(f"Reading text from: {text_file_path}")
        text_content = self.read_text_file(text_file_path)
        text_content = "".join(char if char.isalnum() or char.isspace() or char in ["?", "!", "'", ".", ","] else " " for char in text_content)
        text_content = text_content.strip()

        print("Splitting text into frames...")
        frames = self.split_text_into_frames(text_content)

        print(f"Creating {len(frames)} frames...")

        # Create temporary directory for frame videos
        with tempfile.TemporaryDirectory() as temp_dir:
            frame_videos = []

            for i, frame_text in enumerate(frames):
                frame_video_path = os.path.join(temp_dir, f"frame_{i:04d}.mp4")
                print(f"Creating frame {i+1}/{len(frames)}")

                self.create_frame_video(frame_text, frame_video_path)
                frame_videos.append(frame_video_path)

            print("Concatenating frames into final video...")
            self.concatenate_videos(frame_videos, output_video_path)

        print(f"Video created successfully: {output_video_path}")
        print(f"Total frames: {len(frames)}")
        print(f"Total duration: {len(frames) * self.frame_duration} seconds")


def check_ffmpeg():
    """Check if FFmpeg is available in the system."""
    try:
        subprocess.run(["ffmpeg", "-version"], capture_output=True, check=True)
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        return False


def main():
    parser = argparse.ArgumentParser(
        description="Convert text files to video with readable, centered text frames (with emoji support)",
        epilog="""
Examples:
  python3 mev.py text.txt                           # Basic usage
  python3 mev.py text.txt -o video.mp4              # Custom output name
  python3 mev.py text.txt --font-size 48            # Larger text
  python3 mev.py text.txt --keep-emojis             # Keep original emojis (may not display)
  python3 mev.py text.txt --duration 3              # 3 seconds per frame

Note: By default, emojis are converted to text descriptions like [wave], [smile] etc.
for better compatibility with video output. Use --keep-emojis to preserve original emojis.
        """,
        formatter_class=argparse.RawDescriptionHelpFormatter
    )

    parser.add_argument(
        "input_file",
        help="Path to the input text file"
    )

    parser.add_argument(
        "-o", "--output",
        default="output_video.mp4",
        help="Output video file path (default: output_video.mp4)"
    )

    parser.add_argument(
        "--font-size",
        type=int,
        default=32,
        help="Font size for text (default: 32)"
    )

    parser.add_argument(
        "--width",
        type=int,
        default=1920,
        help="Video width in pixels (default: 1920)"
    )

    parser.add_argument(
        "--height",
        type=int,
        default=1080,
        help="Video height in pixels (default: 1080)"
    )

    parser.add_argument(
        "--duration",
        type=int,
        default=4,
        help="Duration of each frame in seconds (default: 2)"
    )

    parser.add_argument(
        "--background-color",
        default="black",
        help="Background color (default: black)"
    )

    parser.add_argument(
        "--text-color",
        default="white",
        help="Text color (default: white)"
    )

    parser.add_argument(
        "--keep-emojis",
        action="store_true",
        help="Keep original emojis (may not display properly in video)"
    )

    args = parser.parse_args()

    # Check if FFmpeg is available
    if not check_ffmpeg():
        print("Error: FFmpeg is not installed or not available in PATH.")
        print("Please install FFmpeg to use this script.")
        print("On Ubuntu/Debian: sudo apt install ffmpeg")
        print("On macOS: brew install ffmpeg")
        sys.exit(1)

    # Check if input file exists
    if not os.path.exists(args.input_file):
        print(f"Error: Input file '{args.input_file}' does not exist.")
        sys.exit(1)

    # Create output directory if it doesn't exist
    output_dir = os.path.dirname(os.path.abspath(args.output))

    if output_dir and not os.path.exists(output_dir):
        os.makedirs(output_dir)

    # Create the generator and process the file
    convert_emojis = not args.keep_emojis  # If keep_emojis is True, don't convert

    generator = TextToVideoGenerator(
        font_size=args.font_size,
        width=args.width,
        height=args.height,
        background_color=args.background_color,
        text_color=args.text_color,
        frame_duration=args.duration,
        convert_emojis=convert_emojis
    )

    try:
        generator.generate_video(args.input_file, args.output)
    except Exception as e:
        print(f"Error generating video: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
