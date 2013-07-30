#!/usr/bin/python
# -*- coding: utf-8 -*-
#/*
# *      Copyright (C) 2011 Silen
# *
# *
# *  This Program is free software; you can redistribute it and/or modify
# *  it under the terms of the GNU General Public License as published by
# *  the Free Software Foundation; either version 2, or (at your option)
# *  any later version.
# *
# *  This Program is distributed in the hope that it will be useful,
# *  but WITHOUT ANY WARRANTY; without even the implied warranty of
# *  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# *  GNU General Public License for more details.
# *
# *  You should have received a copy of the GNU General Public License
# *  along with this program; see the file COPYING.  If not, write to
# *  the Free Software Foundation, 675 Mass Ave, Cambridge, MA 02139, USA.
# *  http://www.gnu.org/copyleft/gpl.html
# */

import re, os, urllib, urllib2, cookielib, time

try:
    from hashlib import md5 as md5
except:
    import md5

import xbmc, xbmcgui, xbmcplugin, xbmcaddon, xbmcvfs, json #myshows
from datetime import date
from urlparse import urlparse

Addon = xbmcaddon.Addon(id='plugin.video.serialu.net')
try:
    ruspath=Addon.getAddonInfo('path')#myshows
    f= open(os.path.join(ruspath, r'resources', r'lib', r'settings.xml'), 'r')#myshows
    f.close()
    ruspathbool=False
except:
    ruspath=Addon.getAddonInfo('path').decode('utf-8').encode('cp1251')#myshows
    ruspathbool=True

xbmcplugin.setContent(int(sys.argv[1]), 'movies')

# load XML library
try:
    sys.path.append(os.path.join(ruspath, r'resources', r'lib'))
    from BeautifulSoup  import BeautifulSoup
    from ElementTree  import Element, SubElement, ElementTree
    import xppod
except:
    try:
        sys.path.insert(0, os.path.join(ruspath, r'resources', r'lib'))
        from BeautifulSoup  import BeautifulSoup
        from ElementTree  import Element, SubElement, ElementTree
        import xppod
    except:
        sys.path.append(os.path.join(os.getcwd(), r'resources', r'lib'))
        from BeautifulSoup  import BeautifulSoup
        from ElementTree  import Element, SubElement, ElementTree
        import xppod

import HTMLParser
hpar = HTMLParser.HTMLParser()

h = int(sys.argv[1])
icon = xbmc.translatePath(os.path.join(ruspath,'icon.png'))

def showMessage(heading, message, times = 3000):
    xbmc.executebuiltin('XBMC.Notification("%s", "%s", %s, "%s")'%(heading, message, times, icon))

def get_HTML(url, post = None, ref = None):
    html = ''

    if ref == None:
        ref = 'http://'+urlparse(url).hostname

    request = urllib2.Request(urllib.unquote(url), post)

    request.add_header('User-Agent', 'Mozilla/4.0; .NET CLR 1.1.4322; .NET CLR 2.0.50727; .NET CLR 3.0.4506.2152; .NET CLR 3.5.30729; .NET4.0C)')
    request.add_header('Host', urlparse(url).hostname)
    request.add_header('Accept', '*/*')
    request.add_header('Accept-Language', 'ru-RU')
    request.add_header('Referer', ref)
    request.add_header('Cookie', 'MG_6532=1')

    ret = 502
    idx = 5

    while ret == 502 and idx > 0:
        try:
            f = urllib2.urlopen(request)
            ret = 0
        except IOError, e:
            if hasattr(e, 'reason'):
                xbmc.log('We failed to reach a server. Reason: '+ str(e.reason))
            elif hasattr(e, 'code'):
                xbmc.log('The server couldn\'t fulfill the request. Error code: '+ str(e.code))
                ret = e.code

        if ret == 502:
            time.sleep(1)
        idx = idx -1

    if ret == 0:
        html = f.read()
        f.close()

    return html

