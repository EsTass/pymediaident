#!/bin/python
#!/usr/bin/env python3
# -*- coding: utf-8 -*-

'''
Documentation, License etc.

EsTass 2018 
https://github.com/EsTass/pymediaident

@package pymediaident
'''

#IMPORTS
import sys
import os
import unicodedata
import ntpath
import re
import datetime
import array
import subprocess
import json
import datetime
#IMDBpy IMDB https://imdbpy.sourceforge.io/
from imdb import IMDb
#python_filmaffinity https://github.com/sergiormb/python_filmaffinity
import python_filmaffinity
#omdb https://pypi.python.org/pypi/omdb
import omdb
#tvdb_api https://github.com/dbr/tvdb_api/
import tvdb_api

#CONFIGS
VERSION='0.3'
#remove extension from filename
remove_extension = [ '.avi', '.mp4', '.mpeg', '.mkv', '.mpeg4', '.ogm' ]
#min filesize for media file (50mb)
G_MEDIAMINSIZE = 50 * 1024 * 1024
# web data from. imdb|filmaffinity
G_GETDATAFROM_LIST=[ 'imdb', 'filmaffinity', 'omdb', 'thetvdb', 'test' ]
G_GETDATAFROM='imdb'
G_GETDATAFROM_KEY=''
# forced id for imdb|filmaffinity data
G_GETDATAFROM_ID=''
# inet searcher
#ddgr ducker googler
CMDSEARCHLIST = [ 'googler', 'ddgr', 'ducker' ]
CMDSEARCH = ''
#lang
G_LANG='en'
#country
G_COUNTRY='USA'
G_COUNTRY_DEF='USA'
#Max actors
ACTORS_MAX=20
#Rename
G_RENAME=False
#FORMATS
#%title%
#%year%
#%director%
#%season%
#%chapter%
#%chaptertitle%
#%genre%
#Rename Format MOVIE
G_RENAME_FORMAT_MOVIE='%title% (%year%, %director%)'
#Rename Format SERIE
G_RENAME_FORMAT_SERIE='%title% %season%x%chapter%(%year%, %director%)'
#Move
G_MOVE=False
#harlink
G_HARDLINK=False
#JSon Format
G_JSON=False
#Not print info
G_NOINFO=False
#dryrun
G_DRYRUN=False
#interactive mode
G_INTERACTIVE=False
#interactive mode set result
G_INTERACTIVE_SET=False
#Force search string
G_FSEARCHSTRING=False
#barwords txt file
G_BADWORDSFILE=False

#OPTIONS
MSG_OPTIONS = '''
OPTIONS
 -h : help
 -f FILETOIDENT : path to file to ident
 -fp FOLDER : path to folder to scan media files and ident
 -fps 50 : min file size to folder scan to use as media file
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
 
Formats for -rfm -rfs -m -hl
 %title%
 %year%
 %director%
 %season%
 %chapter%
 %chaptertitle%
 %genre%
 
'''
MSG_APPINFO='pymediaident v'+VERSION+' 2018 https://github.com/EsTass/pymediaident'

G_BADWORDS=[ \
        'torrent', \
        'xvid', \
        'divx', \
        'mp4', \
        'acc', \
        'mp3', \
        'x264', \
        'x265', \
        'microhd', \
        'micro-hd', \
        'tsscreener', \
        'tvscreener', \
        'hdscreener', \
        'ts-screener', \
        'tv-screener', \
        'hd-screener', \
        'screener', \
        'dvdline', \
        'dvd-line', \
        'dvdrip', \
        'dvd-rip', \
        'dvd', \
        'dvbrip', \
        'dvb-rip', \
        'dvbline', \
        'dvb-line', \
        'dvb', \
        'fullbluray', \
        'bluray', \
        'blray', \
        'bd-rip', \
        'bdline', \
        'bd-line', \
        'bdrip', \
        'bdremux', \
        'vp8', \
        'vp9', \
        '1080p', \
        '720p', \
        '2ch', \
        '5ch', \
        '7ch', \
        '8ch', \
        '4K ', \
        '3d ', \
    ]

#FUNCTIONS

def getFilesMedia(path):
    global G_MEDIAMINSIZE
    result = []

    printE('Get Files in folder:', path)
    path = u''
    path = os.path.abspath(path)
    
    if os.path.exists( path ):
        for folder, subfolders, files in os.walk(path):
            for file in files:
                filePath = os.path.join(folder, file)
                try:
                    if G_MEDIAMINSIZE<=os.path.getsize(filePath) \
                    and os.path.basename(__file__) != file:
                        result.append(filePath)
                except:
                    pass
    printE('Files finded:', len(result))
    
    return result

def getBadWordsFile(file):
    global G_BADWORDS
    result=False
    num=0
    debug=False
    
    if os.path.isfile(file):
        printE('Loading BadWordsFile:', file)
        try:
            with open(file, 'r') as f:
                data = f.read().splitlines()
                if data:
                    for word in data:
                        if debug: printE('BadWord+:',word)
                        G_BADWORDS.append(word)
                        num+=1
            printE('BadWords Loaded:',str(num))
        except:
            pass
    
    if debug: exit()
    return result

