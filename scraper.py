import re
from urllib.parse import urlparse, urldefrag
from bs4 import BeautifulSoup


UNIQUE_LINKS = set()
UL = 0
UNIQUE_SUBDOMAINS = set()


def scraper(url, resp):
    
    links = extract_next_links(url, resp)
    print(link for link in links if is_valid(link))
    return [link for link in links if is_valid(link)]


def extract_next_links(url, resp):

    # url: the URL that was used to get the page
    # resp.url: the actual url of the page
    # resp.status: the status code returned by the server. 200 is OK, you got the page. Other numbers mean that there was some kind of problem.
    # resp.error: when status is not 200, you can check the error here, if needed.
    # resp.raw_response: this is where the page actually is. More specifically, the raw_response has two parts:
    #         resp.raw_response.url: the url, again
    #         resp.raw_response.content: the content of the page!
    # Return a list with the hyperlinks (as strings) scrapped from resp.raw_response.content

    
    if not is_valid(url) or resp.status != 200:
        return []
    
    html_doc = resp.raw_response.content
    soup = BeautifulSoup(html_doc, 'html.parser')
    
    print(url)
    
    linksSet = set()
    
    # <a> is a tag for hyperlinks
    # Get all links that are found in the current page 
    for link in soup.find_all('a'):
        
        # Add url with fragments deleted to the set
        l = urldefrag(link.get('href'))[0]
        linksSet.add(l)
        UNIQUE_LINKS.add(l)
        global UL
        UL += 1
        parsed = urlparse(l)
        UNIQUE_SUBDOMAINS.add(parsed.netloc)

    for link in linksSet:
        UNIQUE_LINKS.add(link)
        
    return list(linksSet)



def is_valid(url):
    
    # Decide whether to crawl this url or not. 
    # If you decide to crawl it, return True; otherwise return False.
    # There are already some conditions that return False.
    
    # Scope: Only crawl the page that belong in the domain in VALID_DOMAINS
    VALID_DOMAINS = {'ics.uci.edu','cs.uci.edu','informatics.uci.edu','stat.uci.edu'}
    domainFlag = False
    
    try:
        parsed = urlparse(url)
        if parsed.scheme not in set(["http", "https"]):
            return False
        
        
        '''
        Filter out websites with low textual content or low-valued texts.
        '''
        
        # Filter out spam comments in evoke.ics.uci.edu
        if "#comment" in url:
            return False
        if "replytocom" in url:
            return False
        
        # Share query only leads to social media website to share the content. No content added.
        if "?share=" in url:
            return False
        
        # Don't crawl if it is a pdf file in /file path (not .pdf)
        if "pdf" in url:
            return False
        
        # Don't crawl if the site requires logging in.
        if "login" in url:
            return False
        
        # What to do with wics calendar? Too many blank pages with no actual data.
        # Ex. https://wics.ics.uci.edu/events/2021-01-05/
        # URL ending with date means that there is no event on that date.
        if parsed.netloc == "wics.ics.uci.edu" and (re.match(r".*\d{4}-\d{2}-\d{2}/$", url) or re.match(r".*\d{4}-\d{2}/$", url)):
            return False
        
        # Amount of data in the mt-live calendar website is so low its not worth it
        # No real difference in the URL between dates that have events versus ones that don't
        if parsed.netloc == "mt-live.ics.uci.edu" and "events" in url:
            return False
        

        
        # Select only if URL is in the scope
        for domain in VALID_DOMAINS:
            if domain in parsed.netloc:
                domainFlag = True
                
        if not domainFlag:
            return False
    
        if re.match(r"#|/$", url):
            return False
        if  re.match(
            r".*\.(css|js|bmp|gif|jpe?g|ico|jpg|z"
            + r"|png|tiff?|mid|mp2|mp3|mp4|in"
            + r"|wav|avi|mov|mpeg|ram|m4v|mkv|ogg|ogv|pdf"
            + r"|ps|eps|tex|ppt|pptx|doc|docx|xls|xlsx|names"
            + r"|data|dat|exe|bz2|tar|msi|bin|7z|psd|dmg|iso"
            + r"|epub|dll|cnf|tgz|sha1|ss|scm|rkt|java"
            + r"|thmx|mso|arff|rtf|jar|csv|php"
            + r"|rm|smil|wmv|swf|wma|zip|rar|gz|py|txt|ppsx)$", parsed.query.lower()): return False

        # 1000+ pages of extremely short short personal journal-like blogs and opinions
        # Low textual content
        if parsed.netloc == "ngs.ics.uci.edu":
            return False
               
        return not re.match(
            r".*\.(css|js|bmp|gif|jpe?g|ico|jpg|z"
            + r"|png|tiff?|mid|mp2|mp3|mp4|in"
            + r"|wav|avi|mov|mpeg|ram|m4v|mkv|ogg|ogv|pdf"
            + r"|ps|eps|tex|ppt|pptx|doc|docx|xls|xlsx|names"
            + r"|data|dat|exe|bz2|tar|msi|bin|7z|psd|dmg|iso"
            + r"|epub|dll|cnf|tgz|sha1|ss|scm|rkt|java"
            + r"|thmx|mso|arff|rtf|jar|csv|php"
            + r"|rm|smil|wmv|swf|wma|zip|rar|gz|py|txt|ppsx)$", parsed.path.lower())
    
    except TypeError:
        print ("TypeError for ", parsed)
        raise
