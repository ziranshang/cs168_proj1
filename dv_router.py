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
        #record the new nextHop:
        #link up:
        if up:
            #self.log("link up")
            self.routingTable[newHop] = dict([(port, 1)])
            self.nextHops[port] = newHop
        #link down:
        else:
            #self.log("link down")
            self.handle_down(newHop, port)
        self.send_routing_update()

    def handle_down(self, newHop, port):
        for destination, portDict in self.routingTable.items():
            if port in portDict.keys():
                bestPort, bestDistance = self.get_next_hop_to_destination(destination)
                portDict[port] = self.maxHopCount + 1
                bestPort, bestDistance = self.get_next_hop_to_destination(destination)
        #self.routingTable[newHop][port] = float("inf")
        #del self.routingTable[newHop][port]
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
                elif not self.routingTable[destination][port] == distance + 1:
                    self.routingTable[destination][port] = distance + 1
                    is_updated = True
        self.routingTable[self.nextHops[port]][port] = 1
        if is_updated:
            self.send_routing_update()
                        
    def handle_forward_packet(self, packet):
        destination = packet.dst
        if destination not in self.routingTable.keys():
            #self.log("not such destination in routingTable, destination: " + destination)
            return
        if len(self.routingTable[destination].items()) == 0:
            #self.log("No ports for destination in routingTable, destination: " + destination)
            return
        if self.get_next_hop_to_destination(destination)[1] > self.maxHopCount:
            #self.log("Best Path is too long, destination: " + destination)
            return

        #self.log('destination: ' + str(destination))
        #self.log('table for destination: ' + str(self.routingTable[destination]))
        #for entry in self.routingTable[destination]:
            #if entry in self.nextHops.keys():
                #self.log('port: ' + str(entry) + ' dest: ' + str(self.nextHops[entry]))
        self.send(packet, self.get_next_hop_to_destination(destination)[0], False) #send to next hop on way to destination

    def get_next_hop_to_destination(self, destination):
        # returns the smallest (port, distance) for destination by distance
        return min(self.routingTable[destination].items(), key = lambda x: x[1])
    

    def log_routingTable(self):
        for destination, portDict in self.routingTable.items():
            for port, distance in portDict.items():
                if port in self.nextHops.keys() and not isinstance(destination, BasicHost):
                    self.log("destination, bestHop, bestDistance: " + str(destination) + ", " + str(self.nextHops[port]) + ", " + str(distance))
                    