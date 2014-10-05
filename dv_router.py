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
        
        
        self.routingTable = {}  #key: destionation , value: key: port, value: distance to router to destionation through port.      
        self.nextHops = {} #key: port, value: dst
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
        # send routing updates to share forwarding table
        latency =  packet.latency
        up = packet.is_link_up
        newHop = packet.src.name
        #record the new nextHop:
        #link up:
        if(up):
            self.routingTable[newHop] = dict([(port, 1)])
            self.nextHop[port] = newHop
        #link down:
        else:
            self.routingTable[newHop][port] = float("inf")
            del self.nextHop[port]
        self.send_routing_update()

    def send_routing_update(self):
        #send routing update to every neighbors:
        for port, dst in self.nextHops.items():
            update_packet = RoutingUpdate(self, dst)
            for destination, portDict in self.routingTable.items():
                bestDistance = min(portDict.itervalues())
                update_packet.add_destination(destination, bestDistance)
            self.send(update_packet, port, False)

        pass
    
    def handle_routing_update(self, packet, port):
        updated_paths = packet.paths
        
        for destination in updated_paths:
            distance = updated_paths[destination]
            if not destination in self.next_hop_to_destination.keys():
                self.next_hop_to_destination[destination] = port
                self.distance_to_destination[port] = distance
            else:
                current_next_hop = self.next_hop_to_destination[destination]
                current_distance = self.distance_to_destination[current_next_hop]
                if distance < current_distance:
                    self.next_hop_to_destination[destination] = port
                    self.distance_to_destination[port] = distance
                elif distance == current_distance:
                    if port < self.next_hop_to_destination[destination]:
                        self.next_hop_to_destination[destination] = port