#---------- get serials types --------------------------------------------------
def Get_Serial_Type():
    # add search to the list
    name = '[COLOR FF00FFF0]' + '[ПОИСК]' + '[/COLOR]'
    i = xbmcgui.ListItem(name, iconImage=icon, thumbnailImage=icon)
    u = sys.argv[0] + '?mode=SERIAL'
    u += '&name=%s'%urllib.quote_plus(name)
    u += '&tag=%s'%urllib.quote_plus(' ')
    xbmcplugin.addDirectoryItem(h, u, i, True)

    # add last viewed serial
    name = '[COLOR FF00FF00]'+ '[ИСТОРИЯ]' + '[/COLOR]'
    i = xbmcgui.ListItem(name, iconImage=icon, thumbnailImage=icon)
    u = sys.argv[0] + '?mode=SERIAL'
    u += '&name=%s'%urllib.quote_plus(name)
    u += '&tag=%s'%urllib.quote_plus(' ')
    xbmcplugin.addDirectoryItem(h, u, i, True)

    # add serial genres
    name = '[COLOR FFFFF000]'+ '[ЖАНРЫ]' + '[/COLOR]'
    i = xbmcgui.ListItem(name, iconImage=icon, thumbnailImage=icon)
    u = sys.argv[0] + '?mode=GENRE'
    u += '&name=%s'%urllib.quote_plus(name)
    xbmcplugin.addDirectoryItem(h, u, i, True)

    # load serials types
    tree = ElementTree()
    tree.parse(os.path.join(ruspath, r'resources', r'data', r'serials.xml'))

    for rec in tree.getroot().find('TYPES'):
            name = rec.find('name').text.encode('utf-8')
            tag  = rec.tag.encode('utf-8')
            i = xbmcgui.ListItem(name, iconImage=icon, thumbnailImage=icon)
            u = sys.argv[0] + '?mode=SERIAL'
            u += '&name=%s'%urllib.quote_plus(name)
            u += '&tag=%s'%urllib.quote_plus(tag)
            xbmcplugin.addDirectoryItem(h, u, i, True)

    xbmcplugin.endOfDirectory(h)
#-------------------------------------------------------------------------------

#---------- check history ------------------------------------------------------
def Check_History(tag):
    # try to open history
    try:
        htree = ElementTree()
        htree.parse(os.path.join(ruspath, r'resources', r'data', r'history.xml'))
        xml_h = htree.getroot()
    except:
        xbmc.log("*** HISTORY NOT FOUND ")
        return ''

    # build list of history
    try:
        part = xml_h.find(tag).find('Part').text
    except:
        part = ''

    return part.encode('utf-8')

#---------- get serials genres -------------------------------------------------
def Get_Serial_Genre():
    # load serials types
    tree = ElementTree()
    tree.parse(os.path.join(ruspath, r'resources', r'data', r'serials.xml'))

    for rec in tree.getroot().find('GENRES'):
            name = rec.find('name').text.encode('utf-8')
            tag  = rec.tag.encode('utf-8')
            i = xbmcgui.ListItem(name, iconImage=icon, thumbnailImage=icon)
            u = sys.argv[0] + '?mode=SERIAL'
            u += '&name=%s'%urllib.quote_plus('[ЖАНРЫ]')
            u += '&tag=%s'%urllib.quote_plus(tag)
            xbmcplugin.addDirectoryItem(h, u, i, True)

    xbmcplugin.endOfDirectory(h)