def cleanFileName(file):
    global G_BADWORDS
    FILENAMECLEAN=file
    debug=False
    
    #EXTRACT YEAR
    #YEAR=re.search(r"\d{4}", FILENAME).group(1)
    YEARS=re.findall('(\d{4})', FILENAME)
    YEAR=''
    for y in YEARS:
        if int(y) > 1900 and int(y) < (datetime.date.today().year + 2):
            if debug: printE( 'YEAR: ', y )
            YEAR=y
            break

    #EXTRACT CHAPTER
    CHAPTER=False
    SEASON=False
    CSREMOVE=False
    SEASON, CHAPTER, CSREMOVE = extractChapter( FILENAME )
    if SEASON != False:
        if debug: printE( 'Season: ', SEASON )
        if debug: printE( 'Chapter: ', CHAPTER )
        if debug: printE( 'Detected: ', CSREMOVE )
    else:
        if debug: printE( 'No Series data (sxc): ', FILENAME )

    #CLEAN FILENAME

    FILENAMECLEAN=FILENAME
    
    #SxC cut string
    if CSREMOVE != False:
        ft=FILENAMECLEAN.split(CSREMOVE)
        if ft and len(ft[0]) > 5:
            FILENAMECLEAN=ft[0]
            if debug: printE( 'File Cut SEASONxCHPATER: ', FILENAMECLEAN )
    
    #REMOVE SEASONxCHAPTER
    if CSREMOVE != False:
        FILENAMECLEAN=FILENAMECLEAN.replace(CSREMOVE,'')
        if debug: printE( 'File Clean SEASONxCHPATER: ', FILENAMECLEAN )
    
    #REMOVE YEAR
    FILENAMECLEAN=FILENAMECLEAN.replace(YEAR,'')
    if debug: printE( 'File Clean YEAR: ', FILENAMECLEAN )

    #()
    FILENAMECLEAN=re.sub('\(.*?\)', '', FILENAMECLEAN)
    if debug: printE( 'File Clean (): ', FILENAMECLEAN )

    #[]
    FILENAMECLEAN=re.sub('\[.*?\]', '', FILENAMECLEAN)
    if debug: printE( 'File Clean []: ', FILENAMECLEAN )

    #domains A
    filter=r'(http:\/\/www\.|https:\/\/www\.|http:\/\/|https:\/\/)?[a-z0-9]+([\-\.]{1}[a-z0-9]+)*\.[a-z]{2,5}(:[0-9]{1,5})?(\/.*)?$'
    f=re.sub(filter, '', FILENAMECLEAN, re.IGNORECASE)
    if len(f) > 5:
        FILENAMECLEAN=f
    if debug: printE( 'File Clean Domains A: ', FILENAMECLEAN )
    
    #domains B
    filter=r'[a-zA-Z0-9]+\.(com|net|org)'
    f=re.sub(filter, '', FILENAMECLEAN, re.IGNORECASE)
    if len(f) > 5:
        FILENAMECLEAN=f
    if debug: printE( 'File Clean Domains B: ', FILENAMECLEAN )
    
    #remove extensions
    for rext in remove_extension:
        FILENAMECLEAN=FILENAMECLEAN.replace(rext, ' ')
    if debug: printE( 'File Clean extensions: ', FILENAMECLEAN )

    #remove bad words
    for bd in G_BADWORDS:
        pattern = re.compile(bd, re.IGNORECASE)
        FILENAMECLEAN=pattern.sub(bd,FILENAMECLEAN)
    if debug: printE( 'File Clean bad words: ', FILENAMECLEAN )

    #remove all non alfanumeric chars
    FILENAMECLEAN=re.sub(r'[^a-zA-Z0-9]', ' ',FILENAMECLEAN)
    if debug: printE( 'File Clean All except chars: ', FILENAMECLEAN )

    #extra .
    FILENAMECLEAN=re.sub('\.+','.',FILENAMECLEAN)
    if debug: printE( 'File Clean .: ', FILENAMECLEAN )

    #extra spaces
    FILENAMECLEAN=re.sub(' +',' ',FILENAMECLEAN)
    if debug: printE( 'File Clean spaces: ', FILENAMECLEAN )

    #remoev ,
    FILENAMECLEAN=re.sub(',+',',',FILENAMECLEAN)
    if debug: printE( 'File Clean ,: ', FILENAMECLEAN )

    #trim
    FILENAMECLEAN=FILENAMECLEAN.strip()
    
    return YEAR,CHAPTER,SEASON,CSREMOVE,FILENAMECLEAN

def getParam( param ):
    result=False
    
    #PARAMS
    ARG = sys.argv
    #printE( 'Number of arguments:', len(sys.argv), 'arguments.' )
    #printE( 'Argument List:', str(sys.argv) )
    next=False
    for a in ARG:
        #printE( 'Check ARG:', str(a) )
        if next:
            result=a
            break
        elif a == param:
            #printE( '+ARG:', str(a),param )
            #result=a.replace(param,'')
            result=''
            next=True
    
    return result

def getSearcher():
    result = ''
    global CMDSEARCHLIST
    
    for s in CMDSEARCHLIST:
        if is_tool(s):
            printE('External search set to:', s)
            result=s
            break
    
    return result

def is_tool(name):
    """Check whether `name` is on PATH and marked as executable."""

    # from whichcraft import which
    from shutil import which

    return which(name) is not None

def printE(msg1, msg2='',msg3='',msg4='',msg5=''):
    global G_NOINFO
    if G_NOINFO == False:
        print(msg1,msg2,msg3,msg4,msg5)

def extractChapter( filename ):
    season = False
    chapter = False
    sremove = False
    
    #Chapter 0000
    filter =  '(\d{3,4})'
    c=re.findall(filter, filename)
    for y in c:
        if int(y) > 99 and int(y) < 1910:
            printE( 'SeasonXChapter A: ', y )
            sremove=y
            season=int(int(y)/100)
            chapter=int(int(y)-(season*100))
            break
    
    if season == False:
        #Chapter SxC
        filter =  '(\d{1,2}x\d{1,2})'
        sep = 'x'
        c=re.findall(filter, filename)
        for y in c:
            s, ch = y.split( sep )
            if int(s) >= 1  and int(ch) > 0:
                printE( 'SeasonxChapter B: ', s, ch )
                sremove=s+sep+ch
                season=int(s)
                chapter=int(ch)
                break
    
    if season == False:
        #Chapter SXC
        filter =  '(\d{1,2}X\d{1,2})'
        sep = 'X'
        c=re.findall(filter, filename)
        for y in c:
            s, ch = y.split( sep )
            if int(s) >= 1  and int(ch) > 0:
                printE( 'SeasonXChapter C: ', s, ch )
                sremove=s+sep+ch
                season=int(s)
                chapter=int(ch)
                break
    
    return season, chapter, sremove

