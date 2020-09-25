import sys
import subprocess
import os
import glob

def checkExtension(fileName):
    filename, file_extension = os.path.splitext(fileName)
    if file_extension == ".srt":
        return False
    if file_extension == ".nfo":
        return False
    if file_extension == ".exe":
        return False
    if file_extension == ".txt":
        return False
    if file_extension == ".zip":
        return False
    if file_extension == ".parts":
        return False
    if file_extension == ".png":
        return False
    return True

#Check if audio stream needs convert
def needsConvert(ffmpegDir, dirPath, inputFileName):
    if checkExtension(inputFileName) == False:
        return False

    cmd = f'ffprobe -v error -select_streams a:0 -show_entries stream=codec_name -of default=noprint_wrappers=1:nokey=1 "{inputFileName}"'
    probeProcess = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, stdin=subprocess.PIPE)
    out, err = probeProcess.communicate()
    result = out.decode(sys.stdout.encoding).strip()
    error = err.decode(sys.stdout.encoding).strip()

    if "eac3" in result:
        return True
    if "ac3" in result:
        return True
    #if "aac" in result:
    #   print("Already converted.")
    #elif error:
    #   print("Failed.")

    return False

#Convert audio stream
def convert(ffmpegDir, inputFileName):
    filename, file_extension = os.path.splitext(inputFileName)
    outputName = f'{filename}_convert{file_extension}'
    print("\nProcessing: " + inputFileName)
    if os.path.exists(outputName):
        print("File already exists.")
        return
    print(f'Converting {filename}...')

    convertCmd = f'ffmpeg -i "{inputFileName}" -loglevel warning -hide_banner -nostats -vcodec copy -acodec aac -ac 2 -af \"pan=stereo|FL=FC+0.30*FL+0.30*BL|FR=FC+0.30*FR+0.30*BR\" "{outputName}"'
    process = subprocess.call(convertCmd, shell=True)
    print("Finished.")

def processDirectory(dir):
    for (dirPath, dirnames, fileNames) in os.walk(dir):
        print("---------------------------\nEntering directory: " + dirPath)
        #needsConvertMultiple(ffmpegDir, dirPath, fileNames)
        total = len(fileNames)
        if total > 0:
            count = 0
            skipped = 0
            for file in fileNames:
                count += 1
                filePath = os.path.join(dirPath, file)
                isConvertNeeded = needsConvert(ffmpegDir, dirPath, filePath)
                if isConvertNeeded:
                    convert(ffmpegDir, filePath)
                else:
                    skipped += 1
                sys.stdout.write(f'\rProcessed: {count} / {total}, skipped {skipped} files')
            print("")
        else:
            print("No files found.")
        for childDir in dirnames:
            processDirectory(childDir)

ffmpegDir = "/Users/sblac/Downloads/ffmpeg-2020-09-20-git-ef29e5bf42-full_build (2)/ffmpeg-2020-09-20-git-ef29e5bf42-full_build/bin"
print("Enter initial directory path...")
dir = input()
while not os.path.exists(dir):
    print(f"Failed to find '{dir}', please enter a new directory...\n")
    dir = input()

processDirectory(dir)
print("Finished.")
print("--------------------------------------------------")

