# Demonstrates how to stop or start all services in a folder

# For Http calls
import httplib, urllib, json, time, re

# For system tools
import sys

# For reading passwords without echoing
import getpass


# Defines the entry point into the script
def main(argv=None):
    # Print some info
    print
    print "This tool is a script that stops or starts a service/s in a folder."
    print  

    # Ask for admin/publisher user name and password
    username = raw_input("Enter user name: ")
    password = getpass.getpass("Enter password: ")
    
    # Ask for server name/port
    serverName = raw_input("Enter server name: ")
    serverPort = raw_input("Enter server port: ")

    #Establish Token $ Parameters
    token = getToken(username, password, serverName, serverPort)
    params = urllib.urlencode({'token': token, 'f': 'json'})
    headers = {"Content-type": "application/x-www-form-urlencoded", "Accept": "text/plain"}

    #Get names of all folders on server
    httpConn = httplib.HTTPConnection(serverName, serverPort)
    httpConn.request("POST", "/arcgis/admin/services", params, headers)
    response = httpConn.getresponse()
    data = response.read()
    dataObj = json.loads(data)
    print "\n" + "Folders on this server:" 
    for item in dataObj['folders']:
        print item
    print "ROOT"
    print 
    #Ask for folder 
    folder = raw_input("Enter the folder name OR ""all"" to turn all services on server on/off OR reverse: ")

    #Reverses the status of the most recently adjusted services
    if str.upper(folder) == "REVERSE":
        file = open("C:\Michael\status.txt", "r")
        for line in file:
            if "." in line:
                name_split = line.split(".")
                name = name_split[0]
                svcType = line[line.find(".")+1:line.find(":")]
                status = line[line.find(":")+1:line.find(";")]
                afolder = line[line.find(";")+1:line.find("/")]
                print name + "." + svcType + ":" + status + " will be reversed"
                if str.upper(status) == "STARTED":
                    status = "stop"
                    stopOrStart = "stop"
                    httpConn = httplib.HTTPConnection(serverName, serverPort)
                    httpConn.request("POST", "/arcgis/admin/services/" + afolder + "/" + name + "." + svcType + "/" + status, params, headers)
                    response = httpConn.getresponse()
                    if (response.status != 200):
                        httpConn.close()
                        print "Error while executing stop or start. Please check the URL and try again."
                        return
                    else:
                        stopStartData = response.read()
                        # Check that data returned is not an error object
                        if not assertJsonSuccess(stopStartData):
                            if str.upper(stopOrStart) == "START":
                                print "Error returned when starting service " + name + "."
                            else:
                                print "Error returned when stopping service " + name + "."

                            print str(stopStartData)
                        else:
                            print "Service " + name + " processed successfully."
                            
                elif str.upper(status) == "STOPPED":
                    status = "start"
                    stopOrStart = "start"
                    httpConn = httplib.HTTPConnection(serverName, serverPort)
                    httpConn.request("POST", "/arcgis/admin/services/" + afolder + "/" + name + "." + svcType + "/" + status, params, headers)
                    response = httpConn.getresponse()
                    if (response.status != 200):
                        httpConn.close()
                        print "Error while executing stop or start. Please check the URL and try again."
                        return
                    else:
                        stopStartData = response.read()
                        # Check that data returned is not an error object
                        if not assertJsonSuccess(stopStartData):
                            if str.upper(stopOrStart) == "STOP":
                                print "Error returned when starting service " + name + "."
                            else:
                                print "Error returned when stopping service " + name + "."

                            print str(stopStartData)
                        else:
                            print "Service " + name + " processed successfully."
        file = open("status.txt","a")
        file.write("These services have been reversed" + "\n")
        return
                           
            
    file = open("status.txt","w")
    file.write(time.strftime("%m/%d/%y" + "\n"))
    #Turn All services on server on/off
    if str.upper(folder) == "ALL":
        stopOrStart = raw_input("Enter Start/Stop to turn all services on/off on server: ")
        httpConn = httplib.HTTPConnection(serverName, serverPort)
        httpConn.request("POST", "/arcgis/admin/services", params, headers)
        response = httpConn.getresponse()
        data = response.read()
        dataObj = json.loads(data)
        #Turn services on/off on ROOT
        for item in dataObj['services']:
            name = item['serviceName']
            svcType = item['type']
            fullserviceName = name + '.' + item['type'] 
            httpConn.request("POST", "/arcgis/admin/services/" + name + "." + svcType + "/" + stopOrStart, params, headers)
            response = httpConn.getresponse()
            if str.upper(stopOrStart) == "START":
                status = "STARTED"
                file.write(fullserviceName+":"+ status + ";" + "/" + "\n")
            elif str.upper(stopOrStart) == "STOP":
                status = "STOPPED"
                file.write(fullserviceName+":"+ status + ";" + "/" + "\n")
                
            if (response.status != 200):
                httpConn.close()
                print "Error while executing stop or start. Please check the URL and try again."
                return
            else:
                stopStartData = response.read()
                # Check that data returned is not an error object
                if not assertJsonSuccess(stopStartData):
                    if str.upper(stopOrStart) == "START":
                        print "Error returned when starting service " + name + "."
                    else:
                        print "Error returned when stopping service " + name + "."

                    print str(stopStartData)
                else:
                    print "Service " + name + " processed successfully."

        #Connect to each folder
        httpConn.request("POST", "/arcgis/admin/services", params, headers)
        response = httpConn.getresponse()
        data = response.read()
        dataObj = json.loads(data)
        for item in dataObj['foldersDetail']:
            folder = item['folderName']
            httpConn.request("POST", "/arcgis/admin/services/" + folder, params, headers)
            response = httpConn.getresponse()
            data = response.read()
            dataObj = json.loads(data)
            #Connect to each service in folder
            for item in dataObj['services']:
                name = item['serviceName']
                svcType = item['type']
                fullserviceName = name + '.' + item['type'] 
                if str.upper(stopOrStart) == "START":
                    status = "STARTED"
                    file.write(fullserviceName+":"+ status + ";" + folder + "\n")
                elif str.upper(stopOrStart) == "STOP":
                    status = "STOPPED"
                    file.write(fullserviceName+":"+ status + ";" + folder + "\n")
                stopOrStartURL = "/arcgis/admin/services/" + folder + "/" + name + "." + svcType + "/" + stopOrStart
                httpConn.request("POST", stopOrStartURL, params, headers)
                response = httpConn.getresponse()
                if (response.status != 200):
                    httpConn.close()
                    print "Error while executing stop or start. Please check the URL and try again."
                    return
                else:
                    stopStartData = response.read()
                    # Check that data returned is not an error object
                    if not assertJsonSuccess(stopStartData):
                        if str.upper(stopOrStart) == "START":
                            print "Error returned when starting service " + name + "."
                        else:
                            print "Error returned when stopping service " + name + "."
                        print str(stopStartData)
                    else:
                        print "Service " + name + " processed successfully."
                
        return
            
            

    #Get status of services in Folder
    if str.upper(folder) == "ROOT":
        folder = ""
    else:
        folder += "/"
    folderURL = "/arcgis/admin/services/" + folder
    httpConn = httplib.HTTPConnection(serverName, serverPort)
    httpConn.request("POST", folderURL, params, headers)
    response = httpConn.getresponse()
    data = response.read()
    dataObj = json.loads(data)
    print "\n" + "Services in this folder"
    for item in dataObj['services']:
        svc = item['serviceName']
        svctype = item['type']
        httpConn.close()

        #Print status of services in folder
        httpConn = httplib.HTTPConnection(serverName, serverPort)
        httpConn.request("POST", folderURL+svc+"."+ svctype, params, headers)
        response = httpConn.getresponse()
        data = response.read()
        dataObj = json.loads(data)
        status = dataObj['configuredState']
        print svc + ": " + status
    print "\n"   

    #Enter name of service to Start or Stop
    serviceName = raw_input("Enter all to Start/Stop all services or name individual service: ")

    #Start or Stop ALL services in Folder
    stopOrStart = raw_input("Enter whether you want to START or STOP the service: ")

    # Check to make sure stop/start parameter is a valid value
    if str.upper(stopOrStart) != "START" and str.upper(stopOrStart) != "STOP":
        print "Invalid STOP/START parameter entered"
        return
    
    # Get a token
    token = getToken(username, password, serverName, serverPort)
    if token == "":
        print "Could not generate a token with the username and password provided."
        return
    
    # Construct URL to read folder
    if str.upper(folder) == "ROOT":
        folder = ""
    else:
        folder += "/"
            
    folderURL = "/arcgis/admin/services/" + folder
    
    # This request only needs the token and the response formatting parameter 
    params = urllib.urlencode({'token': token, 'f': 'json'})
    
    headers = {"Content-type": "application/x-www-form-urlencoded", "Accept": "text/plain"}
    
    # Connect to URL and post parameters    
    httpConn = httplib.HTTPConnection(serverName, serverPort)
    httpConn.request("POST", folderURL, params, headers)
    
    # Read response
    response = httpConn.getresponse()
    if (response.status != 200):
        httpConn.close()
        print "Could not read folder information."
        return
    else:
        data = response.read()
        
        # Check that data returned is not an error object
        if not assertJsonSuccess(data):          
            print "Error when reading folder information. " + str(data)
        else:
            print "Processed folder information successfully. Now processing services..."

        # Deserialize response into Python object
        dataObj = json.loads(data)
        httpConn.close()
 
        # Loop through each service in the folder and stop or start it
        if str.upper(serviceName) == "ALL":
            for item in dataObj['services']:
                fullserviceName = item['serviceName'] + "." + item['type']
                if str.upper(serviceName) == "ALL":
                    if str.upper(stopOrStart) == "START":
                        status = "STARTED"
                        file.write(fullserviceName+":"+ status + ";" + folder + "\n")
                    elif str.upper(stopOrStart) == "STOP":
                        status = "STOPPED"
                        file.write(fullserviceName+":"+ status + ";" + folder + "\n")
                # Construct URL to stop or start service, then make the request
                stopOrStartURL = "/arcgis/admin/services/" + folder + fullserviceName + "/" + stopOrStart
                httpConn.request("POST", stopOrStartURL, params, headers)
                
                # Read stop or start response
                stopStartResponse = httpConn.getresponse()
                if (stopStartResponse.status != 200):
                    httpConn.close()
                    print "Error while executing stop or start. Please check the URL and try again."
                    return
                else:
                    stopStartData = stopStartResponse.read()
                
                    # Check that data returned is not an error object
                    if not assertJsonSuccess(stopStartData):
                        if str.upper(stopOrStart) == "START":
                            print "Error returned when starting service " + fullSvcName + "."
                        else:
                            print "Error returned when stopping service " + fullSvcName + "."

                        print str(stopStartData)
                    
                    else:
                        print "Service " + fullserviceName + " processed successfully."
        
            return
            
        fullserviceName = serviceName + '.' + item['type'] 

        # Get status of the service after request and write to a text file
        if str.upper(stopOrStart) == "START":
            status = "STARTED"
            file.write(fullserviceName+":"+ status + ";" + folder + "\n")
        elif str.upper(stopOrStart) == "STOP":
            status = "STOPPED"
            file.write(fullserviceName+":"+ status + ";" + folder + "\n")
        
        
        # Construct URL to stop or start service, then make the request
        stopOrStartURL = "/arcgis/admin/services/" + folder + fullserviceName + "/" + stopOrStart
        httpConn.request("POST", stopOrStartURL, params, headers)
        # Read stop or start response
        stopStartResponse = httpConn.getresponse()
        if (stopStartResponse.status != 200):
            print "Services in this Folder"
            httpConn.close()
            print "Error while executing stop or start. Please check the URL and try again."
            return
        else:
            stopStartData = stopStartResponse.read()
                
            # Check that data returned is not an error object
            if not assertJsonSuccess(stopStartData):
                if str.upper(stopOrStart) == "START":
                    print "Error returned when starting service " + fullserviceName + "."
                else:
                    print "Error returned when stopping service " + fullserviceName + "."

                print str(stopStartData)
                    
            else:
                print serviceName + " service processed successfully."

        httpConn.close()           
        
        


