import dominate
import sys
import json
import argparse
import os
from datetime import datetime
from dominate.tags import *

parser = argparse.ArgumentParser()
parser.add_argument("-g", "--generatebaseline", help="generates a baseline to filter", action="store_true")

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

    with open("venator.json", "rb") as f:
	    baseline = json.load(f)

    for module in data:
        for item in reversed(data[module]):
            if type(item) is dict:
                for x in reversed(item):
                    if x == "crontab":
                        if item[x].startswith("crontab: no crontab for"):
                            data[module].remove(item)

                    if type(item[x]) is str:
                        if "vmware" in item[x]:
                            print("Filtered VMWare from " + module)

                            try:
                                data[module].remove(item)
                            except:
                                pass
                    elif x == "id":
                        for baselineitem in baseline[module]:
                            #print(baselineitem["id"])
                            pass
                    else:
                        for item in data[module]:
                            for key in item:
                                if "vmware" in str(item[key]):
                                    print("Filtered VMWare from " + module)
                                    data[module].remove(item)
                                if type(item[key]) is dict:
                                    for nextkey in item[key]:
                                        if "vmware" in str(item[key][nextkey]):
                                            print("Filtered VMWare from " + module)
                                            data[module].remove(item)
                                #else:

                                #    pass
                                    #print(str(key) + ": " + str(item[key]))

            elif type(item) is str:
                #periodic scripts
                #gatekeeper
                #system_info
                #environemnt_variables
                #system protection

                continue
                #print(module + " is a " + str(type(module)) + " and wasn't filtered")
                #print(type(data[module]))
            else:
                print("pass")
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
    with open("test.html","w") as f:
        f.write(doc.render())


def baseline():
    print("Generating baseline...")
    os.system("sudo venator -o baseline.json")


os.chdir(sys.path[0])

if os.path.isfile("baseline.json"):

    #NEEDS TO RUN WHEN TESTING
    #os.system("sudo venator -o venator.json")


    with open("venator.json", "rb") as f:
	    data = json.load(f)
    output(filter(data))
else:
    if args.generatebaseline:
        baseline()
    else:
        print("Please generate a baseline first using the -g flag ")

