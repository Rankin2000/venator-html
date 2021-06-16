import dominate
import sys
import json
import argparse
import os
import plistlib
from datetime import datetime
from dominate.tags import *

#Arguments/Flags
parser = argparse.ArgumentParser()
parser.add_argument("-g", "--generatebaseline", help="generates a baseline to filter", action="store_true")
parser.add_argument("-f", "--filter", help="enables the filter to hide items present in the baseline", action="store_true")
args = parser.parse_args()

#Simple function to try tidy keys from json when adding to report
def tidyitem(item):
    if item == "uuid":
        return item.upper()
    elif item == "TCP_UDP":
        return item.replace("_", "/")
    elif item.endswith("id"):
        item = item.title()
        item = item.replace("_", " ")
        return item.replace("Id", "ID")
    elif "os" in item:
        return item.title().replace("Os", "OS").replace("_", " ")
    else:
        return item.replace("_", " ").title()

#Attempts to filter items from report using baseline json and some other strings
def filter(data):
    print("Filtering data from baseline")

    filtered = data

    #Gets baseline json
    with open("baseline.json", "rb") as f:
	    baseline = json.load(f)

    #Finds differences between current files and baseline files
    os.system("diff baseline.txt venator.txt | grep '>' | egrep -v 'Spotlight|DocumentRevisions|PKInstallSandboxManager|HFS+|fseventsd|TemporaryItems|Library/Logs/DiagnosticReports|Library/Updates|.Trashes|.bash_sessions|Containers/com.apple.Safari|vmware|ActivityMonitor|DiskUtility|Terminal|/Volumes/VMware Shared Folders|/Volumes/macOS SSD|dslocal|systemstats|dyld|Hyper|MacPorts|OceanLotus.H|TaskExplorer_2.0.2.zip|Venator-master.zip|_CCC SafetyNet|analysis_machine_10.14.4|ccc-5.1|Saved Application State|starttor|uuidtext|/private/var/log|/private/var/run/|private/var/db|/dev/|/usr/libexec/firmwarecheckers/eficheck|venator_output|/Volumes/Storage/' > diff.txt")

    #Loops through modules in json to filter
    for module in data:
        if type(data[module]) is list:
            for item in data[module][:]:
                for x in item:
                    #If cron job module has no crontab remove
                    if x == "crontab":
                        if item[x].startswith("crontab: no crontab for"):
                            data[module].remove(item)

                    elif type(item[x]) is str:
                        #If CFBundleIdentifier already in baseline remove
                        if x == "CFBundleIdentifier":
                            if item[x] in str(baseline[module]):
                                data[module].remove(item)
                        #If appHash already in baseline remove
                        elif x == "appHash":
                            if item[x]:
                                if item[x] in str(baseline[module]) :
                                    data[module].remove(item)
                        #If vmware in item remove
                        elif "vmware" in item[x]:
                            try:
                                print("Filtered VMWare from " + module)
                                data[module].remove(item)
                            except:
                                print("Failed to remove item. May have already been removed")
                                print(x + " - " + item[x])
                    elif x == "id":
                        ids = []
                        #Gets all IDs from baseline
                        for baselineitem in baseline[module]:
                            ids.append(baselineitem["id"])
                        #If item already in list of baseline ids remove
                        if item[x] in ids:
                            print("Filtered item from " + module)
                            data[module].remove(item)
                    else:
                        #If package_identifer already in baseline remove
                        if x == "package_identifiers":
                            for identifier in item[x]:
                                if identifier in str(baseline[module]):
                                    try:
                                        data[module].remove(item)
                                    except:
                                        print("Failed to remove item. May have already been removed")
                        #If vmware in item remove it
                        elif "vmware" in str(item[x]):
                            print("Filtered VMWare from " + module)
                            data[module].remove(item)
        elif type(data[module]) is dict:
            #If dict it covers these modules
            #Don't need to be filtered but can be in future
            #SIP
            #Variable
            #System Info
            #Gatekeeper
            #Periodic Script
            pass
    return data

