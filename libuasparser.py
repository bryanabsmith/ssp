# OS X (10.11.1), Chrome 47.0.2526.27: Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/47.0.2526.27 Safari/537.36

def browser_search(uas):
    browList = ["Version", "Chrome", "Firefox", "Edge", "Trident", "MSIE"] # "Version" is Safari, "Trident" is IE11
    brow = ""
    for x in browList: # Find the browser that we're looking at here.
        if uas.find(x) > -1:
            if x == "Version":
                brow = "Safari"
            else:
                brow = x

    for uasPart in uas.split():
        if uasPart.find(brow) > -1:
            browser = uasPart.split("/")
            if browser[0] == "MSIE":
                ieVersion = uas.split().index("MSIE")
                return(["Internet Explorer", uas.split()[ieVersion+1].strip(";")])
            elif browser[0] == "Trident":
                verLocation = uas.find("rv:")
                return("Internet Explorer", uas[53:57])
            else:
                return(uasPart.split("/"))

def os_search(uas):
    osList = ["Mac", "Linux", "Windows"]
    os = ""
    for x in osList:
        if uas.find(x) > -1:
            os = x

    for uasPart in uas.split():
        if os == "Mac":
            #if uasPart.find(os) > -1:
            uas_string = uas.split()
            macIndex = uas_string.index("(Macintosh;") # http://stackoverflow.com/a/176921
            return([uas_string[macIndex+3] + " " + uas_string[macIndex+4], uas_string[macIndex+5].replace("_", ".").strip(")")])
        if os == "Linux":
            uas_string = uas.split()
            linuxIndex = uas_string.index("Linux") # http://stackoverflow.com/a/176921
            return([uas_string[linuxIndex], uas_string[linuxIndex+1]])
        if os == "Windows":
            uas_string = uas.split()
            windowsIndex = uas_string.index("(Windows") # http://stackoverflow.com/a/176921
            return([uas_string[windowsIndex].strip("(") + " " + uas_string[windowsIndex+1], uas_string[windowsIndex+2].strip(";")])

#print("Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_1) AppleWebKit/601.2.7 (KHTML, like Gecko) Version/9.0.1 Safari/601.2.7".split())
#print(browSearch("Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_1) AppleWebKit/601.2.7 (KHTML, like Gecko) Version/9.0.1 Safari/601.2.7"))
print(browser_search("Mozilla/5.0 (compatible; MSIE 10.6; Windows NT 6.1; Trident/5.0; InfoPath.2; SLCC1; .NET CLR 3.0.4506.2152; .NET CLR 3.5.30729; .NET CLR 2.0.50727) 3gpp-gba UNTRUSTED/1.0"))
#print(os_search("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/47.0.2526.16 Safari/537.36"))