#---------- get serials for selected type --------------------------------------
def Get_Serial_List(params):
    s_type = urllib.unquote_plus(params['name'])
    s_tag  = urllib.unquote_plus(params['tag'])
    if s_type == None: return False

    # show search dialog
    if s_type == '[COLOR FF00FFF0]' + '[ПОИСК]' + '[/COLOR]':
        skbd = xbmc.Keyboard()
        skbd.setHeading('Поиск сериалов. Формат: name[:yyyy]')
        skbd.doModal()
        if skbd.isConfirmed():
            SearchStr = skbd.getText().split(':')
            s_name = SearchStr[0]
            if len(SearchStr) > 1:
                s_year = SearchStr[1]
            else:
                s_year = ''
        else:
            return False
        #--
        if not unicode(s_year).isnumeric() and (s_name == '' or s_year <> ''):
            xbmcgui.Dialog().ok('Ошибка поиска',
            'Неверно задан формат поиска сериала.',
            'Используйте формат: ',
            '    <поиск по имени>[:<поиск по году YYYY>]')
            return False

    # load serials types
    tree = ElementTree()
    tree.parse(os.path.join(ruspath, r'resources', r'data', r'serials.xml'))

    if s_type == '[COLOR FF00FF00]'+ '[ИСТОРИЯ]' + '[/COLOR]':
        # try to open history
        try:
            htree = ElementTree()
            htree.parse(os.path.join(ruspath, r'resources', r'data', r'history.xml'))
            xml_h = htree.getroot()
        except:
            xbmc.log("*** HISTORY NOT FOUND ")
            return False

        # build list of history
        for rec_h in xml_h:
            rec = tree.getroot().find('SERIALS').find(rec_h.tag.encode('utf-8'))
            try:
                #get serial details
                i_name      = rec_h.find('Date').text+' '+rec.find('name').text.encode('utf-8')
                try:
                    i_year = int(rec.find('year').text)
                except:
                    try:
                        i_year = int(rec.find('year').text.split('-')[0])
                    except:
                        i_year = 1900

                #get serial details
                i_image     = rec.find('img').text.encode('utf-8')
                i_url       = rec.find('url').text.encode('utf-8')
                i_director  = rec.find('director').text
                i_text      = rec.find('text').text
                i_genre     = rec.find('genre').text
                # set serial to XBMC
                i = xbmcgui.ListItem(i_name, iconImage=i_image, thumbnailImage=i_image)
                u = sys.argv[0] + '?mode=LIST'
                u += '&name=%s'%urllib.quote_plus(i_name)
                u += '&url=%s'%urllib.quote_plus(i_url)
                u += '&img=%s'%urllib.quote_plus(i_image)
                u += '&tag=%s'%urllib.quote_plus(rec.tag)
                u += '&part=%s'%urllib.quote_plus(rec_h.find('Part').text.encode('utf-8'))
                i.setInfo(type='video', infoLabels={ 'title':       i_name,
            						'year':        i_year,
            						'director':    i_director,
            						'plot':        i_text,
            						'genre':       i_genre})
                i.setProperty('fanart_image', i_image)
                xbmcplugin.addDirectoryItem(h, u, i, True)
            except:
                pass
    else:
        for rec in tree.getroot().find('SERIALS'):
            #try:
            if True:
                #get serial details
                i_name      = rec.text.encode('utf-8')
                try:
                    i_year = int(rec.find('year').text)
                except:
                    try:
                        i_year = int(rec.find('year').text.split('-')[0])
                    except:
                        i_year = 1900

                if s_type == '[ЖАНРЫ]':
                    if rec.find('genres').find(s_tag) is None:
                        continue

                elif s_type == '[COLOR FF00FFF0]' + '[ПОИСК]' + '[/COLOR]':
                    # checkout by category or name/year
                    if s_name.strip() <> '':
                        s1 = s_name.decode('utf-8').lower().strip().encode('utf-8')
                        s2 = rec.text.lower().strip().encode('utf-8')

                        if s1 not in s2:
                            #print s1.lower()+' not in '+s2 #myshows
                            continue
                        #else:#myshows
                            #print s1+' yes in '+s2 #myshows
                    if s_year <> '':
                        if int(s_year) <> i_year:
                            continue

                elif s_type == 'MYSHOWS':
                        # checkout by category or name/year
                    if s_name.strip() <> '':
                        s1 = s_name.decode('utf-8').lower().strip().encode('utf-8')
                        s2 = rec.text.lower().strip().encode('utf-8')

                        if s1 not in s2:
                            #print s1.lower()+' not in '+s2 #myshows
                            continue
                        else: #myshows
                            i_url= rec.find('url').text.encode('utf-8')
                            break
                                #print s1+' yes in '+s2 #myshows
                else:
                    if rec.find('categories').find(s_tag) is None:
                        continue

                if s_type != 'MYSHOWS':

                    #get serial details
                    i_image     = rec.find('img').text.encode('utf-8')
                    i_url       = rec.find('url').text.encode('utf-8')
                    i_director  = rec.find('director').text
                    i_text      = rec.find('text').text
                    i_genre     = rec.find('genre').text
                    # set serial to XBMC
                    i = xbmcgui.ListItem(i_name, iconImage=i_image, thumbnailImage=i_image)
                    u = sys.argv[0] + '?mode=LIST'
                    u += '&name=%s'%urllib.quote_plus(i_name)
                    u += '&url=%s'%urllib.quote_plus(i_url)
                    u += '&img=%s'%urllib.quote_plus(i_image)
                    u += '&tag=%s'%urllib.quote_plus(rec.tag)
                    u += '&part=%s'%urllib.quote_plus('-')
                    i.setInfo(type='video', infoLabels={ 'title':       i_name,
                                        'year':        i_year,
                                        'director':    i_director,
                                        'plot':        i_text,
                                        'genre':       i_genre})
                    i.setProperty('fanart_image', i_image)
                    xbmcplugin.addDirectoryItem(h, u, i, True)

                else: return urllib.quote_plus(i_url)
            #except:
                #xbmc.log('***   ERROR ')

    xbmcplugin.endOfDirectory(h)

