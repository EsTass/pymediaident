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


#CONFIGS
remove_extension = [ '.avi', '.mp4', '.mpeg', '.mkv', '.mpeg4', '.ogm' ]
# web data from. imdb|filmaffinity
G_GETDATAFROM_LIST=[ 'imdb', 'filmaffinity', 'omdb' ]
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

#OPTIONS
OPTIONSMSG = '''
OPTIONS
 -h : help
 -f FILETOIDENT : path to file to ident
 -es 'googler|ddgr|ducker' : external search
 -s imdb|filmaffinity|omdb : get data from
 -sid XXX : forced id for imdb|filmaffinity|omdb
 -apikey XXX : apikey for omdb
 -l en|es|mx|ar|cl|co... : languaje
 -c USA : country for release date
 -r : rename
 -rfm "%title% (%year%, %director%)" : rename format movie
 -rfs "%title% %season%x%chapter%(%year%, %director%)" : rename format eries
 -m "/path/%title%": move file to folder with format name 
 -hl "/path/%title%": hardlink file to folder with format name 
 --json : return onlyjson data
 -dr : dryrun, force not changes
 -i : interactive mode, select search result to assign
 -if X: force select X position of interactive mode
 -fs "Search String" : force search string for file
 
Formats for -rfm -rfs -m -hl
 %title%
 %year%
 %director%
 %season%
 %chapter%
 %chaptertitle%
 %genre%
 
'''


#FUNCTIONS

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
    
    a=extractIMDBID(url)
    if a:
        #printE('Check IMDB:', a, str(urls))
        if a in str(urls):
            result=True
            #printE('Check IMDB FINDED:', a, str(urls))
    if result==False:
        a=extractFilmAffinityID(url)
        if a:
            #printE('Check FilmAffinity:', a, str(urls))
            a='film'+a
            if a in str(urls):
                #printE('Check FilmAffinity FINDED:', a, str(urls))
                result=True
    
    return result

#INET SEARCH

def searchTitle( title, extra='imdb.com' ):
    global CMDSEARCH
    result = []
    #cmd = CMDSEARCH + ' -w imdb.com --json "' + str( title ) + '"'
    cmd = CMDSEARCH + ' --json "' + str( title ) + ' ' + extra + '"'
    
    p = subprocess.Popen(cmd, stdout=subprocess.PIPE, shell=True)
     
    (output, err) = p.communicate()
    p_status = p.wait()
    
    printE( "Search cmd: ", cmd)
    #printE( "Search Output: ", output )
    #printE( "Return code : ", p_status )
    #result = output
    
    #get json data
    data  = json.loads(output)
    if isinstance(data, list):
        result = data
        printE( "Links: ", len(data))
    else:
        printE( "Error NO Links: ", output)
        
    return result

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
    
    
    return result

#END FUNCTIONS

#PARAMS
ARG = sys.argv
#printE( 'Number of arguments:', len(sys.argv), 'arguments.' )
#printE( 'Argument List:', str(sys.argv) )

#ASSING PARAMS

'''
 -h : help
 -f FILETOIDENT : path to file to ident
 -es 'googler|ddgr|ducker' : external search
 -s imdb|filmaffinity|omdb : get data from
 -sid XXX : forced id for imdb|filmaffinity|omdb
 -apikey XXX : apikey for omdb
 -l en|es|mx|ar|cl|co... : languaje
 -c USA : country for release date
 -r : rename
 -rfm "%title% (%year%, %director%)" : rename format movie
 -rfs "%title% %season%x%chapter%(%year%, %director%)" : rename format eries
 -m "/path/%title%": move file to folder with format name 
 -hl "/path/%title%": hardlink file to folder with format name 
 --json : return onlyjson data
 -dr : dryrun, force not changes
 -i : interactive mode, select search result to assign
 -if X: force X position of interactive mode
 -fs "Search String" : force search string for file
 '''

#--json
p=getParam('--json')
if p != False:
    #printE('JSon response. ')
    G_JSON=True
    G_NOINFO=True
    
#BASE INFO
printE( '' )
printE( 'pymediaident 2018 https://github.com/EsTass/' )
printE( '' )

#-h or no params
if len(ARG) < 2 or getParam('-h') != False:
    G_NOINFO=False
    printE( 'Usage:' )
    printE( ' pymediaident.py [options] filetoscan' )
    printE( OPTIONSMSG )
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
    printE('File to ident: ', p)
    FILE=p

#-dr
p=getParam('-dr')
if p != False:
    printE('DryRun: not making changes')
    G_DRYRUN=True

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
    
elif G_FSEARCHSTRING:
    printE( 'Forced Search String: ', G_FSEARCHSTRING )
    FILE=G_FSEARCHSTRING

#external search needed
if is_tool(CMDSEARCH) == False:
    printE( 'ERROR::External search not found, install: ', str( CMDSEARCHLIST ))
    exit(1)


#FILENAME CLEAN


#filename
FILENAME=ntpath.basename(FILE)
printE( 'File: ', FILENAME )

#EXTRACT YEAR
#YEAR=re.search(r"\d{4}", FILENAME).group(1)
YEARS=re.findall('(\d{4})', FILENAME)
YEAR=''
for y in YEARS:
    if int(y) > 1900 and int(y) < (datetime.date.today().year + 2):
        printE( 'YEAR: ', y )
        YEAR=y
        break

#EXTRACT CHAPTER
CHAPTER=False
SEASON=False
CSREMOVE=False
SEASON, CHAPTER, CSREMOVE = extractChapter( FILENAME )
if SEASON != False:
    printE( 'Season: ', SEASON )
    printE( 'Chapter: ', CHAPTER )
    printE( 'Detected: ', CSREMOVE )
