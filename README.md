# Phylogeny
### Visually compare multiple generations of a binary or text file

This script performs two functions:

1. Given a list of files, either binary or text, it sorts the files by similarity. This has the effect of (usually) arranging multiple generations or versions of the same file in chronological order. This is particularly helpful when other metadata isn't available, e.g date, version number, etc.

	This sorting method is based on concepts explained fairly well in this video, so I'll skip the explanation here:
	[Zip It! - Finding File Similarity Using Compression Utilities - Computerphile](https://youtu.be/aLaYgzmRPa8?si=3t9V86oC-DqTrFyT)

2. After finding the "best" order to place the list in, the script then generates an SVG and/or PNG graphic that shows the regions of the file that remain unchanged over each generation or version of the file. 

	This may be easier to understand by seeing an example.

### Example output
![14 releases of Patchomator.sh](https://github.com/option8/phylogeny/blob/main/examples/Patchomators.png?raw=true)

This sample image shows 14 release versions of another script I maintain, called [Patchomator](https://github.com/Mac-Nerd/patchomator/releases)

Vertical grey bars each represent an individual version of the file. Corresponding file names are in black vertical text.

Horizontal color bars connecting two file versions represent a region of the file that is common to both. Gaps appear where portions of the file differ from one version to the next. If a section of code, for example, has been moved from the end of the file to the beginning between versions, the colored bar representing that region of code would appear connecting the bottom of one bar to the top of the next.

[More examples](https://github.com/option8/phylogeny/tree/main/examples)

### Usage

`zsh fileThread.zsh [-t / -b] [-s] [-o Output_FileName] file-1 file-2 ... file-n`

 - `-t` Forces sorting and comparison in *text mode* for ASCII or UTF-8 files. 
 
 - `-b` Forces sorting and comparison in *binary mode*, default. 
 
 - `-s` Skips the sorting and re-ordering step, and threads the files in the order as given.
 
 - `-o Output_Filename` Generates "Output_Filename.svg" and "Output_Filename.png" otherwise defaults to "filethread.svg/png"

In *text mode*, any non-alphanumeric characters are removed, and everything that remains is converted to all upper case.

In *binary mode*, repeated null (x00) bytes are collapsed, so the contents of sparse binaries can be compared without concern for empty space.

### Requirements

Currently only tested on macOS Sequoia (15.x). Probably works on Tahoe, or any Mac with ZSH and Python 3.x.

Requires installing `pbzip2`. Install it with homebrew:
```brew install pbzip2```

If you're interested in playing with the compression/sorting scheme, it will work with `gzip`, `pkzip`, among others - but `pbzip` was most consistent in my testing.

### To Do
- Helptext and documentation
- Error checking
- Additional display/output options
- Options to skip "threading" (reorder-only) and output distance matric for actual phylogeny analysis.