def Get_URL(s_name):
    tree = ElementTree()
    tree.parse(os.path.join(ruspath, r'resources', r'data', r'serials.xml'))
    i_urls=[]#myshows
    i_names=[]#myshows
    myshows_setting=xbmcaddon.Addon(id='plugin.video.myshows')#myshows
    myshows_lang=myshows_setting.getLocalizedString#myshows

    for rec in tree.getroot().find('SERIALS'):
        #try:
        if True:
            #get serial details
            i_name      = rec.text.encode('utf-8')
            try:
                i_year = int(rec.find('year').text)
            except:
                try:
                    i_year = int(rec.find('year').text.split('-')[0])
                except:
                    i_year = 1900

        # checkout by category or name/year
        if s_name.strip() <> '':
            s1 = s_name.decode('utf-8').lower().strip().encode('utf-8')
            s2 = rec.text.lower().strip().encode('utf-8')#.split(' ')

            if s1 not in s2:
                #print s1.lower()+' not in '+s2 #myshows
                continue
            else: #myshows
                i_names.append(s2)
                i_urls.append(rec.find('url').text.encode('utf-8'))
                continue


    dialog = xbmcgui.Dialog()
    if  len(i_urls)==0:
        x=dialog.ok(myshows_lang(30402), myshows_lang(30407), myshows_lang(30408))
        print params['stringdata']
        xbmc.executebuiltin('xbmc.RunPlugin("plugin://plugin.video.myshows/?mode=203&myback_url=1&stringdata='+params['stringdata']+'")')
        return None
    elif len(i_urls)==1:
        i_url=i_urls[0]
    else:
        ret = dialog.select(myshows_lang(30401), i_names)
        if ret!=-1:
            i_url=i_urls[ret]
        else: return None
    return i_url