else:
    printE( 'No Series data (sxc): ', FILENAME )

#CLEAN FILENAME

FILENAMECLEAN=FILENAME

#REMOVE SEASONxCHAPTER
if CSREMOVE != False:
    FILENAMECLEAN=FILENAMECLEAN.replace(CSREMOVE,'')
    printE( 'File Clean SEASONxCHPATER: ', FILENAMECLEAN )

#REMOVE YEAR
FILENAMECLEAN=FILENAMECLEAN.replace(YEAR,'')
printE( 'File Clean YEAR: ', FILENAMECLEAN )

#()
FILENAMECLEAN=re.sub('\(.*?\)', '', FILENAMECLEAN)
printE( 'File Clean (): ', FILENAMECLEAN )

#[]
FILENAMECLEAN=re.sub('\[.*?\]', '', FILENAMECLEAN)
printE( 'File Clean []: ', FILENAMECLEAN )

#domains
FILENAMECLEAN=re.sub(r'(?i)\b((?:https?://|www\d{0,3}[.]|[a-z0-9.\-]+[.][a-z]{2,4}     /)(?:[^\s()<>]+|\(([^\s()<>]+|(\([^\s()<>]+\)))*\))+(?:\(([^\s()<>]+|(\([^\s()<>]+\)))*\)|[^\s`!()\[\]{};:\'".,<>?«»“”‘’]))', '', FILENAMECLEAN)
printE( 'File Clean Domains: ', FILENAMECLEAN )

#remove extensions
for rext in remove_extension:
    FILENAMECLEAN=FILENAMECLEAN.replace(rext, ' ')
printE( 'File Clean extensions: ', FILENAMECLEAN )

#remove all non alfanumeric chars
FILENAMECLEAN=re.sub(r'[^a-zA-Z0-9]', ' ',FILENAMECLEAN)
printE( 'File Clean All except chars: ', FILENAMECLEAN )

#extra .
FILENAMECLEAN=re.sub('\.+','.',FILENAMECLEAN)
printE( 'File Clean .: ', FILENAMECLEAN )

#extra spaces
FILENAMECLEAN=re.sub(' +',' ',FILENAMECLEAN)
printE( 'File Clean spaces: ', FILENAMECLEAN )

#remoev ,
FILENAMECLEAN=re.sub(',+',',',FILENAMECLEAN)
printE( 'File Clean ,: ', FILENAMECLEAN )

#trim
FILENAMECLEAN=FILENAMECLEAN.strip()

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

##IMDB
if G_GETDATAFROM == 'imdb':
    imdbid = False
    url=False
    
    if len(G_GETDATAFROM_ID) > 0:
        imdbid=G_GETDATAFROM_ID
        printE( 'IMDBid(forced): ' + imdbid )
    else:
        if SEASON != False:
            SEARCHTITLE += ' ' + str( SEASON ) + 'x' + str( CHAPTER )
        
        #forced searchstring
        if G_FSEARCHSTRING:
            printE( 'Forced Search Title: ', SEARCHTITLE )
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
        MEDIADATA['chaptertitle']=''
        MEDIADATA['mpaa']=data.get( 'mpaa' )
        MEDIADATA['rating']=data.get( 'rating' )
        MEDIADATA['votes']=str(data.get( 'votes' ))
        MEDIADATA['genres']=','.join(data.get( 'genres' ))
        MEDIADATA['actors']=','.join(actors)
        MEDIADATA['urlposter']=data.get('cover url')
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
            SEARCHTITLE += ' ' + str( SEASON ) + 'x' + str( CHAPTER )
        
        #forced searchstring
        if G_FSEARCHSTRING:
            printE( 'Forced Search Title: ', SEARCHTITLE )
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
        printE('FilmAffinity result: ',data)
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
            MEDIADATA['chaptertitle']=''
            MEDIADATA['mpaa']=''
            MEDIADATA['rating']=data['rating']
            MEDIADATA['votes']=data['votes']
            MEDIADATA['genres']=','.join(genres)
            MEDIADATA['actors']=','.join(actors)
            MEDIADATA['urlposter']=data['poster']
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
            SEARCHTITLE += ' ' + str( SEASON ) + 'x' + str( CHAPTER )
            
        #forced searchstring
        if G_FSEARCHSTRING:
            printE( 'Forced Search Title: ', SEARCHTITLE )
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
        NEWNAME=nameFormat(FORMAT,MEDIADATA)
        #extension
        filename, file_extension = os.path.splitext(nfile)
        NEWNAME+=file_extension
        printE('New Name:', NEWNAME)
        nfile=os.path.join(os.path.dirname(FILE), NEWNAME).encode( "utf-8", errors="ignore")
        if G_DRYRUN:
            printE('DryRun Mode:', nfile)
        else:
            printE('Rename:', FILE, nfile)
            a=nfile
            os.rename( FILE, a )
    
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
                nfile2=os.path.join(NEWFOLDER,os.path.basename(nfile))
                #nfile2=NEWFOLDERFILE
                os.link( nfile, nfile2)
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
                nfile2=os.path.join(NEWFOLDER,os.path.basename(nfile))
                os.rename( nfile, nfile2)
                if os.path.isfile(nfile2):
                    printE('File Moved:', nfile2)
                else:
                    printE('Error moving file:', nfile2)
            else:
                printE('Error creating folder:', NEWFOLDER)
    
