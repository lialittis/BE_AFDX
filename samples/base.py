################################################################@
"""

This file is a starting base for xml network parsing.
It is provided in the scope of the AFDX Project (WoPANets Extension)
The aim of such a file it to simplify the python coding, so that students focus on Network Calculus topics.

You have to update and complete this file in order to fit all the projects requirements.
Particularly, you need to complete the Station, Switch, Edge, Flow and Target classes.

"""
################################################################@

import xml.etree.ElementTree as ET
import os.path
import sys
import random

################################################################@
""" Local classes """
################################################################@

""" Node
    The Node class is used to handle any node if the network
    It's an abstract class
"""
class Node:
    def __init__(self, name):
        self.name = name

""" Station
    The Station class is used to handle stations
"""
class Station(Node):
    def __init__(self, name, transCapacity):
        self.name = name
        self.transCapacity = transCapacity
        self.delay = 0.
        self.burst = 0.
        self.rate = 0.
        self.outCurve = [0.,0.]
    
    def isSwitch(self):
        return False

    def getParameters(self):
        self.burst = 0.
        self.rate = 0.
        for flow in flows:
            if flow.source == self.name:
                self.burst += (flow.payload + flow.overhead)*8
                self.rate += (flow.payload + flow.overhead)*8/flow.period
        #print("name :",self.name,"burst and rate are : ", self.burst, self.rate)

    def calDelay(self):
        self.delay = self.burst/self.transCapacity
        self.outCurve = [self.burst + self.rate*self.delay, self.rate]
        # print("delay and out Curve",self.delay,self.outCurve)

""" Switch
    The Switch class is used to handle switches
"""
class Switch(Node):
    def __init__(self, name, latency,transCapacity):
        self.name = name
        self.latency = latency
        self.transCapacity = transCapacity
        self.neighbors = {}
        # self.Lmax = {}

    def isSwitch(self):
        return True

    def getNeighbors(self):
        for flow in flows:
            # lmax = (flow.payload+flow.overhead)*8
            for target in flow.targets:
                for i in range(1,len(target.path)-1):
                    last = target.path[i-1]
                    current = target.path[i]
                    nxt = target.path[i+1]
                    if current == self.name:
                        if nxt not in self.neighbors.keys():
                            self.neighbors[nxt] = [last]
                            # self.lmax[nxt] = lmax
                        elif last not in self.neighbors[nxt]:
                            self.neighbors[nxt].append(last)
        #print(self.neighbors)

""" Edge
    The Edge class is used to handle edges
"""
class Edge:
    direct = 0.
    reverse = 0.
    def __init__(self, name, frm,to,transCapacity):
        self.name = name
        self.frm = frm
        self.to = to
        self.transCapacity = transCapacity
    
    def getLoadDirect(self,value):
        self.direct += value*1000 # for one second

    def getLoadReverse(self,value):
        self.reverse += value*1000 # for one second

""" Target
    The Target class is used to handle targets
"""
class Target:
    def __init__(self, flow, to):
        self.flow = flow
        self.to = to
        self.path = []
        self.delay = 0.

""" Flow
    The Flow class is used to handle flows
"""
class Flow:
    def __init__(self, name, source, payload, overhead, period):
        self.name = name
        self.source = source
        self.payload = payload
        self.overhead = overhead
        self.period = period
        self.targets = []

    def calDelay(self):
        for target in self.targets:
            #print(target.to)
            delay = 0.
            for i in range(len(target.path)-1):
                #print(i,target.path[i])
                if i == 0:
                    delay += name_to_node[self.source].delay
                    # print("source : ",self.source,"delay current:",delay)
                else:
                    node = name_to_node[target.path[i]]
                    nxt = target.path[i+1]
                    lasts = node.neighbors[nxt]
                    sum_arr_curve = [0.,0.]
                    for last in lasts:
                        # print(lasts)
                        arr_curve  = getOutCurveOfNode(name_to_node[last],node.name)
                        sum_arr_curve = [sum_arr_curve[0]+arr_curve[0],sum_arr_curve[1]+arr_curve[1]]
                        # print(sum_arr_curve)
                        if last == "A1":
                            print(sum_arr_curve[0]/node.transCapacity)
                    delay += sum_arr_curve[0]/node.transCapacity
                    # print("node: ",node.name,"delay current",delay)
            target.delay = delay