def nameFormat(format,MEDIAINFO):
    result=''
    debug=False
    #FORMATS
    #%title%
    #%year%
    #%director%
    #%season%
    #%chapter%
    #%genre%

    if debug: printE(' Formatting:', format)
    format=format.replace('%title%', MEDIAINFO['title'])
    if debug: printE(' Formatting:', format)
    format=format.replace('%year%', MEDIAINFO['year'])
    if debug: printE(' Formatting:', format)
    format=format.replace('%director%', MEDIAINFO['director'])
    if debug: printE(' Formatting:', format)
    format=format.replace('%season%', MEDIAINFO['season'].zfill(2))
    if debug: printE(' Formatting:', format)
    format=format.replace('%chapter%', MEDIAINFO['chapter'].zfill(2))
    if debug: printE(' Formatting:', format)
    format=format.replace('%genre%', MEDIAINFO['genres'].split(',')[0])
    if debug: printE(' Formatting:', format)
    format=format.replace('%chaptertitle%', MEDIAINFO['chaptertitle'])
    if debug: printE(' Formatting:', format)
    
    result=format
    
    return result

def interactiveShow(searchdata, defselection=False):
    result=False
    
    x=0
    urls={}
    for d in searchdata:
        checkexist=interactiveExist(d['url'],urls)
        #printE('CheckExist:',str(checkexist))
        if checkexist==False:
            printE( '===ITEM: ' + str(x) )
            printE( 'Element: ', d[ 'title' ], d[ 'url' ] )
            printE( 'Abstract: ' + d[ 'abstract' ] )
            urls[x]=(d[ 'url' ])
            x+=1
    
    if defselection!=False and defselection in urls.keys():
        printE( 'Forced Selected: ' + urls[defselection] )
        result=urls[defselection]
    else:
        while result==False or result.isdigit() == False or int(result) < 0 or int(result) > (x-1):
            result=input( 'Select item[0-'+str(x-1)+'][x:exit]: ' )
            if result == 'x':
                printE('Exit')
                exit(0)
        
        if int(result) in urls.keys():
            printE( 'Selected: ' + urls[int(result)] )
            result=urls[int(result)]
        else:
            printE( 'Invalid Selected, first: ' + urls[0] )
            result=urls[0]
    
    return result

def interactiveExist(url, urls):
    result=False
    debug=False
    
    a=extractIMDBID(url)
    if a:
        if debug: printE('Check IMDB:', a, str(urls))
        if a in str(urls):
            result=True
            if debug: printE('Check IMDB FINDED:', a, str(urls))
    if result==False:
        a=extractFilmAffinityID(url)
        if a:
            if debug: printE('Check FilmAffinity:', a, str(urls))
            a='film'+a
            if a in str(urls):
                if debug: printE('Check FilmAffinity FINDED:', a, str(urls))
                result=True
    if result==False:
        a=extractTheTVDBID(url)
        if a:
            if debug: printE('Check TheTVDB:', a, str(urls))
            a=''+a
            if a in str(urls):
                if debug: printE('Check TheTVDB FINDED:', a, str(urls))
                result=True
    
    return result

#INET SEARCH

def searchTitle( title, extra='imdb.com' ):
    global CMDSEARCH
    global CMDSEARCHLIST
    global G_INTERACTIVE
    result = []
    inlist=[]
    cmdapp=CMDSEARCH
    
    if G_INTERACTIVE:
        nn=input('Search for ['+str(title)+']:')
        if nn and len(nn)>0:
            title=nn
            
    inlist.append(cmdapp)
    #cmd = cmdapp + ' -w imdb.com --json "' + str( title ) + '"'
    cmd = cmdapp + ' --json "' + str( title ) + ' ' + extra + '"'
    data=searchExtCMD(cmd)
    
    if data == False:
        for s in CMDSEARCHLIST:
            if s not in inlist:
                cmdapp=s
                inlist.append(cmdapp)
                #cmd = cmdapp + ' -w imdb.com --json "' + str( title ) + '"'
                cmd = cmdapp + ' --json "' + str( title ) + ' ' + extra + '"'
                data=searchExtCMD(cmd)
                if data != False:
                    break
    
    if isinstance(data, list):
        result = data
        printE( "Links: ", len(data))
    else:
        printE( "Error NO Links: ", data)
        
    return result

def searchExtCMD( cmd ):
    data=False
    try:
        printE( "Search cmd: ", cmd)
        p = subprocess.Popen(cmd, stdout=subprocess.PIPE, shell=True)
        (output, err) = p.communicate()
        #printE( "Search Output: ", output )
        p_status = p.wait()
        #printE( "Return code : ", p_status )
        #get json data
        data  = json.loads(output)
    except:
        data=False
        pass
    
    return data

#IMDB

def extractIMDBID( url ):
    result = False
    
    #IMDBid tt0000000
    filter =  '(tt\d{7})'
    c=re.findall(filter, url)
    for y in c:
        #printE( 'IMDBid: ', y )
        result=y
        break
    
    return result

def getIMDBData( id ):
    result = False
    
    id =id.replace( 'tt', '' )
    printE( 'Get Data IMDB: ', id )
    
    ia = IMDb()
    result = ia.get_movie( id )
    #ia.update(result, 'all')
    ia.update(result, 'release dates')
    
    return result

def imdb_getReleaseDate(data):
    result = ''
    defdate = ''
    global G_COUNTRY
    
    if isinstance(data, list):
        for s in data:
            country, datenow = s.split('::')
            printE( 'Release date check: ', country, datenow )
            if defdate == '':
                try:
                    defdate = datetime.datetime.strptime(datenow, "%d %B %Y").strftime('%Y-%m-%d')
                except:
                    pass
                printE( 'Release date first defdate: ', defdate )
            elif country == G_COUNTRY:
                try:
                    result = datetime.datetime.strptime(datenow, "%d %B %Y").strftime('%Y-%m-%d')
                except:
                    pass
                printE( 'Release date finded: ', result )
                break
            elif country == G_COUNTRY_DEF:
                try:
                    defdate = datetime.datetime.strptime(datenow, "%d %B %Y").strftime('%Y-%m-%d')
                except:
                    pass
                printE( 'Release date defdate: ', defdate )
    
    if result == '':
        result = defdate
    
    return result

def imdb_getPlot(data):
    result = ''
    
    if isinstance(data, list):
        for s in data:
            d=s.split('::')
            if len(d) == 1:
                plot=d[0]
            else:
                plot=s
            if len(d) == 2:
                username=d[1]
            else:
                username=''
            #printE( 'Plot search: ', plot, username )
            if len(plot) > len(result):
                result=plot
    
    return result