#---------- get serial ---------------------------------------------------------
def Get_Serial(params):
    myshows=False#myshows
    myshows_items=[]#myshows
    myshows_files=[]#myshows
    try:#myshows
        myshows_setting=xbmcaddon.Addon(id='plugin.video.myshows')#myshows
        myshows_lang=myshows_setting.getLocalizedString#myshows
        stringdata = urllib.unquote_plus(params['stringdata'])#myshows
        print stringdata#myshows
        if stringdata!=None:#myshows
            sdata=json.loads(stringdata)#myshows
            myshows=True#myshows
        myshowspath=myshows_setting.getAddonInfo('path')#myshows
    except: pass#myshows

    try:image  = urllib.unquote_plus(params['img'])
    except: image=None
    s_name = urllib.unquote_plus(params['name'])
    try:tag    = urllib.unquote_plus(params['tag'])
    except: tag=None
    try:h_part = Check_History(tag)
    except: h_part=None
    try:url = urllib.unquote_plus(params['url'])
    except: url=None

    if url == None:
        url=Get_URL(s_name)
    if url == None:
        return False

    #-- get serial play list & parameters  -------------------------------------
    xbmc.log("URL: "+url)
    html = get_HTML(url, None, 'http://serialu.net/media/uppod.swf')
    if html=='':
        return False

    # -- parsing web page
    html = re.compile('<body>(.+?)<\/body>', re.MULTILINE|re.DOTALL).findall(html)[0]
    soup = BeautifulSoup(html) #, fromEncoding="windows-1251")
    pl_url = ''

    is_multiseason = len(soup.findAll('object', {'type':'application/x-shockwave-flash'}))

    for rec in soup.findAll('object', {'type':'application/x-shockwave-flash'}):
        if is_multiseason > 1:
            season = rec.parent.previousSibling.previousSibling.text+r' '
        else:
            season = r''

        for par in rec.find('param', {'name':'flashvars'})['value'].split('&'):
            if par.split('=')[0] == 'pl':
                pl_url = par[3:]

        if pl_url.find('http:') == -1:
            pl_url = xppod.Decode(pl_url)

        #-- get playlist details ---------------------------------------------------
        xbmc.log("Playlist: "+pl_url)
        html = get_HTML(pl_url, None, 'http://serialu.net/media/uppod.swf')
        if html=='':
            return False

        # -- check if playlist is encoded
        if html.find('{"playlist":[') == -1:
            try:html = xppod.Decode(html).encode('utf-8').split(' or ')[1]#myshows
            except: html = xppod.Decode(html).encode('utf-8').split(' or ')[0]#myshows

        # -- parsing web page
        s_url = ''
        s_num = 0

        #fw = xbmcvfs.File('D:\\'+str(time.time())+'y.txt', 'w+') #myshows_fw
        #fw.write(html)


        for rec in re.compile('{(.+?)}', re.MULTILINE|re.DOTALL).findall(html.replace('{"playlist":[', '')):
            for par in rec.replace('"','').split(','):
                if par.split(':')[0]== 'comment':
                    name = str(s_num+1) + ' серия' #par.split(':')[1]+' '
                    if myshows:
                        myshows_name=par.strip().split(':')[1].split(' ')#myshows
                        #fw.write(str(myshows_name)) #myshows_fw
                        try:
                            n=0
                            if len(myshows_name) in (3,5):
                                n=1
                            if len(myshows_name)==n+4:#myshows
                                episodeId=int(myshows_name[n+0])#myshows
                                seasonId=int(myshows_name[n+2])#myshows
                            elif len(myshows_name)==n+2 and myshows_name[n+1] in ('\xc3\x91\xc2\x81\xc3\x90\xc2\xb5\xc3\x90\xc2\xb7\xc3\x90\xc2\xbe\xc3\x90\xc2\xbd',):#myshows
                                episodeId=int(1)#myshows
                                seasonId=int(myshows_name[n+0])#myshows
                            elif len(myshows_name)==n+2:#myshows
                                episodeId=int(myshows_name[n+0])#myshows
                                seasonId=int(sdata['seasonId'])#myshows
                            #fw.write('XXX'+str(episodeId)+' YYY '+str(seasonId)+'\n') #myshows_fw
                        except: continue

                if par.split(':')[0]== 'file':
                    if 'http' in par.split(':')[1]:
                        s_url = par.split(':')[1]+':'+par.split(':')[2]
                        #fw.write(str(par.split(':'))) #myshows_fw
                        #xbmc.sleep(2)
                    else:
                        if not myshows:
                            s_url = xppod.Decode(par.split(':')[1]).split(' or ')[1]
                        else:
                            if sdata['id']==None:
                                s_url = xppod.Decode(par.split(':')[1]).split(' or ')[1]#myshows
                            elif sdata['seasonId']==seasonId and sdata['episodeId']==episodeId:
                                dialog = xbmcgui.Dialog()
                                ret = dialog.select(myshows_lang(30401), xppod.Decode(par.split(':')[1]).split(' or '))
                                s_url=xppod.Decode(par.split(':')[1]).split(' or ')[ret]#myshows
                        #fw.write('XXX'+str(s_num+1)+' - '+xppod.Decode(par.split(':')[1]).split(' or ')[1]+'\n') #myshows_fw
                        #xbmc.sleep(2)

            s_num += 1
            #print urllib.unquote(s_url)
            # mark part for history
            name = season.encode('utf-8') + name
            if h_part <> '-':
                if name == h_part:
                    name = '[COLOR FF00FF00]'+name+'[/COLOR]'
            if not myshows:
                i = xbmcgui.ListItem(name, iconImage=image, thumbnailImage=image)
                u = sys.argv[0] + '?mode=PLAY'
                u += '&name=%s'%urllib.quote_plus(name)
                u += '&url=%s'%urllib.quote_plus(s_url)
                u += '&serial=%s'%urllib.quote_plus(s_name)
                u += '&serial_tag=%s'%urllib.quote_plus(tag)
                u += '&serial_url=%s'%urllib.quote_plus(url)
                u += '&img=%s'%urllib.quote_plus(image)
                u += '&pl_url=%s'%urllib.quote_plus(pl_url)
                u += '&pl_pos=%s'%urllib.quote_plus(str(s_num))

                ##print urllib.unquote_plus(u)
                #myshows
                i.setProperty('IsPlayable', 'true')
                xbmcplugin.addDirectoryItem(h, u, i, False)
                #print(u)
            else:#myshows
                myshows_items.append('S%sE%s'%(str(episodeId),str(seasonId)))#myshows
                if not sdata['id']:
                    sdata['episodeId']=str(episodeId)
                    sdata['seasonId']=str(seasonId)
                sys_url='{"filename":"%s", "showId":%s, "seasonId":%s, "episodeId":%s}' % (urllib.quote_plus(s_url), sdata['showId'], sdata['seasonId'], sdata['episodeId'])
                if sdata['id']==None:
                    myshows_files.append(sys_url)#myshows
                elif sdata['seasonId']==seasonId and sdata['episodeId']==episodeId:
                    myshows_files.append(sys_url)

    #fw.close() #myshows_fw
    if myshows:
        fw = xbmcvfs.File(os.path.join(myshowspath, 'tmp','serialu_'+str(sdata['showId'])+'.txt'), 'w')
        fw.write(str(myshows_files))
        fw.close()
        xbmc.executebuiltin('xbmc.RunPlugin("plugin://plugin.video.myshows/?mode=3012&stringdata='+urllib.quote_plus(stringdata)+'")')
    else:
        xbmcplugin.endOfDirectory(h, True)

