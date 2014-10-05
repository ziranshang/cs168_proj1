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
        
        self.next_hop_to_destination = {} # maps destination => next hop, update if shorter distance found with routing update
        self.distance_to_destination = {} # maps next hops => distance to destination through hop, compare for shorter distance with routing update
        
        #pass

    def handle_rx (self, packet, port):
        # Add your code here!
        #raise NotImplementedError
            
        if isinstance(packet, DiscoveryPacket):
            self.handle_discovery_packet(packet, port)
        elif isinstance(packet, RoutingUpdate):
            self.handle_routing_update(packet, port)
        else:
            destination = packet.dst
            self.send(packet, self.next_hop_to_destination[destination], False) #send to next hop on way to destination

    def handle_discovery_packet(self, packet, port):
        
        
        pass
    
    def handle_routing_update(self, packet, port):
        updated_paths = packet.paths
        
        for destination in updated_paths:
            distance = updated_paths[destination]
            if not destination in self.next_hop_to_destination.keys():
                self.next_hop_to_destination[destination] = port
                
                
    