#Creates HTML report
def output(data):
    doc = dominate.document(title='Venator')

    #Gets rid of empty items
    items = []
    for item in data:
        if len(data[item]) > 0:
            items.append(item)

    #Adds stylesheet link
    with doc.head:
        link(rel='stylesheet', href='style.css')

    #Document Content
    with doc:
        #Header
        h1("Venator Report")
        #Added time of report
        today = datetime.now()
        h3("Generated on " + today.strftime("%a, %d %b %Y at %H:%M:%S"), cls="right-header")

        #Sidebar
        with div(id='sidebar'):
            #Summary Header
            h3("Summary", cls="left-header")

            #Table
            with table():
                #Table header
                with thead():
                    #Row
                    with tr():
                        th("Module")
                        th("Number of Items")
                #Table body
                with tbody():
                    #For item in items create row
                    for item in items:
                        with tr():
                            #Tidy item and make it a link to a header of the same name
                            td(a(tidyitem(item), href="#" + item))
                            #Number of things in the item
                            td(len(data[item]))



        #Creates main div
        with div(id='main'):
            #For each module
            for name in items:
                #Div with id as name so sidebar can link to
                with div(id=name):
                    #Header with tidied name
                    h2(tidyitem(name))

                    #Table
                    with table():
                        #Table header
                        with thead():
                            with tr():
                                th("Item")
                                th("Value")

                        #Table body
                        with tbody():
                            #Creates row
                            with tr():
                                #For item in the module
                                for item in data[name]:
                                    #If module is dict in
                                    if type(item) is dict:
                                        #For key in dict
                                        for x in item:
                                            #Create row
                                            with tr():
                                                #Tidy key and add to row
                                                th(tidyitem(x))
                                                #If key is zsh_commands
                                                if x == "zsh_commands":
                                                    #Create list by splitting on \n
                                                    cmds = item[x].split("\n")
                                                    #Create unordered list for cmds
                                                    with td():
                                                        with ul():
                                                            for cmd in cmds:
                                                                li(cmd)

                                                #If item not empty
                                                elif item[x]:
                                                    #Add to table and convert to string
                                                    td(str(item[x]))
                                                else:
                                                    #Add N/A to row if no item
                                                    td("N/A")
                                    #if module is list
                                    elif type(data[name][item]) is list:
                                        #Create row
                                        with tr():
                                            #Tidy item
                                            th(tidyitem(item))
                                            #Create unordered list for item's list
                                            with td():
                                                with ul():
                                                    for x in data[name][item]:
                                                        li(x)

                                    #If string
                                    elif type(item) is str:
                                        #Create row
                                        with tr():
                                            #Tidy item
                                            th(tidyitem(item))
                                            #If its a key for a dict
                                            if type(data[name][item]) is dict:
                                                #Create unordered list with list items based of dict
                                                with td():
                                                    with ul():
                                                        for i in data[name][item]:
                                                            li(i + ": " + data[name][item][i])
                                            #Else just add string
                                            else:
                                                td(data[name][item])

                                    #Gap in table for easier viewing
                                    with tr(cls="break"):
                                        th(colspan=2)

            #Files dropped
            h2("Files Dropped")

            files = []
            #If filter flag
            if args.filter:
                #Files dropped is from diff.txt file
                with open("diff.txt", "r") as f:
                    files = f.read().splitlines()
            else:
                #Files droppd is from base venator.txt file
                with open("venator.txt", "r") as f:
                    files = f.read().splitlines()

            #Create unordered list for files dropped
            with ul():
                for f in files:
                    if f:
                        li(f)

    #Write html out to file
    with open("venator.html","w") as f:
        f.write(doc.render())


#Creates baseline
def baseline():
    print("Generating baseline...")
    #Gets files on system
    os.system("find / | sort > baseline.txt")

    #Runs venator
    os.system("sudo venator -o baseline.json")


#Changes working directory to python file location
os.chdir(sys.path[0])

#If generate baseline flag, generate baseline
if args.generatebaseline:
    baseline()
else:
    #Gets files on system
    os.system("find / | sort > venator.txt")
    #Runs venator
    os.system("sudo venator -o venator.json")


    #Gets venator json
    with open("venator.json", "rb") as f:
	    data = json.load(f)

    #Gets all user folders
    users = os.listdir("/Users")

    userLaunchAgents = []

    for user in users:
        try:
            #Get launchagents files from user folder
            tmpAgent = os.listdir("/Users/" + user + "/Library/LaunchAgents")

            agents = []
            for agent in tmpAgent:
                #Use plistlib to parse plist file
                with open("/Users/" + user + "/Library/LaunchAgents/" + agent, "rb") as f:
                    pl = plistlib.load(f)

                try:
                    #Append dict in similar format to venator
                    agents.append({"hostname": data["system_info"]["hostname"], "uuid": data["system_info"]["uuid"], "runAtLoad": str(bool(pl["RunAtLoad"])), "label": pl["Label"], "programExecutable": pl["Program"], "user": user,  "agent": agent})
                except:
                    #Some plist files did not have "runatload" so add without
                    agents.append({"hostname": data["system_info"]["hostname"], "uuid": data["system_info"]["uuid"], "label": pl["Label"], "programExecutable": pl["Program"], "user": user,  "agent": agent})

            userLaunchAgents.extend(agents)
        except:
            #If no files it will fail trying to open so pass
            pass

    #Add user launch agents to venator json
    data["launch_agents"].extend(userLaunchAgents)

    #if filter flag
    if args.filter:
        #If baseline already generated
        if os.path.isfile("baseline.json"):
            #Run data through filter function before output
            output(filter(data))
        else:
            #Else no baseline.json file and no flag so need to do before tool works
            print("Please generate a baseline first using the -g flag ")
    else:
        #Else output base json
        output(data)

