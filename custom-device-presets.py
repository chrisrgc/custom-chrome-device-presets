#!/usr/bin/env python
import sys
import re
import os

breakpointOptions = [
    {"name": "default", "sizes": [
        {"size": 320, "title": "Mobile S"},
        {"size": 375, "title": "Mobile M"},
        {"size": 425, "title": "Mobile L"},
        {"size": 768, "title": "Tablet"},
        {"size": 1024, "title": "Laptop"},
        {"size": 1440, "title": "Laptop L"},
        {"size": 2560, "title": "4K"}]},
    {"name": "tailwind", "sizes": [
        {"size": 320, "title": "Tailwind xs"},
        {"size": 640, "title": "Tailwind sm"},
        {"size": 768, "title": "Tailwind md"},
        {"size": 1024, "title": "Tailwind lg"},
        {"size": 1280, "title": "Tailwind xl"},
        {"size": 1536, "title": "Tailwind 2xl"},
        {"size": 2560, "title": "4K"}]},
    {"name": "bootstrap4", "sizes": [
        {"size": 320, "title": "BS4 xs"},
        {"size": 576, "title": "BS4 sm"},
        {"size": 768, "title": "BS4 md"},
        {"size": 992, "title": "BS4 lg"},
        {"size": 1200, "title": "BS4 xl"},
        {"size": 2560, "title": "4K"}]}
    ]


def find_presets_start(data):
    match = re.search("(_populatePresetsContainer\(\)\s*\{)", data)
    if match:
        location = data.find(match.group())
        if location > -1:
            return location

    raise Exception("_populatePresetsContainer not found.")


def find_sizes_length(data):
    match = re.search("\s+sizes\s*=\s*\[(.*?)\]\s*;", data)
    if match:
        return match.end() - match.start()

    raise Exception("Sizes collection not found.")


def generate_sizes(breakpoints):
    sizes = []

    for breakpoint in breakpoints:
        sizes.append(str(breakpoint["size"]))

    return ",".join(sizes)


def replace_sizes(data, start, end, breakpoints):
    slice = data[start:end]

    originalLen = find_sizes_length(slice)
    sizes = generate_sizes(breakpoints)
    newSizes = " sizes=[%s];" % sizes
    newSizes = newSizes + (" " * (originalLen - len(newSizes)))

    replacement = re.sub("\s+sizes\s*=\s*\[(.*?)\]\s*;", newSizes, slice)
    data = data[:start] + replacement + data[end:]
    return data


def generate_titles(breakpoints):
    titles = []
    breakpoints.sort(key=lambda x: x["size"])
    for breakpoint in breakpoints:
        titles.append("Common.UIString('%s')" % breakpoint["title"])

    return ",".join(titles)


def replace_titles(data, start, end, breakpoints):
    slice = data[start:end]

    originalLen = find_titles_length(slice)
    titles = generate_titles(breakpoints)
    newTitles = " titles=[%s];" % titles
    newTitles = newTitles + (" " * (originalLen - len(newTitles)))
    replacement = re.sub("\s+titles\s*=\s*\[(.*?)\]\s*;", newTitles, slice)
    data = data[:start] + replacement + data[end:]
    return data


def find_titles_length(data):
    match = re.search("\s+titles\s*=\s*\[(.*?)\]\s*;", data)
    if match:
        return match.end() - match.start()

    raise Exception("Titles collection not found.")


def usage():
    print "Usage: chrome-device-presets.py resources-file preset-selection"

    print "\nOptions:\n   preset-selection"
    print "\tdefault\t\tChrome defaults"
    print "\ttailwind\tBreakpoints for Tailwind CSS"
    print "\tbootstrap4\tBreakpoints for Bootstrap 4"

    print "\nExample:\n   chrome-device-presets.py " + os.sep.join([".", "resources.pak"]) + " tailwind"

    exit(1)


def select_breakpoints(presetName):
    breakpoints = [x["sizes"] 
        for x in breakpointOptions
            if x["name"] == presetName]

    if len(breakpoints) != 1:
        usage()

    breakpoints = breakpoints[0]

    breakpoints.sort(key=lambda x: x["size"])

    return breakpoints


def extract_args():
    if len(sys.argv) != 3:
        usage()

    return (sys.argv[1], sys.argv[2])


def main():
    (inputFile, presetName) = extract_args()

    breakpoints = select_breakpoints(presetName)

    resourceDataPack = open(inputFile, "rb")

    resourceData = resourceDataPack.read()

    start = find_presets_start(resourceData)
    end = start + 1000

    originalLen = len(resourceData)

    resourceData = replace_sizes(resourceData, start, end, breakpoints)
    resourceData = replace_titles(resourceData, start, end, breakpoints)

    newLen = len(resourceData)

    if newLen != originalLen:
        raise Exception("New file length not equal to the original resource data pack.")

    out = open("resources.pak", "wb+")
    out.write(resourceData)
    out.close()


if __name__ == '__main__':
    main()