# A function to generate a token given username, password and the adminURL.
def getToken(username, password, serverName, serverPort):
    # Token URL is typically http://server[:port]/arcgis/admin/generateToken
    tokenURL = "/arcgis/admin/generateToken"
    
    params = urllib.urlencode({'username': username, 'password': password, 'client': 'requestip', 'f': 'json'})
    
    headers = {"Content-type": "application/x-www-form-urlencoded", "Accept": "text/plain"}
    
    # Connect to URL and post parameters
    httpConn = httplib.HTTPConnection(serverName, serverPort)
    httpConn.request("POST", tokenURL, params, headers)
    
    # Read response
    response = httpConn.getresponse()
    if (response.status != 200):
        httpConn.close()
        print "Error while fetching tokens from admin URL. Please check the URL and try again."
        return
    else:
        data = response.read()
        httpConn.close()
        
        # Check that data returned is not an error object
        if not assertJsonSuccess(data):            
            return
        
        # Extract the token from it
        token = json.loads(data)        
        return token['token']            
        

# A function that checks that the input JSON object 
#  is not an error object.
def assertJsonSuccess(data):
    obj = json.loads(data)
    if 'status' in obj and obj['status'] == "error":
        print "Error: JSON object returns an error. " + str(obj)
        return False
    else:
        return True
    
        
# Script start
if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