def imdb_getPlotShort(data):
    result = ''
    
    if isinstance(data, list):
        for s in data:
            d=s.split('::')
            if len(d) == 1:
                plot=d[0]
            else:
                plot=s
            if len(d) == 2:
                username=d[1]
            else:
                username=''
            #printE( 'Plot Short search: ', plot, username )
            if len(result) == 0:
                result=plot
            elif len(result) > len(plot):
                result=plot
    
    return result

#FILMAFFINITY

def extractFilmAffinityID( url ):
    result = False
    
    #FilmAffinity /film605498.html
    filter =  '(film\d{6}.html)'
    c=re.findall(filter, url)
    for y in c:
        y=y.replace('film','').replace('.html','')
        if y.isdigit():
            #printE( 'FilmAffinityID: ', y )
            result=y
            break
    
    return result

#OMDB

def omdb_getReleaseDate(date):
    result=False
    
    if result==False:
        try:
            result=str(datetime.datetime.strptime(date, "%d %b %Y").strftime('%Y-%m-%d'))
        except:
            pass
    
    if result==False:
        try:
            result=str(datetime.datetime.strptime(date, "%d %B %Y").strftime('%Y-%m-%d'))
        except:
            pass
    
    if result==False:
        try:
            result=str(datetime.datetime.strptime(date, "%d-%m-%Y").strftime('%Y-%m-%d'))
        except:
            pass
    
    if result==False:
        try:
            result=str(datetime.datetime.strptime(date, "%Y-%m-%d").strftime('%Y-%m-%d'))
        except:
            pass
    
    
    return result

#TheTVDB

def extractTheTVDBID( url ):
    result = False
    
    #TheTVDB .thetvdb.com/?id=311902&tab=series
    filter =  '(id=\d{3,8}&)'
    c=re.findall(filter, url)
    for y in c:
        result=y.replace('id=','').replace('&','')
        printE( 'TheTVDB: ', result )
        break
    
    return result

def tvdbid_extradata(title,season,chapter):
    result=False
    
    printE('Extradata TheTVDB', title, season, chapter)
    t = tvdb_api.Tvdb(language=G_LANG)
    try:
        data = t[title]
        #printE('TheTVDB result: ',data.data.keys())
        #printE('Episode title TheTVDB result: ',data.data)
        if len(data.data.keys())>0:
            printE('Extradata TheTVDB result: ',data['seriesName'])
            result={}
            result['releasedate']=omdb_getReleaseDate(data['firstAired'])
            result['chaptertitle']=data[season][chapter]['episodeName']
    except:
        pass
    
    return result

#END FUNCTIONS

#PARAMS
ARG = sys.argv
#printE( 'Number of arguments:', len(sys.argv), 'arguments.' )
#printE( 'Argument List:', str(sys.argv) )

#ASSING PARAMS

#--json
p=getParam('--json')
if p != False:
    #printE('JSon response. ')
    G_JSON=True
    G_NOINFO=True
    
#BASE INFO
printE( '' )
printE( MSG_APPINFO )
printE( '' )

#-h or no params
if len(ARG) < 2 or getParam('-h') != False:
    G_NOINFO=False
    printE( 'Usage:' )
    printE( ' pymediaident.py [options] filetoscan' )
    printE( MSG_OPTIONS )
    printE( '' )
    FILE=False
    exit(0)

#-es
p=getParam('-es')
if p in CMDSEARCHLIST:
    printE('External search from:', p)
    CMDSEARCH=p
else:
    p=getSearcher()
    printE('Default External search from:', p)
    CMDSEARCH=p

#-s
p=getParam('-s')
if p in G_GETDATAFROM_LIST:
    printE('Assing webdata from:', p)
    G_GETDATAFROM=p

#-sid
p=getParam('-sid')
if p and len(p) > 0:
    printE('ID for scrapper from:', p)
    G_GETDATAFROM_ID=p

#-apikey
p=getParam('-apikey')
if p and len(p) > 0:
    printE('Apikey for:', G_GETDATAFROM)
    G_GETDATAFROM_KEY=p

#-l
p=getParam('-l')
if p and len( p ) == 2:
    printE('Assing languaje to:', p)
    G_LANG=p

#-c
p=getParam('-c')
if p!=False:
    printE('Assing country to:', str(p))
    G_COUNTRY=str(p)

#-rfm
p=getParam('-rfm')
if p != False:
    printE('Movies Format: ', p)
    G_RENAME_FORMAT_MOVIE=p

#-rfs
p=getParam('-rfs')
if p != False:
    printE('Series Format: ', p)
    G_RENAME_FORMAT_SERIE=p

#-r
p=getParam('-r')
if p != False:
    printE('Rename file to format. ')
    printE('-Movies: ', G_RENAME_FORMAT_MOVIE )
    printE('-Series: ', G_RENAME_FORMAT_SERIE )
    G_RENAME=True

#-m
p=getParam('-m')
if p != False and len(p) > 0:
    printE('Move to folder: ', p)
    G_MOVE=p

#-hl
p=getParam('-hl')
if p != False and len(p) > 0:
    printE('Hardlink to folder: ', p)
    G_HARDLINK=p

#-fs
p=getParam('-fs')
if p != False and len(p) > 0:
    printE('Search String: ', p)
    G_FSEARCHSTRING=p

#-i
p=getParam('-i')
if p != False:
    printE('Interactive Mode. ')
    G_INTERACTIVE=True

#-if
p=getParam('-if')
if p != False and len(p) > 0 and p.isdigit():
    printE('Interactive Mode select: ', p)
    G_INTERACTIVE_SET=int(p)

#-f FILENAME
FILE=False
p=getParam('-f')
if p != False and len(p) > 0:
    try:
        p=os.path.abspath(p)
        printE('File to ident: ', p)
        FILE=p
    except:
        printE('ERROR::File to scan: ', p)
        FILE=False
        pass

#-fp FOLDERPATH
FOLDERPATH=False
p=getParam('-fp')
if p != False and len(p) > 0:
    try:
        p=os.path.abspath(p)
        FOLDERPATH=p
        printE('Folder to scan: ', FOLDERPATH)
    except:
        printE('ERROR:Folder to scan: ', p)
        FOLDERPATH=False
        pass

