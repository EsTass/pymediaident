# pymediaident 0.6
python media (movies, series) ident, rename and show json data. beta Version.
![pymediaident](https://raw.githubusercontent.com/EsTass/pymediaident/master/img/example.gif)

## Description
Renamer for media files trying to identify searching on web (googler,ddgr,ducker), getting data from IMDBpy, python_filmaffinity, OMDB, TheTVDB.

## Installation

### Dependencies Auto
On first run try to install dependencies with pip (install before) and needed admin rights (sudo).

### Dependencies
 - googler: https://pypi.python.org/pypi/googler
 - ddgr: https://github.com/jarun/ddgr
 - ducker: https://pypi.python.org/pypi/ducker/2.0.1
 - IMDBpy: https://imdbpy.sourceforge.io/
 - python_filmaffinity: https://github.com/sergiormb/python_filmaffinity
 - omdb: https://pypi.python.org/pypi/omdb
 - tvdb_api: https://github.com/dbr/tvdb_api
 ### Dependencies Install
 ```
 pip install googler IMDBpy python_filmaffinity omdb tvdb_api
 ```
 
### Full Install on Arch

Install needed by pymediaident
```
pacman -S python python-pip 
yay/yaourt/pacaur -S ddgr ducker
pip install googler IMDBpy python_filmaffinity omdb tvdb_api
```
Then install pymediaident
```
wget https://raw.githubusercontent.com/EsTass/pymediaident/master/pymediaident.py
chmod +x pymediaident.py
cp ./pymediaident.py /usr/bin
```
Test all ok:
```
pymediaident.py -h
```

 ### Download
  - direct download file: https://raw.githubusercontent.com/EsTass/pymediaident/master/pymediaident.py
 
## Usage
```
pymediaident.py [options] [-f FILE|-fp PATH|-fs Searchtext]
```

### OPTIONS
```
 -h : help
 -v : verbose mode
 -f FILETOIDENT : path to file to ident
 -fp FOLDER : path to folder to scan media files and ident
 -fps 50 : min file size to folder scan to use as media file
 -fpee ext1,ext2 : scan folder exclude extensions ('part','part.met','!qb','tmp','temp')
 -es 'googler|ddgr|ducker' : external search
 -s imdb|filmaffinity|omdb|thetvdb : get data from
 -sid XXX : forced id for imdb|filmaffinity|omdb|thetvdb
 -apikey XXX : apikey for omdb|thetvdb
 -l en|es|mx|ar|cl|co... : languaje
 -c USA : country for release date
 -r : rename
 -rfm "%title% (%year%, %director%)" : rename format movie
 -rfs "%title% %season%x%chapter%(%year%, %director%)" : rename format series
 -m "/path/%title%": move file to folder with format name 
 -hl "/path/%title%": hardlink file to folder with format name 
 --json : return onlyjson data
 -dr : dryrun, force not changes
 -i : interactive mode, select search result to assign
 -if X: force select X position of interactive mode
 -fs "Search String" : force search string for file
 -bwf badwordsfile.txt : bad words for clean filenames (1 word each line)
 ```
 
### Formats for file/folders (-rfm -rfs -m -hl)
```
 %title%
 %year%
 %director%
 %season%
 %chapter%
 %chaptertitle%
 %genre%
 ```
 
 ### Examples
 
 Search for files in ./Media with filesize >100Mb with imdb and rename with default formats:
 ```
 pymediaident.py -fp "./Media" -fps 100 -s imdb -r
 ```
 
 Search for title 'The matrix' imdb and rename file to format "%title% (%year%, %director%)":
 ```
 pymediaident.py -f "./Th3 mAtr12.mp4" -fs "The matrix" -s imdb -r -rfm "%title% (%year%, %director%)"
 ```
 
 Search for title 'The matrix' imdb and rename file to format "%title% (%year%, %director%)" only preview:
 ```
 pymediaident.py -f "./Th3 mXtr12.mp4" -fs "The matrix" -s imdb -r -rfm "%title% (%year%, %director%)" -dr
 ```
 
 Ident file './The matrix.mp4' imdb and rename to format "%title% (%year%, %director%)":
 ```
 pymediaident.py -f "./The matrix.mp4" -s imdb -r -rfm "%title% (%year%, %director%)"
 ```
 
 Ident file './Th3 mAtr12.mp4' forcing search "the matrix" imdb and rename to format "%title% (%year%, %director%)":
 ```
 pymediaident.py -fs "the matrix" -f "./Th3 mAtr12.mp4" -s imdb -r -rfm "%title% (%year%, %director%)"
 ```
 
 Ident file './The matrix.mp4' duckduckgo/filmaffinity and rename to format "%title% (%year%, %director%)" in interactive mode:
 ```
 pymediaident.py -f "./The matrix.mp4" -s filmaffinity -r -rfm "%title% (%year%, %director%)" -i -es ddgr
 ```
 
 Ident file './The matrix.mp4' duckduckgo/imdb and rename to format "%title% (%year%, %director%)" in interactive mode and autoselect option 2 of interactive list:
 ```
 pymediaident.py -f "./The matrix.mp4" -s imdb -r -rfm "%title% (%year%, %director%)" -i -if 2 -es ddgr
 ```
 
 Ident file './The matrix.mp4' imdb, rename to format "%title% (%year%, %director%)" and move to folder "./%title%":
 ```
 pymediaident.py -f "./The matrix.mp4" -s imdb -r -rfm "%title% (%year%, %director%)" -m "./%title%"
 ```
 
 Ident file './The matrix.mp4' duckduckgo/filmaffinity, rename to format "%title% (%year%, %director%)" and show only json data:
 ```
 pymediaident.py -f "./The matrix.mp4" -s filmaffinity -r -rfm "%title% (%year%, %director%)" -es ddgr --json
 ```
 
 Ident file './The matrix.mp4' duckduckgo/omdb and rename to format "%title% (%year%, %director%)" in interactive mode:
 ```
 pymediaident.py -f "./The matrix.mp4" -s omdb -apikey XXXXXX -r -rfm "%title% (%year%, %director%)" -es ddgr -i
 ```
 