#-------------------------------------------------------------------------------

def Get_Play_List(pl_url, pos, img):

    # create play list
    pl=xbmc.PlayList(1)
    pl.clear()

    #-- get playlist details ---------------------------------------------------
    html = get_HTML(pl_url, None, 'http://serialu.net/media/uppod.swf')
    if html=='':
        return pl

    # -- check if playlist is encoded
    if html.find('{"playlist":[') == -1:
        html = xppod.Decode(html).encode('utf-8')

    # -- parsing web page
    s_url = ''
    s_num = 0
    for rec in re.compile('{(.+?)}', re.MULTILINE|re.DOTALL).findall(html.replace('{"playlist":[', '')):
        for par in rec.replace('"','').split(','):
            if par.split(':')[0]== 'comment':
                name = str(s_num+1) + ' серия' #par.split(':')[1]+' '
            if par.split(':')[0]== 'file':
                if 'http' in par.split(':')[1]:
                    s_url = par.split(':')[1]+':'+par.split(':')[2]
                else:
                    s_url = xppod.Decode(par.split(':')[1]).split(' or ')[1]
        s_num += 1

        if s_num >= pos :
            i = xbmcgui.ListItem(name, path = urllib.unquote(s_url), thumbnailImage=img)
            pl.add(s_url, i)

    return pl
#-------------------------------------------------------------------------------

