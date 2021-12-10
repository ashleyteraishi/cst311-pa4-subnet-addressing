from mininet.net import Mininet
from mininet.node import Controller, RemoteController, OVSController
from mininet.node import CPULimitedHost, Host, Node
from mininet.node import OVSKernelSwitch, UserSwitch
from mininet.node import IVSSwitch
from mininet.cli import CLI
from mininet.log import setLogLevel, info
from mininet.link import TCLink, Intf
from subprocess import call
def myNetwork():

    # allows for custom ip addresses
    net = Mininet(topo=None)

    # adds controller using the tcp protocol and port number for virtual box
    info( '*** Adding controller\n' )
    c0=net.addController(name='c0',
                      controller=Controller,
                      protocol='tcp',
                      port=6633)

    # adds switches using the OVSKernelSwitch
    info( '*** Add switches\n')
    s1 = net.addSwitch('s1', cls=OVSKernelSwitch)
    s2 = net.addSwitch('s2', cls=OVSKernelSwitch)

    # adds routers with custom ip addresses and subnet masks
    info('*** Add routers\n')
    r3 = net.addHost('r3', cls=Node, ip='10.0.5.1/24')
    r3.cmd('sysctl -w net.ipv4.ip_forward=1')
    r4 = net.addHost('r4', cls=Node, ip='192.168.1.2/30')
    r4.cmd('sysctl -w net.ipv4.ip_forward=1')
    r5 = net.addHost('r5', cls=Node, ip='10.0.6.1/24')
    r5.cmd('sysctl -w net.ipv4.ip_forward=1')

    # adds hosts with custom ip addresses and specifies a custom default route
    info( '*** Add hosts\n')
    h1 = net.addHost('h1', cls=Host, ip='10.0.5.2/24', defaultRoute='via 10.0.5.1')
    h2 = net.addHost('h2', cls=Host, ip='10.0.6.2/24', defaultRoute='via 10.0.6.1')

    # adds links and wires hardware in order
    info( '*** Add links\n')
    net.addLink(h1, s1)
    net.addLink(h2, s2)
    net.addLink(s1, r3)
    net.addLink(s2, r5)
    net.addLink(r3, r4, intfName1='r3-eth1', params1={ 'ip' : '192.168.1.1/30'},
        intfName2='r4-eth0', params2={ 'ip' : '192.168.1.2/30'} )
    net.addLink(r4, r5, intfName1='r4-eth1', params1={ 'ip' : '192.168.2.1/30'},
        intfName2='r5-eth1', params2={ 'ip' : '192.168.2.2/30'} )

    # Adds static routes
    r3.cmd('route add -net 10.0.6.0/24 gw 192.168.1.2 r3-eth1')
    r3.cmd('route add -net 192.168.2.0/30 gw 192.168.1.2 r3-eth1')
    r4.cmd('route add -net 10.0.5.0/24 gw 192.168.1.1 r4-eth0')
    r4.cmd('route add -net 10.0.6.0/24 gw 192.168.2.2 r4-eth1')
    r5.cmd('route add -net 10.0.5.0/24 gw 192.168.2.1 r5-eth1')
    r5.cmd('route add -net 192.168.1.0/30 gw 192.168.2.1 r5-eth1')

    # starts the network at the controller
    info( '*** Starting network\n')
    net.build()
    info( '*** Starting controllers\n')
    for controller in net.controllers:
        controller.start()

    # starts the switches
    info( '*** Starting switches\n')
    net.get('s1').start([c0])
    net.get('s2').start([c0])
    info( '*** Post configure switches and hosts\n')
    CLI(net)
    net.stop()
if __name__ == '__main__':
    setLogLevel( 'info' )
    myNetwork()