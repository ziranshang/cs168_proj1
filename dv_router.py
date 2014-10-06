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
            destination = packet.dst
            if destination not in self.routingTable.keys() or len(self.routingTable[destination]) == 0 or self.get_next_hop_to_destination(destination)[1] > self.maxHopCount:
                return # drop packet if no next hops to destination or distance is too big
            
            self.send(packet, self.get_next_hop_to_destination(destination)[0], False) #send to next hop on way to destination

    def handle_discovery_packet(self, packet, port):
        # send routing updates to share forwarding table
        latency =  packet.latency
        up = packet.is_link_up
        newHop = packet.src.name
        #record the new nextHop:
        #link up:
        if up:
            self.routingTable[newHop] = dict([(port, 1)])
            self.nextHops[port] = newHop
        #link down:
        else:
            self.routingTable[newHop][port] = float("inf")
            del self.nextHops[port]
        self.send_routing_update()

    def send_routing_update(self):
        #send routing update to every neighbors:
        for port, dst in self.nextHops.items():
            update_packet = RoutingUpdate()
            for destination in self.routingTable.keys():
                bestDistance = self.get_next_hop_to_destination(destination)[1]
                update_packet.add_destination(destination, bestDistance)
            self.send(update_packet, port, False)
    
    def handle_routing_update(self, packet, port):
        is_updated = False
        for destination in packet.all_dests():
            distance = packet.get_distance(destination)
            if not destination in self.routingTable.keys():
                is_updated = True
                self.routingTable[destination] = {port: distance}
            else:
                if not port in self.routingTable[destination].keys():
                    self.routingTable[destination][port] = distance + 1
                elif not self.routingTable[destination][port] == distance + 1:
                    self.routingTable[destination][port] = distance + 1
                    is_updated = True
        if is_updated:
            self.send_routing_update()
                        
    def get_next_hop_to_destination(self, destination):
        # returns the smallest (port, distance) for destination by distance
        return min(self.routingTable[destination].items(), key = lambda x: x[1])
    