import os, shutil
from mutagen.mp3 import MP3
from mutagen.id3 import ID3, TIT2, TRCK, TPE1, TALB, TYER, TCON, COMM, APIC, TPOS
# filepath autocompletion
from prompt_toolkit import prompt
from prompt_toolkit.completion import PathCompleter

filetypes = [".mp3", ".flac", ".wav"]
pic_filetypes = [".png", ".jpg", ".jpeg"]

# The main metadata changer (pretty dang easy stuff), 1 at a time
def change_mp3_metadata(file_path, title, track_number, artist, album, year, genre, comment, pic_path, disk, disktotal):
    audio = MP3(file_path, ID3=ID3)

    ## if there ain't an ID3 tag, make one
    if not audio.tags:
        audio.add_tags()
        audio.save()

    tags = audio.tags

    tags.setall('TIT2', [TIT2(encoding=3, text=[str(title)])])
    tags.setall('TRCK', [TRCK(encoding=3, text=[str(track_number)])])
    tags.setall('TPE1', [TPE1(encoding=3, text=[str(artist)])])
    tags.setall('TALB', [TALB(encoding=3, text=[str(album)])])
    tags.setall('TYER', [TYER(encoding=3, text=[str(year)])])
    tags.setall('TCON', [TCON(encoding=3, text=[str(genre)])])

    ## metadata for disk total
    if int(disktotal) <= 1:
        disk_string = disktotal
    else:
        disk_string = f"{disk}/{disktotal}"
    tags.add(TPOS(encoding=3, text=disk_string))

    ## set optional comment
    if comment != "empty":
        tags.setall('COMM', [COMM(encoding=3, text=[str(comment)])])

    ## set optional album art
    if pic_path != "empty":
        ### if the chosen picture file is jpg or png, assign mime to corresponding
        if pic_path.lower().endswith(".jpg") or pic_path.lower().endswith(".jpeg"):
            mime = "image/jpeg"
        elif pic_path.lower().endswith(".png"):
            mime = "image/png"
        ### officially inject album art into mp3
        with open(pic_path, 'rb') as img:
            tags.add(
                APIC(
                    #### set encoding to UTF-8
                    encoding = 3,
                    mime = mime,
                    #### type of album art, 3 is front cover
                    type = 3,
                    desc = "Album Art",
                    data = img.read()
                )
            )
    audio.save()

def mp3_metadata_inator(dir_path, dir_list, artist, album, year, genre, yn_comment, all_comment):
    ## Ask if they want to inject album art in the file
    yn_picture = input("[?] Do you want to inject Album Art? If so, is it in this folder? (Y/n)\n[?] ")
    pic_file_list = []
    pic_path = "empty"
    if yn_picture.lower() == "y":
        for file in dir_list:
            if file.endswith(tuple(pic_filetypes)):
                pic_file_list.append(file)
        print("[?] Please pick from the list of picture files below:")
        [print(f"{pic_file_list.index(pic_file)} {pic_file}") for pic_file in pic_file_list]
        pic_choice = int(input("[?] "))
        pic_path = os.path.join(dir_path, pic_file_list[pic_choice])

    disktotal = input("[?] What's the total amount of disks?\n[?] ")
    if int(disktotal) > 1:
        yn_disknum = input("[?] Do you want to keep asking about the disk? If no, default is 1. (Y/n)\n[?] ")
    else:
        disk = 1

    ## Loop individually handling individual tracks with individual info
    comment = "empty"
    for file in dir_list:
        ### find mp3s, skip files that ain't mp3
        file_path = os.path.join(dir_path, file)
        if file[-4:].lower() != ".mp3":
            continue

        ### for file/song in question, ask title and number of song
        print(f"[*] {file}")
        title = input("[?] What is the title of the song?\n[?] ")
        track_number = input("[?] What is the track number of this song?\n[?] ")

        ### ask about comment, and if only one comment for all, change yn comment to prevent asking again
        if yn_comment.lower() == "y":
            comment = input("[?] What is the comment you want in the file(s)?\n[?] ")
            if all_comment.lower() == "y":
                yn_comment = "prevent looping"

        ### if there's more than 1 disk, keep asking what current disk of current song is
        if int(disktotal) > 1:
            if yn_disknum.lower() == "y":
                disk = input("[?] What's the current disk?\n[?] ")

        change_mp3_metadata(file_path, title, track_number, artist, album, year, genre, comment, pic_path, disk, disktotal)


# Function to allow user to interface with previous function optimally
def metadata_inquiry(dir_path, dir_list):

    artist = input("[?] Who is the artist?\n[?] ")
    album = input("[?] What is the name of this album?\n[?] ")
    year = input("[?] What is the year of the album?\n[?] ")
    genre = input("[?] What is the genre?\n[?] ")
    yn_comment = input("[?] Do you want to inject comments? (Y/n)\n[?] ")
    all_comment = "n"
    if yn_comment == "y":
        all_comment = input("[?] Do you want all files to have one comment? (Y/n)\n[?] ")

    mp3_metadata_inator(dir_path, dir_list, artist, album, year, genre, yn_comment, all_comment)

def main():

    program_dir = os.path.dirname(os.path.abspath(__file__))
    ## before dir path changes, open lyrics token in program root dir
    genius_path = os.path.join(program_dir, 'lyrics.token')
    with open(genius_path, 'r') as file:
        genius_token = file.readline().strip
    ## to allow filepath completion
    completion = PathCompleter()
    ## loop seeking desired music directory until satisfied
    while True:
        dir_path = prompt("[?] Please enter path to folder/directory below:\n", completer=completion)
        dir_list = sorted(os.listdir(dir_path))
        for file in dir_list:
            print(f"[*] {file}")
        confirmation = input("[?] Are you sure this is the right directory/folder? (Y/n)\n[?] ")
        if confirmation.lower() == "y":
            break

    ## ask desired filetype to edit
    print("[?] From list below, select number for your desired filetype:")
    [print(f"{filetypes.index(filetype)} {filetype}") for filetype in filetypes]
    filetype_num = int(input("[?] "))
    ## yes
    if filetype_num == 0:
       metadata_inquiry(dir_path, dir_list)


main()
