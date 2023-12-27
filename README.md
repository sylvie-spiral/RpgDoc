Needs:
* pandoc
* pdfsizeopt (https://github.com/pts/pdfsizeopt)

For pandoc on Windows:
winget install JohnMacFarlane.Pandoc

For pandoc on Linux:
sudo apt-get install pandoc

Make a directory named doc in the same directory that make.sh / make.ps1 is in.

Download pdfsizeopt and put binaries in ./pdfsizeopt-linux or ./pdfsizeopt-win32.

Run ./make.sh on Linux or ./make.ps1 on Windows, and you get a directory named out with two PDF files - one is build from the Markdown files and the other is the optimized version.  Images can beb referenced from the markdown as normal, etc.  The purpose of this is to assemble PDF documents from a collection of Markdown files, to make collaborative editing easier.
