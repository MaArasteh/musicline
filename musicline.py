from pygame import mixer
from argparse import ArgumentParser
from mutagen import File
import os
import re
import curses

pattern = re.compile(".*.*mp3$", re.IGNORECASE)


def read_audio_metadata(file_path, directory):
    try:
        audio = File(directory + '/' + file_path, easy=True)
        if audio is None:
            return 'Unknown', 'Unknown', 'Unknown'
        track_name = audio.get('title', ['Unknown'])[0]
        artist = audio.get('artist', ['Unknown'])[0]
        album = audio.get('album', ['Unknown'])[0]
        return track_name, artist, album
    except Exception as e:
        print(f"Error reading metadata from {file_path}: {e}")
        return None, None, None


def play_song(directory, selected_file):
    mixer.music.load(directory + '/' + selected_file)
    mixer.music.play()


def main(stdscr):
    parser = ArgumentParser(prog="Musicline", description="Play music in command line")
    parser.add_argument("folder", nargs='?')
    args = parser.parse_args()
    mixer.init()
    sp = " " * 60
    sp2 = "-" * 133
    sp3 = "|"
    stdscr.clear()
    curses.start_color()
    curses.use_default_colors()
    curses.init_pair(1, curses.COLOR_BLACK, curses.COLOR_WHITE)
    curses.init_pair(2, curses.COLOR_GREEN, curses.COLOR_BLACK)
    curses.init_pair(3, curses.COLOR_YELLOW, curses.COLOR_BLACK)
    files = os.listdir(args.folder)
    audio_files = [file for file in files if pattern.match(file)]
    cursor_pos = 0
    selected_index = -1
    header_lines = 2
    is_paused = False
    currently_playing = None
    metadata = ('', '', '')
    while True:
        stdscr.clear()
        stdscr.addstr(0, 0, sp + "MusicLine" + sp)
        stdscr.addstr(1, 0, sp2)
        max_y, max_x = stdscr.getmaxyx()
        column_pos = max_x // 2
        for i, audio_file in enumerate(audio_files):
            if i >= cursor_pos and i < cursor_pos + max_y - header_lines:
                if len(audio_file) > max_x:
                    audio_file = audio_file[:max_x-1]

                if selected_index == i:
                    if audio_file == currently_playing:
                        if is_paused:
                            stdscr.addstr(i - cursor_pos + header_lines, 0, audio_file, curses.color_pair(3))
                        else:
                            stdscr.addstr(i - cursor_pos + header_lines, 0, audio_file, curses.color_pair(2))
                    else:
                        stdscr.addstr(i - cursor_pos + header_lines, 0, audio_file, curses.color_pair(1))
                else:
                    stdscr.addstr(i - cursor_pos + header_lines, 0, audio_file)

        for j in range(header_lines, max_y):
            stdscr.addch(j, column_pos, '|')

        if selected_index != -1:
            stdscr.addstr(header_lines, column_pos + 1, f"{audio_files[selected_index]}")
            stdscr.addstr(header_lines + 1, column_pos + 1, f"{metadata[0]}")
            stdscr.addstr(header_lines + 2, column_pos + 1, f"{metadata[1]}")
            stdscr.addstr(header_lines + 3, column_pos + 1, f"{metadata[2]}")

        stdscr.refresh()
        key = stdscr.getch()

        if key == curses.KEY_DOWN:
            if cursor_pos < len(audio_files) - 1:
                cursor_pos += 1
                selected_index = cursor_pos
        elif key == curses.KEY_UP:
            if cursor_pos > 0:
                cursor_pos -= 1
                selected_index = cursor_pos
        elif key == curses.KEY_ENTER or key in [10, 13]:
            if selected_index != -1:
                selected_file = audio_files[selected_index]
                if currently_playing == selected_file:
                    if not is_paused:
                        mixer.music.pause()
                        is_paused = True
                    else:
                        mixer.music.unpause()
                        is_oaused = False
                else:
                    for j in range(header_lines, max_y):
                        stdscr.move(j, column_pos + 1)
                        stdscr.clrtoeol()

                    metadata = read_audio_metadata(selected_file, args.folder)
                    currently_playing = selected_file
                    is_paused = False
                    play_song(args.folder, selected_file)
        elif key == ord('q'):
            break

if __name__ == '__main__':
    curses.wrapper(main)
