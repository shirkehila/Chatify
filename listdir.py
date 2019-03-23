import os

def process_directory(direct, path):
    for p in os.listdir(path):
        abspath = os.path.join(path, p)
        isdir = os.path.isdir(abspath)
        if isdir:
            subdir = (p, [])
            process_directory(subdir[1], abspath)
        else:
            filename, file_extension = os.path.splitext(p)
            direct.append((filename,file_extension))



directory = []
my_path = r'C:\Users\Shir\Pictures\allGroups'
process_directory(directory,my_path)
print(directory)

filename, file_extension = os.path.splitext("classify.py")

print(file_extension)

