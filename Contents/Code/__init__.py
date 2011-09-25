import re, urllib

WEB_ROOT = 'http://www.sesamestreet.org'
SEARCH_PAGE = 'http://www.sesamestreet.org/browseallvideos?p_p_id=browsegpv_WAR_browsegpvportlet&p_p_lifecycle=1&p_p_state=normal&p_p_mode=view'
CACHE_INTERVAL = 3600 * 6

####################################################################################################
def Start():
  Plugin.AddPrefixHandler("/video/sesameStreet", MainMenu, 'Sesame Street', 'icon-default.jpg', 'art-default.jpg')
  Plugin.AddViewGroup("Details", viewMode="InfoList", mediaType="items")
  MediaContainer.title1 = 'Sesame Street'
  MediaContainer.content = 'Items'
  MediaContainer.art = R('art-default.jpg')
  DirectoryItem.thumb = R("icon-default.jpg")
  HTTP.SetCacheTime(CACHE_INTERVAL)

####################################################################################################
def MainMenu():
  dir = MediaContainer()
  dir.Append(Function(DirectoryItem(Browse, title="By Subject"), url=WEB_ROOT+'/browsevideosbysubject', title='By Subject'))
  dir.Append(Function(DirectoryItem(Browse, title="By Theme"), url=WEB_ROOT+'/browsevideosbytheme', title='By Theme'))
  dir.Append(Function(DirectoryItem(Browse, title="By Character"), url=WEB_ROOT+'/browsevideosbycharacter', title='By Character'))
  dir.Append(Function(SearchDirectoryItem(Search, title=L("Search..."), prompt=L("Search for Videos"), thumb=R('search.png'))))
  return dir

####################################################################################################
def Browse(sender, url, title = None, replaceParent=False, values=None):
    page = HTML.ElementFromURL(url, cacheTime=1200, values=values)
    dir = MediaContainer(title1="Sesame Street", title2=title, replaceParent=replaceParent)
    for tag in page.xpath("//div[@class='viewby-content-display']//td | //div[@class='tile-content-display']//td"):
        if tag.xpath(".//div"):
            dir.viewGroup='Details'
            dir.Append(CreateVideo(tag))            
        else:
            if XML.StringFromElement(tag) != "<td></td>":
              dir.Append(CreateCategory(tag))

            
    AddPager(page, dir, title)  
    
    return dir
    
####################################################################################################
def CreateVideo(tag):
    url = tag.xpath(".//a")[0].get('href')
    if url.find('http:') < 0:
          url = WEB_ROOT+'/'+url
    title = tag.xpath(".//h4//span")[0].text
    return WebVideoItem(url, title, thumb=GetThumb(tag), summary=GetSummary(tag), subtitle=GetSubtitle(tag))

####################################################################################################
def CreateCategory(tag):
    Log(XML.StringFromElement(tag))
    url = tag.xpath("./a")[0].get('href')
	# http://www.sesamestreet.org/browseallvideos?p_p_id=browsegpv_WAR_browsegpvportlet&p_p_lifecycle=1&p_p_state=normal&p_p_mode=view&p_p_col_id=column-2&p_p_col_count=1&_browsegpv_WAR_browsegpvportlet_elementType=subject&_browsegpv_WAR_browsegpvportlet_subject=Alphabet+%2F+Letters
    #urlParts = re.match("doSearch\('([^']*)','([^']*)", url)
    #url = urlParts.group(1) + urllib.quote_plus(urlParts.group(2))

    index = url.rfind('=')
    title = urllib.unquote(url[index+1:]).replace("+", " ")
    if url.find('http:') < 0:
         url = WEB_ROOT+'/'+url
    return Function(DirectoryItem(Browse, title=title), url=url, title=title)


####################################################################################################    
def GetThumb(tag):
    thumb = WEB_ROOT+tag.xpath(".//div[@class='thumb-image']/a/img")[0].get('src')
    if thumb.find('http:') < 0:
        thumb = WEB_ROOT+'/'+thumb
    return thumb

####################################################################################################    
def GetSubtitle(tag):
    try:
      return tag.xpath(".//div[@class='subject']")[0].text.replace('Subject: ','')
    except:
      return ""

####################################################################################################    
def GetSummary(tag):
    try:
      list = [text for text in tag.xpath(".//div[@class='description']")[0].itertext()]
      Log(list)
      if len(list) > 2:
        return list[2].strip()
    except:
      raise
    
####################################################################################################    
def AddPager(page, dir, pageTitle):
    next = page.xpath("//div[@class='pagination']//span[@class='current']/following-sibling::a")
    if next:
        next = next[0]
        url = next.get('href')
        dir.Append(Function(DirectoryItem(Browse, title=L("Next Page...")), url=url, title=pageTitle, replaceParent=True))
    prev = page.xpath("//div[@class='pagination']//span[@class='current']/preceding-sibling::a")
    if prev:
        prev = prev[0]
        url = prev.get('href')
        dir.Append(Function(DirectoryItem(Browse, title=L("Previous Page...")), url=url, title=pageTitle, replaceParent=True))
        
####################################################################################################
def Search(sender, query):
    #http://www.sesamestreet.org/browseallvideos?p_p_id=browsegpv_WAR_browsegpvportlet&p_p_lifecycle=1&p_p_state=normal&p_p_mode=view&_browsegpv_WAR_browsegpvportlet_keywords=elmo+world
    return Browse(sender, SEARCH_PAGE, title="Search Results", values={"_browsegpv_WAR_browsegpvportlet_keywords":query})