#-fps
p=getParam('-fps')
if p != False and len(p) > 0 and p.isdigit():
    printE('Min file size to: ', p, 'Mb')
    G_MEDIAMINSIZE=int(p) * 1024 * 1024

#-dr
p=getParam('-dr')
if p != False:
    printE('DryRun: not making changes')
    G_DRYRUN=True

#-bwf
p=getParam('-bwf')
if p != False and len(p) > 0:
    printE('BadWordsFile: ', p)
    G_BADWORDSFILE=p
    getBadWordsFile(G_BADWORDSFILE)
    printE('BadWords Total:', len(G_BADWORDS))

#check file

if FILE:
    if os.path.isfile( FILE ) == False:
        printE( 'File not exist: ', str(FILE) )
        FILE=False
    else:
        printE( 'File exist: ', FILE )

    #file needed
    if FILE==False:
        printE( 'ERROR::No file to ident.' )
        exit(1)

#check folder

if FOLDERPATH:
    if os.path.isdir( FOLDERPATH ) == False:
        printE( 'Folder not exist: ', str(FOLDERPATH) )
        FILE=False
    else:
        printE( 'Folder exist: ', FOLDERPATH )
    
    #folder needed
    if FOLDERPATH==False:
        printE( 'ERROR::No folder to ident.' )
        exit(1)
    
elif G_FSEARCHSTRING:
    printE( 'Forced Search String: ', G_FSEARCHSTRING )
    FILE=G_FSEARCHSTRING

#external search needed
if is_tool(CMDSEARCH) == False:
    printE( 'ERROR::External search not found, install: ', str( CMDSEARCHLIST ))
    exit(1)


#GET FILES OF FOLDER IF NEEDED

FILELIST=[]
#force only search string, file or full folder
if G_FSEARCHSTRING:
    FILELIST.append(G_FSEARCHSTRING)
elif FILE!=False:
    FILELIST.append(FILE)
else:
    FILELIST=getFilesMedia(FOLDERPATH)

#FILE ACTIONS

#FILENAME CLEAN

