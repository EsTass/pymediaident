# pymediaident 0.1
python media (movies, series) ident and renamer alpha
![pymediaident](https://raw.githubusercontent.com/EsTass/pymediaident/master/img/example.gif)

## Description
Renamer for media files trying to identify searching on web (googler,ddgr,ducker), getting data from IMDBpy, python_filmaffinity or OMDB.

## Installation
### Dependencies
 - googler: https://pypi.python.org/pypi/googler
 - ddgr: https://github.com/jarun/ddgr
 - ducker: https://pypi.python.org/pypi/ducker/2.0.1
 - IMDBpy: https://imdbpy.sourceforge.io/
 - python_filmaffinity: https://github.com/sergiormb/python_filmaffinity
 - omdb: https://pypi.python.org/pypi/omdb
 - tvdb_api: https://github.com/dbr/tvdb_api
 
 ### Download
  - direct download file: https://raw.githubusercontent.com/EsTass/pymediaident/master/pymediaident.py
 
## Usage
```
pymediaident.py [options] [-f FILE|-fs Searchtext]
```

### OPTIONS
```
 -h : help
 -f FILETOIDENT : path to file to ident
 -es 'googler|ddgr|ducker' : external search
 -s imdb|filmaffinity|omdb|thetvdb : get data from
 -sid XXX : forced id for imdb|filmaffinity|omdb|thetvdb
 -apikey XXX : apikey for omdb|thetvdb
 -l en|es|mx|ar|cl|co... : languaje
 -c USA : country for release date
 -r : rename
 -rfm "%title% (%year%, %director%)" : rename format movie
 -rfs "%title% %season%x%chapter%(%year%, %director%)" : rename format eries
 -m "/path/%title%": move file to folder with format name 
 -hl "/path/%title%": hardlink file to folder with format name 
 --json : return only json data
 -dr : dryrun, force not changes
 -i : interactive mode, select search result to assign
 -if X: force select X position of interactive mode
 -fs "Search String" : force search string for file
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
 