################################################################@
""" Local methods """
################################################################@
""" parseStations
    Method to parse stations
        root : the xml main root
"""
def parseStations(root):
    for station in root.findall('station'):
        default_tc = 100000000
        tc = station.get('transmission-capacity')
        if tc.endswith("Mbps"):
            default_tc = default_tc
        else:
            default_tc = float(tc)
        nodes.append (Station(station.get('name'),default_tc))

""" parseSwitches
    Method to parse switches
        root : the xml main root
"""
def parseSwitches(root):
    for sw in root.findall('switch'):
        default_tc = 100000000
        tc = sw.get('transmission-capacity')
        if tc.endswith("Mbps"):
            default_tc = default_tc
        else:
            default_tc = float(tc)
        nodes.append (Switch(sw.get('name'),float(sw.get('tech-latency'))*1e-6,default_tc))

""" parseEdges
    Method to parse edges
        root : the xml main root
"""
def parseEdges(root):
    for sw in root.findall('link'):
        default_tc = 100000000
        tc = sw.get('transmission-capacity')
        if tc.endswith("Mbps"):
            default_tc = default_tc
        else:
            default_tc = float(tc)
        edges.append (Edge(sw.get('name'),sw.get('from'),sw.get('to'),default_tc))

""" parseFlows
    Method to parse flows
        root : the xml main root
"""
def parseFlows(root):
    for sw in root.findall('flow'):
        flow = Flow (sw.get('name'),sw.get('source'),float(sw.get('max-payload')),67,float(sw.get('period'))*1e-3)
        flows.append (flow)
        for tg in sw.findall('target'):
            target = Target(flow,tg.get('name'))
            flow.targets.append(target)
            target.path.append(flow.source)
            for pt in tg.findall('path'):
                target.path.append(pt.get('node'))

""" parseNetwork
    Method to parse the whole network
        xmlFile : the path to the xml file
"""
def parseNetwork(xmlFile):
    if os.path.isfile(xmlFile):
        tree = ET.parse(xmlFile)
        root = tree.getroot()
        parseStations(root)
        parseSwitches(root)
        parseEdges(root)
        parseFlows(root)
    else:
        print("File not found: "+xmlFile)

""" traceNetwork
    Method to trace the network to the console
"""
def traceNetwork():
    print("Stations:")
    for node in nodes:
        if not node.isSwitch():
            print ("\t" + node.name)
            
    print("\nSwitches:")
    for node in nodes:
        if node.isSwitch():
            print ("\t" + node.name)
            
    print("\nEdges:")
    for edge in edges:
        print ("\t" + edge.name + ": " + edge.frm + "=>" + edge.to)
    
    print("\nFlows:")
    for flow in flows:
        print ("\t" + flow.name + ": " + flow.source + " (L=" + str(flow.payload) +", p=" + str(flow.period) + ")")
        for target in flow.targets:
            print ("\t\tTarget=" + target.to)
            for node in target.path:
                print ("\t\t\t" + node)

""" constructParameters
"""
def constructParameters():
    for node in nodes:
        if node.isSwitch() :
            node.getNeighbors()
        else:
            node.getParameters();
            node.calDelay();
        name_to_node[node.name] = node

""" getOutCurveOfNode
    Method to get the output arrive curve of node knowing its next node by a recursive way
"""
def getOutCurveOfNode(node,nxt):
    if not node.isSwitch():
        # print(node.name,node.outCurve)
        return node.outCurve # for stations
    else:
        sum_arr_curve = [0.,0.]
        lasts = node.neighbors[nxt]
        # lmax = node.lmax[nxt]
        for last in lasts:
            arr_curve = getOutCurveOfNode(name_to_node[last],node.name)
            sum_arr_curve = [sum_arr_curve[0]+arr_curve[0],sum_arr_curve[1]+arr_curve[1]]

        # print(sum_arr_curve)
        delay = sum_arr_curve[0]/node.transCapacity
        # print(delay)
        out_arr_curve = [sum_arr_curve[0]+sum_arr_curve[1]*delay,sum_arr_curve[1]]
        # print(node.name,out_arr_curve)
        return out_arr_curve
    
