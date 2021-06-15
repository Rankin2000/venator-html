import dominate
import sys
import json
import argparse
import os
import plistlib
from datetime import datetime
from dominate.tags import *

parser = argparse.ArgumentParser()
parser.add_argument("-g", "--generatebaseline", help="generates a baseline to filter", action="store_true")
parser.add_argument("-f", "--filter", help="enables the filter to hide items present in the baseline", action="store_true")
args = parser.parse_args()


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
        name = item.replace("_", " ")
        name = name.title()
        return name

def filter(data):
    print("Filtering data from baseline")

    filtered = data

    with open("baseline.json", "rb") as f:
	    baseline = json.load(f)


    #os.system("diff baseline.txt venator.txt | grep '>' | egrep -v 'Spotlight|DocumentRevisions|PKInstallSandboxManager|HFS+|fseventsd|TemporaryItems|Library/Logs/DiagnosticReports|Library/Updates|.Trashes|.bash_sessions|Containers/com.apple.Safari|vmware|ActivityMonitor|DiskUtility|Terminal|/Volumes/VMware Shared Folders|/Volumes/macOS SSD|dslocal|systemstats|dyld|Hyper|MacPorts|OceanLotus.H|TaskExplorer_2.0.2.zip|Venator-master.zip|_CCC SafetyNet|analysis_machine_10.14.4|ccc-5.1|Saved Application State|starttor|uuidtext|/private/var/log|/private/var/run/|private/var/db|/dev/|/usr/libexec/firmwarecheckers/eficheck|venator_output|/Volumes/Storage/' | cut -c 4- >> diff.txt")

    #Previous command creates multiple lists for some reason
    os.system("diff baseline.txt venator.txt | grep '>' >> diff.txt")


    for module in data:
        if type(data[module]) is list:
            for item in data[module][:]:
                for x in item:
                    if x == "crontab":
                        if item[x].startswith("crontab: no crontab for"):
                            data[module].remove(item)

                    elif type(item[x]) is str:
                        if x == "CFBundleIdentifier":
                            if item[x] in str(baseline[module]):
                                data[module].remove(item)
                        elif x == "appHash":
                            if item[x]:
                                if item[x] in str(baseline[module]) :
                                    data[module].remove(item)

                        elif "vmware" in item[x]:
                            try:
                                print("Filtered VMWare from " + module)
            #                    print(x + " - " + item[x])
                                data[module].remove(item)
                            except:
                                print("Failed to remove item. May have already been removed")
                                print(x + " - " + item[x])
                                pass
                    elif x == "id":
                        ids = []
                        for baselineitem in baseline[module]:
                            ids.append(baselineitem["id"])
                        if item[x] in ids:
                            print("Filtered item from " + module)
                            data[module].remove(item)
                    else:
                        if x == "package_identifiers":
                            for identifier in item[x]:
                                if identifier in str(baseline[module]):
                                    try:
                                        data[module].remove(item)
                                    except:
                                        print("Failed to remove item. May have already been removed")
                                    pass

                        elif "vmware" in str(item[x]):
                            print("Filtered VMWare from " + module)
                            data[module].remove(item)
        elif type(data[module]) is dict:
            #SIP
            #Variable
            #System Info
            #gatekeeper
            #Periodic Script
            pass
        else:

            print("DIDNT DO" + str(type(data[module])))
    return data





def output(data):
    doc = dominate.document(title='Test')

    items = []
    for item in data:

        if len(data[item]) > 0:
            items.append(item)

    with doc.head:
        link(rel='stylesheet', href='style.css')

    with doc:
        h1("Venator Report")
        today = datetime.now()
        h3("Generated on " + today.strftime("%a, %d %b %Y at %H:%M:%S"), cls="right-header")
        with div(id='sidebar'):
            h3("Summary", cls="left-header")
            #for name in items:

            with table():
                with thead():
                    with tr():
                        th("Module")
                        th("Number of Items")
                with tbody():
                    for item in items:
                        with tr():
                            td(a(tidyitem(item), href="#" + item))
                            td(len(data[item]))



        with div(id='main'):
            for name in items:
                with div(id=name):
                    h2(tidyitem(name))

                    with table():
                        with thead():
                            with tr():
                                th("Item")
                                th("Value")

                        with tbody():
                            with tr():
                                for item in data[name]:
                                    if type(item) is dict:
                                        for x in item:
                                            with tr():
                                                th(tidyitem(x))
                                            #if type(item[x]) is dict:
                                            #    td(str(item[x][y]))
                                            #else:
                                                if x == "zsh_commands":
                                                    cmds = item[x].split("\n")
                                                    with td():
                                                        with ul():
                                                            for cmd in cmds:
                                                                li(cmd)

                                                elif item[x]:

                                                    td(str(item[x]))
                                                else:
                                                    td("N/A")
                                    elif type(data[name][item]) is list:
                                        with tr():
                                            th(tidyitem(item))
                                            with td():
                                                with ul():
                                                    for x in data[name][item]:
                                                        li(x)

                                    elif type(item) is str:
                                        with tr():
                                            th(tidyitem(item))
                                            if type(data[name][item]) is dict:
                                                with td():
                                                    with ul():
                                                        for i in data[name][item]:

                                                            li(i + ": " + data[name][item][i])
                                            else:
                                                td(data[name][item])


                                    with tr(cls="break"):
                                        th(colspan=2)

            h2("Files Dropped")
            files = []
            if args.filter:
                with open("diff.txt", "r") as f:
                    files = f.read().splitlines()
            else:
                with open("venator.txt", "r") as f:
                    files = f.read().splitlines()

            with ul():
                for f in files:
                    if f:
                        li(f)

    with open("test.html","w") as f:
        f.write(doc.render())


def baseline():
    print("Generating baseline...")
    os.system("find / | sort > baseline.txt")

    os.system("sudo venator -o baseline.json")


os.chdir(sys.path[0])

if os.path.isfile("baseline.json"):

    #NEEDS TO RUN WHEN TESTING
    #os.system("sudo venator -o venator.json")

    os.system("find / | sort > venator.txt")

    with open("venator.json", "rb") as f:
	    data = json.load(f)

    users = os.listdir("/Users")

    userLaunchAgents = []
    for user in users:
        try:
            tmpAgent = os.listdir("/Users/" + user + "/Library/LaunchAgents")
            agents = []
            for agent in tmpAgent:
                with ("/Users/" + user + "/Library/LaunchAgents" + agent, "rb") as f:
                    pl = plistlib.load(f)
                try:
                    agents.append({"hostname": data["system_info"]["hostnam,e"], "uuid": data["system_info"]["uuid"], "runAtLoad": str(bool(pl["RunAtLoad"])), "label": pl["Label"], "programExecutable": pl["ProgramExecutable"], "user": user,  "agent": agent})
                except:
                    agents.append({"hostname": data["system_info"]["hostnam,e"], "uuid": data["system_info"]["uuid"], "label": pl["Label"], "programExecutable": pl["ProgramExecutable"], "user": user,  "agent": agent})

            userLaunchAgents.extend(agents)
        except:
            pass

    data["launch_agents"].extend(userLaunchAgents)

    if args.filter:
        output(filter(data))
    else:
        output(data)
else:
    if args.generatebaseline:
        baseline()
    else:
        print("Please generate a baseline first using the -g flag ")