def PLAY(params):
    # -- parameters
    url         = urllib.unquote_plus(params['url'])
    img         = urllib.unquote_plus(params['img'])
    serial      = urllib.unquote_plus(params['serial'])
    tag         = urllib.unquote_plus(params['serial_tag'])
    serial_url  = urllib.unquote_plus(params['serial_url'])
    name        = urllib.unquote_plus(params['name'])
    pl_url      = urllib.unquote_plus(params['pl_url'])
    pl_pos      = int(urllib.unquote_plus(params['pl_pos']))

    # -- if requested continious play
    if Addon.getSetting('continue_play') == 'true':
        pl=Get_Play_List(pl_url, pl_pos, img)
        #xbmc.Player().play(pl)
        xbmcplugin.setResolvedUrl(h, True, pl[0])
    # -- play only selected item
    else:
        if url.find('http:') == -1:
                url = xppod.Decode(url)

        i = xbmcgui.ListItem(name, path = urllib.unquote(url), thumbnailImage=img)
        xbmc.Player().play(url, i)
        xbmcplugin.setResolvedUrl(h, True, i)

    # -- save view history -----------------------------------------------------
    Save_Last_Serial_Info(tag, serial, serial_url, img, name)
#-------------------------------------------------------------------------------

def Save_Last_Serial_Info(tag, serial, serial_url, img, part):
    # get max history lenght
    try:
        max_history = (1, 5, 10, 20, 30, 50)[int(Addon.getSetting('history_len'))]
        #xbmc.log("*** HISTORY LEN: "+ str(max_history))
        if max_history > 99:
            max_history = 99
    except:
        max_history = 10

    sdate = today = date.today().isoformat()

    # load or create history file
    try:
        tree = ElementTree()
        tree.parse(os.path.join(ruspath, r'resources', r'data', r'history.xml'))
        xml1 = tree.getroot()
    except:
        # create XML structure
        xml1 = Element("SERIALU_NET_HISTORY")

    # shrink history to limit
    if len(xml1) > max_history:
        idx = 1
        for rec in xml1:
            if idx >= max_history:
                xml1.remove(rec)
            idx = idx + 1

    # format name
    if part.find('[/COLOR]') > -1:
        part = re.compile('[COLOR FF00FF00](.+?)[/COLOR]', re.MULTILINE|re.DOTALL).find(part)

    xml_hist = None
    # update sequince number for history records
    for rec in xml1:
        if rec.tag == tag:
            rec.find("ID").text = str(0).zfill(2)
            xml_hist = rec
        else:
            rec.find("ID").text = str(int(rec.find("ID").text)+1).zfill(2)

    if xml_hist == None:
        xml_hist = SubElement(xml1, tag)
        SubElement(xml_hist, "ID").text     = str(0).zfill(2)
        SubElement(xml_hist, "Serial").text = unescape(serial)
        SubElement(xml_hist, "URL").text    = serial_url
        SubElement(xml_hist, "Date").text   = sdate
        SubElement(xml_hist, "Part").text   = unescape(part)
        SubElement(xml_hist, "Image").text  = img
    else:
        xml_hist.find("Part").text   = unescape(part)
        xml_hist.find("Date").text   = sdate

    # sort history by IDs
    xml1[:] = sorted(xml1, key=getkey)

    ElementTree(xml1).write(os.path.join(ruspath, r'resources', r'data', r'history.xml'), encoding='utf-8')

def getkey(elem):
    return elem.findtext("ID")

def unescape(text):
    try:
        text = hpar.unescape(text)
    except:
        text = hpar.unescape(text.decode('utf8'))

    try:
        text = unicode(text, 'utf-8')
    except:
        text = text

    return text

#-------------------------------------------------------------------------------
def get_params(paramstring):
	param=[]
	if len(paramstring)>=2:
		params=paramstring
		cleanedparams=params.replace('?','')
		if (params[len(params)-1]=='/'):
			params=params[0:len(params)-2]
		pairsofparams=cleanedparams.split('&')
		param={}
		for i in range(len(pairsofparams)):
			splitparams={}
			splitparams=pairsofparams[i].split('=')
			if (len(splitparams))==2:
				param[splitparams[0]]=splitparams[1]
	return param
#-------------------------------------------------------------------------------
params=get_params(sys.argv[2])

mode = None

try:
	mode = urllib.unquote_plus(params['mode'])
except:
    Get_Serial_Type()

if mode == 'SERIAL':
	Get_Serial_List(params)
elif mode == 'GENRE':
    Get_Serial_Genre()
elif mode == 'LIST':
    Get_Serial(params)
elif mode == 'PLAY':
	PLAY(params)
