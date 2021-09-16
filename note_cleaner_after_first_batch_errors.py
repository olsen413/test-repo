import re
import os

def get_dangling_first(str_in):
    '''
    The first line of the note will be at the end of the first line of input.
    This function moves from the end of that line until it encounters a junk
    character.
    Outputs the first line of the note as a string
    '''
    str_out = ''
    for char in reversed(str_in):
        if (char.isalpha() or char in ' ",.\n\'()'):
            str_out = char + str_out
        else:
            return str_out.strip()
    return str_out.strip()


def get_title_plus(str_in):
    '''
    The title will be embedded in a long string of junk characters, but will be
    bookended by "B>" and "4A4A".
    If there is no "4A4A" the note had no title, insted the first line will be
    used. However, this makes the get_dangling_first function redundant and
    irrelevant. This function returns a flag that determines if that function is
    necessary
    This function splits the line at each break point and slices junk character.
    Outputs the title as string, flag as boolean within a list.
    '''
    str_out = ''
    to_dangle = False
    try:
        tmp = str_in.split('B>')[1]
        if '4A4A' in tmp:
            tmp = tmp.split('4A4A')[0]
            to_dangle = True
        tmp = tmp[1::].strip()
    except IndexError:
        # Indicates regular title process didn't work
        # instead sets up process to get dangle alone
        tmp = None
        to_dangle = True
    return [tmp, to_dangle]

'''
The try - except block checks that the shell script below has cleaned the .note
formatted files:
    for d in TestScript/*/;
    do (cd "$d" && iconv -c -f utf-8 -t latin1 < note.note |
    tr -cd '\11\12\40-\176' > noteConv.txt);
    done
The recursive folder call should be updated to call this script (lyric_cleaner)
and track_namer - track namer will rely on returned title from lyric_cleaner
'''
try:

    fp_in = open('noteConv.txt', 'r')
    lines = fp_in.readlines()
    fp_in.close()

    print('Lines read in from noteConv.txt:\n', lines)

    '''
    When a note has no title, the first line will appear after "B>" and get_title_plus
    will catch it and make it the title, even though there is no "4A4A".
    However, a redundant first line is generated...Does it matter? Yes, because only
    get_title_plus handles the extra character.
    So the absence of "4A4A" should prevent get_dangling_first from running...
    '''
    title_plus = get_title_plus(lines[0]) # returns list with title and dangle flag
    title = title_plus[0] # get title alone
    to_dangle = title_plus[1] # get dangle flag
    body_index = 1

    # if title == None:
    #     # try putting the B> full file search here too
    #     title = get_dangling_first(lines[0])
    #     print('title_plus returned None\nUsing dangle for title: ')
    #     print(title)
    #     while title == None or len(title) < 2:
    #         # title = lines[body_index]
    #         title = get_dangling_first(lines[body_index])
    #         try:
    #             title = title.strip()
    #         except AttributeError:
    #             pass
    #         print('Title too short. Using next line as title: ')
    #         print(title)
    #         body_index += 1
    #
    #     to_dangle = False
        # check if dangle can be used for title
        # if that doesn't work, check line by line until a suitable alnum is
        # usable -- >  see /home/wo/Notes/dri…otes_210115_000658
        # this will require implementing a way to do the for loop starting from
        # a variable index

    while title == None or len(title) < 2:
        if body_index > len(lines):
            title = 'untitled'
        else:
            title = get_dangling_first(lines[body_index-1])
            body_index += 1
            try:
                title = title.strip()
            except AttributeError:
                pass
            print('Title too short. Using next line as title: ')
            print(title)
        to_dangle = False

    file_title = title.replace(' ', '_')
    file_title = title.replace('/', '-')
    fp_out = open(file_title+'.txt', 'w')

    fp_out.write(title + '\n')

    if to_dangle:
        dangle = get_dangling_first(lines[0])
        fp_out.write(dangle + '\n')


    cont = True
    for line_idx, str in enumerate(lines[body_index:]):
        if str == '\t\n':
            # stops loop when encountering junk lines after final text line
            cont = False
        if cont:
            # Is it the last text line? check
            # PAPAPAPA won't be in untitled notes - so check with the re.search
            # some notes WON'T have PA..PA, only PA..
            # if 'PAPAPAPA' in str:
            if re.search('PA..', str) != None:
                str_break_idx = re.search('PA..', str).start()
                str = str[:str_break_idx]
            fp_out.write(str)

    fp_out.close()
    print('Note Converted. Currently in '+os.getcwd())
except FileNotFoundError:
    print('Note has not been converted. Currently in')



path = os.getcwd()
sub_path = (path+'/media')
for file in os.listdir(sub_path):
    print(file)
    if file.endswith('mp4'):
        file_str = (sub_path+'/'+file)
        new_str = (path+'/'+file_title+'.mp4')
        print()
        os.rename(file_str, new_str)
    else:
        os.remove(sub_path+'/'+file)
os.rmdir(sub_path)

for file in os.listdir(path):
    if file.startswith(file_title):
        print(file)
        os.rename(path+'/'+file, '/home/wo/Notes/'+file)
