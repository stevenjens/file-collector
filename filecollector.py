# python Pictures/refar.py --collect "Pictures/ToShare/2017 Christmas Concert.txt" -s Pictures -t "C:\Users\steve\Desktop\Photos to share\2017 Christmas Concert"

# Not the most robust thing -- in particular, don't put tabs in your filenames


import argparse, os, sys
import os.path as op
from shutil import copy2

# os.remove deletes a file
from os import makedirs, remove
from os.path import normpath



def getFileSizeMap(dirname, exclude = None):
    dirname = normpath(dirname)
    if exclude is not None:
        exclude = normpath(exclude)
    
    filesizemap = {}
    for root, dirs, files in os.walk(dirname):
        for name in files:
            absolute_path = op.join(root, name)
            if exclude is None or not absolute_path.startswith(exclude):
                the_size = op.getsize(absolute_path)
                if the_size in filesizemap:
                    filesizemap[the_size].append(absolute_path)
                else:
                    filesizemap[the_size] = [absolute_path]
    return filesizemap



def filesAreIdentical(file1, file2):
    with open(file1, "rb") as fd1:
        with open(file2, "rb") as fd2:
            buf1 = fd1.read(65536)
            buf2 = fd2.read(65536)
            if buf1 != buf2:
                return False
            else:
                while len(buf1) > 0 and len(buf2) > 0:
                    buf1 = fd1.read(65536)
                    buf2 = fd2.read(65536)
                    if buf1 != buf2:
                        return False
                return True




class Spec:
    # self._data is a list of tuples -- source/destination pairs
    def __init__(self, data = []):
        self._data = data

    def __str__(self):
        return "\n".join([x+"\t"+y for (x, y) in self._data])
    def __len__(self):
        return len(self._data)
    def __getitem__(self, idx):
        return self._data[idx]


    def collect(sourcedir, targetdir):
        # TK: sourcedir = "." with targetdir underneath, it isn't excluding targetdir from sources -- should make path absolute
        myspec_tuples = []
        # first, collect file sizes of files in target directory
        targetSizeMap = getFileSizeMap(targetdir)
        # then, search for files of those sizes in source directory (hashmap of lists) --
        #   exclude anything in the target directory, if it's a subdirectory
        sourceSizeMap = getFileSizeMap(sourcedir, exclude = targetdir)
        # either compare file contents directly or use hashing function -- will we need to compare a lot, or do we scan a file at most once anyway?
        for this_size, target_files in targetSizeMap.items():
            if this_size in sourceSizeMap:
                possible_sources = sourceSizeMap[this_size]
                for target_file in target_files:
                    for source_file in possible_sources:
                        if filesAreIdentical(target_file, source_file):
                            if "\t" in target_file:
                                print(target_file + " contains a tab character -- skipping")
                                break
                            elif not target_file.startswith(targetdir + os.sep):
                                print(target_file + " should start with " + targetdir + os.sep)
                                break
                            elif "\t" in source_file:
                                print(source_file + " contains a tab character -- skipping")
                                break
                            elif not source_file.startswith(sourcedir + os.sep):
                                print(source_file + " should start with " + sourcedir + os.sep)
                            else:
                                myspec_tuples.append((source_file[len(sourcedir + os.sep):],
                                                      target_file[len(targetdir + os.sep):]))
                                break
        myspec_tuples.sort()
        return Spec(myspec_tuples)

    def fromFile(filename):
        return_spec = Spec()
        with open(filename) as f:
            for line in f:
                source, target = line.split('\t')
                return_spec._data.append((source, target.strip()))
        return return_spec


    def toFile(self, filename):
        with open(filename, "w") as out:
            out.write(str(self))
            out.write("\n")

    def expand(self, sourcedir, targetdir):
        # TK I assume if a source file isn't found, this crashes
        # TK if source file isn't found, should we go searching?
        for source, dest in self._data:
            sourcefile = op.join(sourcedir, source)
            destfile = op.join(targetdir, dest)
            if not op.exists(sourcefile):
                print("Can't find " + sourcefile)
            else:
                if not op.exists(op.dirname(destfile)):
                    makedirs(op.dirname(destfile))
                copy2(sourcefile, destfile)
            






if __name__ == "__main__":
    parser = argparse.ArgumentParser(description = """Create an archive by finding duplicates of files or select
a sample of files and copy them to a destination.
Primary original purpose is to share some pictures from
within an archive with other people, possibly with different
names that might be more meaningful to them.

If targetdir is a subdirectory of sourcedir, %(prog)s excludes
targetdir and its subdirectories in its search for reference files.
""")

    # TK I would prefer to allow both -c and -d, which would execute in that order
    parser_action_group = parser.add_mutually_exclusive_group(required = True)
    parser_action_group.add_argument("-c", "--collect", action="store_true")
    parser_action_group.add_argument("-e", "--expand", action="store_true")
    parser_action_group.add_argument("-d", "--delete", action="store_true", help = "delete the target files from the file system")
    
    parser.add_argument("specfile")
    parser.add_argument("-s", "--sourcedir",
                        default = normpath(os.getenv("DATA_HOME", "C:/Users/steve/Documents")),
                        help = "the directory under which to find the duplicate files")
    parser.add_argument("-t", "--targetdir", help = "the directory under which to place new files or collect files for archiving")
    
    
    args = parser.parse_args()
    
    args.sourcedir = normpath(args.sourcedir)
    
    # TK can I tell argparse that the default targetdir is op.join(sourcedir, "Tmp") ?
    if args.targetdir is None:
        args.targetdir = op.join(args.sourcedir, "Tmp")
    
    args.targetdir = normpath(args.targetdir)
    
    
    print(str(args))
    
    
    
    SOURCE_ROOT_DIR = normpath(args.sourcedir)
    TARGET_ROOT_DIR = normpath(args.targetdir)
    
    
    
    if args.expand:
        print("Expanding " + args.specfile + " using source " + args.sourcedir + " and target " + args.targetdir)
        myspec = Spec.fromFile(args.specfile)
        myspec.expand(args.sourcedir, args.targetdir)
    
    if args.collect:
        print("Collecting")
        if op.exists(args.specfile):
            print(args.specfile + " already exists -- will not overwrite")
        else:
            myspec = Spec.collect(args.sourcedir, args.targetdir)
            myspec.toFile(args.specfile)
    
    if args.delete:
        print("Deleting " + args.specfile + " using target " + args.targetdir)
        myspec = Spec.fromFile(args.specfile)
        for source, target in myspec:
            file_to_remove = op.join(args.targetdir, target)
            # TK should check for existence
            os.remove(file_to_remove)
