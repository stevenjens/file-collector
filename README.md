# File Collector

This script is useful for keeping track of subsets of a larger set of
files.

For example, I use it for pictures: I keep all of my digital pictures
in a common directory tree, but I sometimes want to share a subset of
them with family and maybe a different subset with friends who have a
particular interest in common with me.  I found myself keeping
separate directories of pictures for these different groups,
duplicating the files in my main archive.  But I don't need 12 copies
of a picture of my kids taking up space in my file system, so I
created this script to replace each special-purpose directory with a
single file that indicates what files are needed to recreate the
directory and where to find them.

As currently written, the script just stores the file as a
tab-delimited file with relative paths to the archived file and the
duplicate file.  If I decide to put more work into this project, I
will probably switch to a format like JSON and also store the roots of
the directory trees that are passed in when the archive is created so
they can be used as defaults when the archive is extracted (also, I
could handle file names with tabs).

## Usage

    usage: filecollector.py [-h] (-c | -e | -d) [-s SOURCEDIR] [-t TARGETDIR]
                            specfile
    
    Create an archive by finding duplicates of files or select a sample of files
    and copy them to a destination. Primary original purpose is to share some
    pictures from within an archive with other people, possibly with different
    names that might be more meaningful to them. If targetdir is a subdirectory of
    sourcedir, filecollector.py excludes targetdir and its subdirectories in its
    search for reference files.
    
    positional arguments:
      specfile
    
    optional arguments:
      -h, --help            show this help message and exit
      -c, --collect
      -e, --expand
      -d, --delete          delete the target files from the file system
      -s SOURCEDIR, --sourcedir SOURCEDIR
                            the directory under which to find the duplicate files
      -t TARGETDIR, --targetdir TARGETDIR
                            the directory under which to place new files or
                            collect files for archiving
