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
        
        # {destination => {port => distance to dest through port}}
        
        self.next_hop_to_destination = {} # maps destination => next hop ports, update if shorter distance found with routing update
        self.distance_to_destination = {} # maps next hop ports => distance to destination through hop, compare for shorter distance with routing update

    def handle_rx (self, packet, port):
        # Add your code here!
            
        if isinstance(packet, DiscoveryPacket):
            self.handle_discovery_packet(packet, port)
        elif isinstance(packet, RoutingUpdate):
            self.handle_routing_update(packet, port)
        else:
            destination = packet.dst
            if len(routingTable[destination]) == 0 or self.get_next_hop_to_destination(destination)[1] > 50:
                return # drop packet if no next hops to destination or distance is too big
            
            self.send(packet, self.get_next_hop_to_destination(destination)[0], False) #send to next hop on way to destination

    def handle_discovery_packet(self, packet, port):
        # send routing updates to share forwarding table
        
        pass
    
    def handle_routing_update(self, packet, port):
        updated_paths = packet.paths
        
        for destination in updated_paths:
            distance = updated_paths[destination]
            
            if not destination in self.routingTable.keys():
                self.routingTable[destination] = {port: distance}
            else:
                self.routingTable[destination][port] = distance
                        
        self.send_routing_update()
                        
    def get_next_hop_to_destination(self, destination):
        # returns the smallest (port, distance) by distance
        return min(self.routingTable, key = lambda x: x[1])
    