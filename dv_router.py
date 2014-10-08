from sim.api import *
from sim.basics import *

'''
Create your distance vector router in this file.
'''
class DVRouter (Entity):
    def __init__(self):
        # Add your code here!
        
        # maintain a routing table that we update when receiving a routing update
        # assign distances to destination through next hop
        # next hop => distance can be checked when receiving routing update
        # map destination => next hop to find which hop to send to when sending a packet
        
        self.routingTable = {} # {destination => {port => distance to dest through port}}
        self.nextHops = {} #key: port, value: dst
        self.maxHopCount = 50

    def handle_rx (self, packet, port):
        # Add your code here!
            
        if isinstance(packet, DiscoveryPacket):
            self.handle_discovery_packet(packet, port)
        elif isinstance(packet, RoutingUpdate):
            self.handle_routing_update(packet, port)
        else:
            self.handle_forward_packet(packet)
            
    def handle_discovery_packet(self, packet, port):
        # send routing updates to share forwarding table
        latency =  packet.latency
        up = packet.is_link_up
        newHop = packet.src
        #link up:
        if up:
            self.routingTable[newHop] = {port: 1}
            self.nextHops[port] = newHop
        #link down:
        else:
            self.handle_down(newHop, port)
        self.send_routing_update()

    def handle_down(self, newHop, port):
        for destination, portDict in self.routingTable.items():
            if port in portDict.keys():
                portDict[port] = self.maxHopCount + 1
        del self.nextHops[port]


    def send_routing_update(self):
        #send routing update to every neighbors:
        for port, dst in self.nextHops.items():
            update_packet = RoutingUpdate()
            for destination in self.routingTable.keys():
                bestPort, bestDistance = self.get_next_hop_to_destination(destination)
                #if not (bestPort == port and (not destination == self.nextHops[port])):    #split horzion:
                if not port == bestPort:
                    update_packet.add_destination(destination, bestDistance)
            self.send(update_packet, port, False)

    def handle_routing_update(self, packet, port):
        is_updated = False
        for destination in packet.all_dests():
            distance = packet.get_distance(destination)  
            if not destination in self.routingTable.keys():
                is_updated = True
                self.routingTable[destination] = {port: distance + 1}
            else:
                if not port in self.routingTable[destination].keys():   #when we had no way of going to destination through any port before
                    self.routingTable[destination][port] = distance + 1
                    is_updated = True
                else:
                    bestDistance = self.get_next_hop_to_destination(destination)[1]
                    if not self.routingTable[destination][port] == distance + 1:
                        self.routingTable[destination][port] = distance + 1
                    if bestDistance > distance + 1:
                        is_updated = True
        if is_updated:
            #self.log_hops()
            #self.log_routingTable()
            self.send_routing_update()
                        
    def handle_forward_packet(self, packet):
        destination = packet.dst
        if destination not in self.routingTable.keys():
            return
        if len(self.routingTable[destination].items()) == 0:
            return
        if self.get_next_hop_to_destination(destination)[1] > self.maxHopCount:
            return
        #self.log_hops()
        #self.log_routingTable()
        self.send(packet, self.get_next_hop_to_destination(destination)[0], False) #send to next hop on way to destination

    def get_next_hop_to_destination(self, destination):
        # returns the smallest (port, distance) for destination by distance
        return min(self.routingTable[destination].items(), key = lambda x: x[1])
    

    def log_routingTable(self):
        for destination, portDict in self.routingTable.items():
            self.log("portDict for destination: " + str(destination) + ", " + str(portDict))

    def log_hops(self):
        for port, nextHop in self.nextHops.items():
            self.log("port, nextHop: " + str(port) + ", " + str(nextHop))                    