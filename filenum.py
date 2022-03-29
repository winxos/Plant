# -- coding: utf-8 --
import datetime
import os
save_path = "/home/pi/Desktop/data/"


def get_filter_files(dir, ext=None):
    allfiles = []
    needExtFilter = (ext != None)
    for root, dirs, files in os.walk(dir):
        for filepath in files:
            # filepath = os.path.join(root, filespath)
            extension = os.path.splitext(filepath)[1][1:]
            if needExtFilter and extension in ext:
                allfiles.append(filepath)
            elif not needExtFilter:
                allfiles.append(filepath)
    return allfiles


def get_cur_num():
    q = get_filter_files(save_path, 'txt')
    if len(q) == 0:
        return 0
    q.sort(reverse=True)
    id = 0
    while id<len(q) and len(q[id].split('.')[0])!=12:
        id+=1
    f = q[id].split('.')[0]
    today = "%s" % (datetime.datetime.now().strftime('%Y%m%d'))
    id = 0
    if f[:-4] == today:
        id = int(f.split('.')[0][-4:]) + 1
    return id


if __name__ == "__main__":
    print("filenum test")
    print("current num is %d" % get_cur_num())