""" calculate EndToEnd Delay
    Method to calculate end-to-end delay
"""
def calculateEED():
    for flow in flows:
        flow.calDelay()

""" findEdge
    Method to find edge by the from and to
"""
def findEdge(frm,to):
    for edge in edges:
        if edge.frm == frm and edge.to == to:
            return edge,True
        elif edge.frm == to and edge.to == frm:
            return edge,False
        else:
            continue

def calculPercent(value,total):
    return '{:.2%}'.format(value/total)

""" calculateLoadForEdges
    Method to calculate loads for each edges;
"""
def calculateLoadForEdges():
    for flow in flows:
        loadedEdgesD = []
        loadedEdgesR = []
        for target in flow.targets:
            for i in range(1,len(target.path)):
                edge,isDirect = findEdge(target.path[i-1],target.path[i])
                if edge not in loadedEdgesD and isDirect:
                    edge.getLoadDirect((flow.payload+flow.overhead)*8)
                    loadedEdgesD.append(edge)
                    # print(edge.name,edge.frm,edge.to,flow.name,target.path,edge.direct)
                elif edge not in loadedEdgesR and not isDirect:
                    edge.getLoadReverse((flow.payload+flow.overhead)*8)
                    loadedEdgesR.append(edge)
                    # print(edge.name,edge.frm,edge.to,flow.name,target.path,edge.reverse)
                else:
                    continue
                if edge.name == "L1":
                    print(flow.name,target.to,target.path[i-1],target.path[i],edge.reverse)

""" createFakeResultsFile
    Method to create a fake result file ; only delays are generated (random value between 40 and 80)
        xmlFile : the path to the xml (input) file
"""
def createFakeResultsFile (xmlFile):
    posDot = xmlFile.rfind('.')
    if not (posDot == -1):
        resFile = xmlFile[0:posDot]+'_res.xml'
    else:
        resFile = xmlFile+'_res.xml'
    res = open(resFile,"w")
    res.write('<?xml version="1.0" encoding="UTF-8"?>\n')
    res.write('<results>\n')
    res.write('\t<delays>\n')
    for flow in flows:
        res.write('\t\t<flow name="' + flow.name + '">\n');
        i = 0
        for target in flow.targets:
            res.write('\t\t\t<target name="' + target.to + '" value="'+("%.2f"%(target.delay*10**6))+'" />\n');
        res.write('\t\t</flow>\n')
    
    for edge in edges:
        #v = loadRes[edge.name]
        #vr = loadRes[edge.name+" Reverse"]
        res.write('\t\t<edge name="' + edge.name + '">\n')
        res.write('\t\t\t<usage type="direct" value="' + str(edge.direct/1000) + '" percent="' + calculPercent(edge.direct,edge.transCapacity)+'" />\n')
        res.write('\t\t\t<usage type="reverse" value="' + str(edge.reverse/1000) + '" percent="' + calculPercent(edge.reverse,edge.transCapacity)+'" />\n')
        res.write('\t\t</edge>\n')
    res.write('\t</delays>\n')
    res.write('</results>\n')
    res.close()
    file2output(resFile)
    
""" file2output
    Method to print a file to standard ouput
        file : the path to the xml (input) file
"""
def file2output (file):
    hFile = open(file, "r")
    for line in hFile:
        print(line.rstrip())

################################################################@
""" Global data """
################################################################@
nodes = [] # the nodes
edges = [] # the edges
flows = [] # the flows

name_to_node = {} # from name to node
################################################################@
""" Main program """
################################################################@

if len(sys.argv)>=2:
    xmlFile=sys.argv[1]
else:
    xmlFile="./ES2E_M.xml"
 
parseNetwork(xmlFile)
constructParameters()
calculateEED()
calculateLoadForEdges()
#traceNetwork()
#createFakeResultsFile(xmlFile)