for FILE in FILELIST:
    #filename
    FILENAME=ntpath.basename(FILE)
    printE( 'File: ', FILENAME )
    YEAR,CHAPTER,SEASON,CSREMOVE,FILENAMECLEAN=cleanFileName(FILENAME)

    #SEARCH TITLE from clean file
    SEARCHTITLE = FILENAMECLEAN + ' ' + YEAR


    ##GET DATA

    #MEDIA INFO DATA
    #title
    #plot
    #plotshort
    #kind
    #releasedate
    #year
    #director
    #season
    #chapter
    #chaptertitle
    #mpaa
    #rating
    #votes
    #genres: a,b,...
    #actors: a,b,...
    #urlposter: 
    MEDIADATA={}

    ##TEST
    if G_GETDATAFROM == 'test':
        printE('##')
        printE('TESTING Filename: ', FILENAME)
        printE('TESTING Search Title: ', SEARCHTITLE)

    ##IMDB
    elif G_GETDATAFROM == 'imdb':
        imdbid = False
        url=False
        
        if len(G_GETDATAFROM_ID) > 0:
            imdbid=G_GETDATAFROM_ID
            printE( 'IMDBid(forced): ' + imdbid )
        else:
            if SEASON != False:
                SEARCHTITLE += ' ' + str( SEASON ) + 'x' + str( CHAPTER ) + ' serie '
            
            #forced searchstring
            if G_FSEARCHSTRING:
                if SEASON != False:
                    G_FSEARCHSTRING += ' serie '
                printE( 'Forced Search Title: ', G_FSEARCHSTRING )
                SEARCHTITLE=G_FSEARCHSTRING
            
            printE( 'IMDB Search Title: ', SEARCHTITLE )
            searchdata = searchTitle( SEARCHTITLE )
            
            if searchdata != False and G_INTERACTIVE:
                printE( '##INTERACTIVE' )
                printE( '##LINKS' )
                url=interactiveShow(searchdata,G_INTERACTIVE_SET)
            elif searchdata != False:
                printE( '##LINKS' )
                for d in searchdata:
                    printE( 'Title: ' + d[ 'title' ] )
                    printE( 'URL: ' + d[ 'url' ] )
                    printE( 'Abstract: ' + d[ 'abstract' ] )
                    url=d[ 'url' ]
                    break
            else:
                printE( 'Search without data.' )
        
        if url:
            imdbid = extractIMDBID(url)
            if imdbid != False:
                printE( 'IMDBid: ' + imdbid )
            
        #With IMDBid get data
        if imdbid != False:
            printE( 'Get IMDB data: ', imdbid )
            data = getIMDBData( imdbid )
            printE( 'Title: ', data.get( 'title' ) )
            printE( 'Plots list: ', data.get( 'plot' ) )
            plot=imdb_getPlot(data.get( 'plot' ))
            printE( 'Plot: ', plot )
            plotshort=imdb_getPlotShort(data.get( 'plot' ))
            printE( 'Plot Short: ', plotshort )
            printE( 'Year: ', data.get( 'year' ) )
            #kind; string; one in ('movie', 'tv series', 'tv mini series', 'video game', 'video movie', 'tv movie', 'episode')
            printE( 'Kind: ', data.get( 'kind' ) )
            printE( 'Release Date A: ', data.get( 'release_date' ) )
            if data.has_key('release dates'):
                reldate=imdb_getReleaseDate( data['release dates'] )
                printE( 'Release Date B: ', reldate )
            else:
                #TODO middle of year
                reldate=str(data.get( 'year' ))+'-06-15'
                printE( 'Release Date C: ', reldate )
            c = data.get( 'cast' )
            actors=[]
            if c:
                for a in c[:ACTORS_MAX]:
                    printE( ' Actors: ', a[ 'name' ] )
                    actors.append(a['name'])
                    
            #EXTRA DATA thetvdb
            chaptertitle=''
            title=data.get( 'title' )
            if SEASON != False and CHAPTER != False and len(chaptertitle) == 0:
                #printE( 'Search extradata: ', title, SEASON, CHAPTER )
                exdata=tvdbid_extradata(title,SEASON,CHAPTER)
                if exdata != False:
                    chaptertitle=exdata['chaptertitle']
                    if reldate.endswith('-06-15') and \
                    exdata['releasedate'] != False and \
                    len(exdata['releasedate']) > 0:
                        reldate=exdata['releasedate']
                
            #Prepare data
            MEDIADATA['title']=data.get( 'title' )
            MEDIADATA['plot']=plot
            MEDIADATA['plotshort']=plotshort
            MEDIADATA['kind']=data.get( 'kind' )
            MEDIADATA['releasedate']=reldate
            MEDIADATA['year']=str(data.get( 'year' ))
            director=data.get( 'director' )
            if isinstance(director,list) and len(director)>0:
                director=director[0]['name']
            else:
                director=''
            MEDIADATA['director']=director
            if SEASON != False:
                MEDIADATA['season']=str( SEASON )
            else:
                MEDIADATA['season']=''
            if CHAPTER != False:
                MEDIADATA['chapter']=str( CHAPTER )
            else:
                MEDIADATA['chapter']=''
            MEDIADATA['mpaa']=data.get( 'mpaa' )
            MEDIADATA['rating']=data.get( 'rating' )
            MEDIADATA['votes']=str(data.get( 'votes' ))
            MEDIADATA['genres']=','.join(data.get( 'genres' ))
            MEDIADATA['actors']=','.join(actors)
            MEDIADATA['urlposter']=data.get('cover url')
            #chaptertitle
            MEDIADATA['chaptertitle']=chaptertitle
        else:
            printE('IMDB No data.')
            
    ##FILMAFFINITY

    elif G_GETDATAFROM == 'filmaffinity':
        dataid = False
        
        if len(G_GETDATAFROM_ID) > 0:
            dataid=G_GETDATAFROM_ID
            printE( 'FilmAffinityID(forced): ' + dataid )
        else:
            if SEASON != False:
                SEARCHTITLE += ' ' + str( SEASON ) + 'x' + str( CHAPTER ) + ' serie '
            
            #forced searchstring
            if G_FSEARCHSTRING:
                if SEASON != False:
                    G_FSEARCHSTRING += ' serie '
                printE( 'Forced Search Title: ', G_FSEARCHSTRING )
                SEARCHTITLE=G_FSEARCHSTRING
            
            printE( 'FILMAFFINITY Search Title: ', SEARCHTITLE )
            searchdata = searchTitle( SEARCHTITLE, 'filmaffinity.com' )
            url=False
            
            if searchdata != False and G_INTERACTIVE:
                printE( '##INTERACTIVE' )
                printE( '##LINKS' )
                url=interactiveShow(searchdata,G_INTERACTIVE_SET)
            elif searchdata != False:
                printE( '##LINKS' )
                for d in searchdata:
                    printE( 'Title: ' + d[ 'title' ] )
                    printE( 'URL: ' + d[ 'url' ] )
                    printE( 'Abstract: ' + d[ 'abstract' ] )
                    dataid = extractFilmAffinityID( d[ 'url' ] )
                    if dataid != False:
                        url=d[ 'url' ]
                        break
            else:
                printE( 'Search without data.' )
        
        if url:
            dataid = extractFilmAffinityID(url)
            printE( 'FilmAffinityID: ' + dataid )
            
        #with dataid
        
        if dataid:
            printE( 'Get FilmAffinity data: ', dataid )
            service = python_filmaffinity.FilmAffinity(lang=G_LANG)
            data = service.get_movie(id=dataid)
            #printE('FilmAffinity result: ',data)
            #printE('FilmAffinity result: ',data.keys())
            
            if data:
                title=re.sub('\(.*?\)', '', data[ 'title' ]).strip()
                printE( 'Title: ', title )
                printE( 'Plot: ', data['description'] )
                printE( 'Plot Short: ', '' )
                printE( 'Year: ', data['year'] )
                
                #kind; string; one in ('movie', 'tv series', 'tv mini series', 'video game', 'video movie', 'tv movie', 'episode')
                kind=''
                if isinstance(data['genre'],list):
                    if 'erie' in str(data['genre']):
                        kind='tv serie'
                    else:
                        kind='movie'
                printE( 'Kind: ', kind )
                
                #TODO: middle of year
                reldate=data['year']+'-06-15'
                printE( 'Release Date: ', reldate )
                
                c = data['directors']
                director=''
                if c and isinstance(c,list):
                    a=re.sub('\(.*?\)', '', c[0]).strip()
                    printE( 'Director: ', a )
                    director=a
                
                c = data['actors']
                actors=[]
                if c and isinstance(c,list):
                    for a in c[:ACTORS_MAX]:
                        a=re.sub('\(.*?\)', '', a).strip()
                        printE( ' Actors: ', a)
                        actors.append(a)
                
                c = data['genre']
                genres=[]
                if c and isinstance(c,list):
                    for a in c[:10]:
                        printE( ' Genres: ', a )
                        genres.append(a)
                
                #EXTRA DATA thetvdb
                chaptertitle=''
                if SEASON != False and CHAPTER != False and len(chaptertitle) == 0:
                    #printE( 'Search extradata: ', title, SEASON, CHAPTER )
                    exdata=tvdbid_extradata(title,SEASON,CHAPTER)
                    if exdata != False:
                        chaptertitle=exdata['chaptertitle']
                        if reldate.endswith('-06-15') and \
                        exdata['releasedate'] != False and \
                        len(exdata['releasedate']) > 0:
                            reldate=exdata['releasedate']
                
                #Prepare data
                MEDIADATA['title']=title
                MEDIADATA['plot']=data[ 'description' ]
                MEDIADATA['plotshort']=''
                MEDIADATA['kind']=kind
                MEDIADATA['releasedate']=reldate
                MEDIADATA['year']=data['year']
                MEDIADATA['director']=director
                if SEASON != False:
                    MEDIADATA['season']=str( SEASON )
                else:
                    MEDIADATA['season']=''
                if CHAPTER != False:
                    MEDIADATA['chapter']=str( CHAPTER )
                else:
                    MEDIADATA['chapter']=''
                MEDIADATA['mpaa']=''
                MEDIADATA['rating']=data['rating']
                MEDIADATA['votes']=data['votes']
                MEDIADATA['genres']=','.join(genres)
                MEDIADATA['actors']=','.join(actors)
                MEDIADATA['urlposter']=data['poster']
                #episodeName chaptertitle
                MEDIADATA['chaptertitle']=chaptertitle
            else:
                printE('FilmAffinity No data.')

    #OMDB

    elif G_GETDATAFROM == 'omdb':
        dataid = False
        if len(G_GETDATAFROM_KEY) == 0:
            printE('No valid apikey for OMDB')
            exit(1)
        
        if len(G_GETDATAFROM_ID) > 0:
            dataid=G_GETDATAFROM_ID
            printE( 'OMDB(forced): ' + dataid )
        else:
            if SEASON != False:
                SEARCHTITLE += ' ' + str( SEASON ) + 'x' + str( CHAPTER ) + ' serie '
                
            #forced searchstring
            if G_FSEARCHSTRING:
                if SEASON != False:
                    G_FSEARCHSTRING += ' serie '
                printE( 'Forced Search Title: ', G_FSEARCHSTRING )
                SEARCHTITLE=G_FSEARCHSTRING
            
            printE( 'OMDB Search Title: ', SEARCHTITLE )
            searchdata = searchTitle( SEARCHTITLE, 'imdb.com' )
            url=False
            
            if searchdata != False and G_INTERACTIVE:
                printE( '##INTERACTIVE' )
                printE( '##LINKS' )
                url=interactiveShow(searchdata,G_INTERACTIVE_SET)
            elif searchdata != False:
                printE( '##LINKS' )
                for d in searchdata:
                    printE( 'Title: ' + d[ 'title' ] )
                    printE( 'URL: ' + d[ 'url' ] )
                    printE( 'Abstract: ' + d[ 'abstract' ] )
                    url=d[ 'url' ]
                    break
            else:
                printE( 'Search without data.' )
        
        if url:
            dataid = extractIMDBID(url)
            if dataid!=False:
                printE( 'IMDBid: '+dataid )
            
        #with dataid
        
        if dataid:
            printE( 'Get OMDB data: ', dataid )
            omdb.set_default('apikey', G_GETDATAFROM_KEY)
            data=omdb.imdbid('tt'+str(dataid).replace( 'tt', '' ))
            printE('OMDB result: ',data.get('title'))
            
            if data:
                printE( 'Title: ', data.get('title') )
                printE( 'Plot: ', data.get('plot') )
                printE( 'Plot Short: ', '' )
                printE( 'Year: ', data.get('year') )
                printE( 'Genre: ', data.get('genre') )
                printE( 'actors: ', data.get('actors') )
                
                #kind; string; one in ('movie', 'tv series', 'tv mini series', 'video game', 'video movie', 'tv movie', 'episode')
                kind=data.get('type')
                printE( 'Kind: ', kind )
                
                reldate=omdb_getReleaseDate(data.get('released'))
                #TODO: middle of year
                if reldate == False or len(reldate) == 0:
                    reldate=data.get('year')+'-06-15'
                printE( 'Release Date: ', reldate )
                
                director=data.get('director')
                
                actors=data.get('actors')
                
                genres=data.get('genre')
                
                #Prepare data
                MEDIADATA['title']=data.get('title')
                MEDIADATA['plot']=data.get('plot')
                MEDIADATA['plotshort']=''
                MEDIADATA['kind']=kind
                MEDIADATA['releasedate']=reldate
                MEDIADATA['year']=data.get('year')
                MEDIADATA['director']=director
                if SEASON != False:
                    MEDIADATA['season']=str( SEASON )
                else:
                    MEDIADATA['season']=''
                if CHAPTER != False:
                    MEDIADATA['chapter']=str( CHAPTER )
                else:
                    MEDIADATA['chapter']=''
                MEDIADATA['chaptertitle']=''
                MEDIADATA['mpaa']=data.get('rated')
                MEDIADATA['rating']=data.get('imdb_rating')
                MEDIADATA['votes']=data.get('imdb_votes')
                MEDIADATA['genres']=genres
                MEDIADATA['actors']=actors
                MEDIADATA['urlposter']=data.get('poster')
            else:
                printE('OMDB No data.')

    #TheTVDB

    elif G_GETDATAFROM == 'thetvdb':
        dataid = False
        title = SEARCHTITLE
        
        if len(G_GETDATAFROM_KEY) == 0:
            printE('No valid apikey for TheTVDB')
            #exit(1)
        
        if len(G_GETDATAFROM_ID) > 0:
            dataid=G_GETDATAFROM_ID
            printE( 'TheTVDB(forced): ', dataid )
        else:
            if SEASON != False:
                SEARCHTITLE += ' ' + str( SEASON ) + 'x' + str( CHAPTER ) + ' serie '
                
            #forced searchstring
            if G_FSEARCHSTRING:
                if SEASON != False:
                    G_FSEARCHSTRING += ' serie '
                printE( 'Forced Search Title: ', G_FSEARCHSTRING )
                SEARCHTITLE=G_FSEARCHSTRING
            
            printE( 'TheTVDB Search Title: ', SEARCHTITLE )
            searchdata = searchTitle( SEARCHTITLE, 'thetvdb.com' )
            url=False
            
            if searchdata != False and G_INTERACTIVE:
                printE( '##INTERACTIVE' )
                printE( '##LINKS' )
                url=interactiveShow(searchdata,G_INTERACTIVE_SET)
            elif searchdata != False:
                printE( '##LINKS' )
                for d in searchdata:
                    printE( 'Title: ' + d[ 'title' ] )
                    printE( 'URL: ' + d[ 'url' ] )
                    printE( 'Abstract: ' + d[ 'abstract' ] )
                    url=d[ 'url' ]
                    #TODO clean name
                    title=d[ 'title' ].split('(')[0].split(':')[0]
                    break
            else:
                printE( 'Search without data.' )
        
        if url:
            dataid = extractTheTVDBID(url)
            if dataid!=False:
                printE( 'TheTVDB: ',dataid,title )
        
        #with dataid
        
        if dataid:
            printE( 'Get TheTVDB data: ', dataid, title )
            # apikey G_GETDATAFROM_KEY)
            #TODO banners = True
            t = tvdb_api.Tvdb(language=G_LANG)
            data = t[title]
            #printE('TheTVDB result: ',data.data.keys())
            #printE('TheTVDB result: ',data.data)
            
            if data:
                printE( 'Title: ', data['seriesName'] )
                printE( 'Plot: ', data['overview'] )
                printE( 'Plot Short: ', '' )
                printE( 'Year: ', data['firstAired'].split('-')[0] )
                
                c = data['genre']
                genres=[]
                if c and isinstance(c,list):
                    for a in c[:10]:
                        printE( ' Genres: ', a )
                        genres.append(a)
                
                #kind; string; one in ('movie', 'tv series', 'tv mini series', 'video game', 'video movie', 'tv movie', 'episode')
                kind='tv serie'
                printE( 'Kind: ', kind )
                
                reldate=omdb_getReleaseDate(data['firstAired'])
                #TODO: middle of year
                if reldate == False or len(reldate) == 0:
                    reldate=data['firstAired']
                printE( 'Release Date: ', reldate )
                
                director=''
                actors=''
                if SEASON != False and CHAPTER != False:
                    chaptername=data[SEASON][CHAPTER]['episodeName']
                else:
                    chaptername=''
                
                #Prepare data
                MEDIADATA['title']=data['seriesName']
                MEDIADATA['plot']=data['overview']
                MEDIADATA['plotshort']=''
                MEDIADATA['kind']=kind
                MEDIADATA['releasedate']=reldate
                MEDIADATA['year']=data['firstAired'].split('-')[0]
                MEDIADATA['director']=director
                if SEASON != False:
                    MEDIADATA['season']=str( SEASON )
                else:
                    MEDIADATA['season']=''
                if CHAPTER != False:
                    MEDIADATA['chapter']=str( CHAPTER )
                else:
                    MEDIADATA['chapter']=''
                MEDIADATA['chaptertitle']=''
                MEDIADATA['mpaa']=data['rating']
                MEDIADATA['rating']=data['siteRating']
                MEDIADATA['votes']=data['siteRatingCount']
                MEDIADATA['genres']=','.join(genres)
                MEDIADATA['actors']=actors
                MEDIADATA['urlposter']=''
                #episodeName chaptertitle
                MEDIADATA['chaptertitle']=chaptername
            else:
                printE('TheTVDB No data.')

    #END ACTIONS

    if G_JSON:
        print( json.dumps(MEDIADATA, indent=4, sort_keys=True, ensure_ascii=False) )
        exit()

    #ACTIONS ON FILE

    if os.path.isfile( FILE ) == False:
        printE('File not found')
    elif 'title' in MEDIADATA.keys():
        nfile=FILE
        #-r rename
        if G_RENAME:
            printE('##Renaming')
            if 'movie' in MEDIADATA['kind']:
                FORMAT=G_RENAME_FORMAT_MOVIE
            else:
                FORMAT=G_RENAME_FORMAT_SERIE
            printE('Format:', FORMAT)
            NEWNAME=nameFormat(FORMAT,MEDIADATA).encode( "utf-8", errors="ignore")
            #extension
            filename, file_extension = os.path.splitext(nfile)
            try:
                NEWNAME+=file_extension.encode( "utf-8", errors="ignore")
            except:
                NEWNAME+=file_extension
            printE('New Name:', NEWNAME)
            ufile=os.path.dirname(FILE).encode('UTF-8')
            nfile=os.path.join(ufile, NEWNAME)
            if G_DRYRUN:
                printE('DryRun Mode:', nfile)
            else:
                printE('Rename:', FILE, nfile)
                a=nfile
                try:
                    os.rename( FILE, a )
                except:
                    pass
        
        #-hl hardlink
        if G_HARDLINK:
            printE('##HardLink')
            printE('Format:', G_HARDLINK)
            NEWFOLDERFILE=nameFormat(G_HARDLINK,MEDIADATA).encode( "utf-8", errors="ignore")
            printE('hardlink to:', NEWFOLDERFILE)
            if G_DRYRUN:
                printE('DryRun Mode:', NEWFOLDERFILE)
            else:
                NEWFOLDER=NEWFOLDERFILE
                os.makedirs(NEWFOLDER, exist_ok=True)
                if os.path.isdir( NEWFOLDER ):
                    printE('Folder Created:', NEWFOLDER)
                    try:
                        ufile=os.path.basename(nfile).encode('UTF-8', errors="ignore")
                    except:
                        ufile=os.path.basename(nfile)
                    printE('Hardlinking file:', NEWFOLDER,ufile)
                    nfile2=os.path.join(NEWFOLDER,ufile)
                    #nfile2=NEWFOLDERFILE
                    try:
                        os.link( nfile, nfile2)
                    except:
                        pass
                    if os.path.isfile(nfile2):
                        printE('File hardlinked:', nfile2)
                    else:
                        printE('Error hardlinking file:', nfile2)
                else:
                    printE('Error creating folder:', NEWFOLDER)

        #-m move
        elif G_MOVE:
            printE('##Moving')
            printE('Format:', G_MOVE)
            NEWFOLDER=nameFormat(G_MOVE,MEDIADATA).encode( "utf-8", errors="ignore")
            printE('Folder to move:', NEWFOLDER)
            if G_DRYRUN:
                printE('DryRun Mode:', NEWFOLDER)
            else:
                os.makedirs(NEWFOLDER, exist_ok=True)
                if os.path.isdir(NEWFOLDER):
                    printE('Folder Created:', NEWFOLDER)
                    try:
                        ufile=os.path.basename(nfile).encode('UTF-8', errors="ignore")
                    except:
                        ufile=os.path.basename(nfile)
                    printE('Movinf file:', NEWFOLDER,ufile)
                    nfile2=os.path.join(NEWFOLDER,ufile)
                    try:
                        os.rename( nfile, nfile2)
                    except:
                        pass
                    if os.path.isfile(nfile2):
                        printE('File Moved:', nfile2)
                    else:
                        printE('Error moving file:', nfile2)
                else:
                    printE('Error creating folder:', NEWFOLDER)
    
printE('#END#')
