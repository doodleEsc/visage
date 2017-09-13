import sys
try:
    import xml.etree.cElementTree as ET
except ExceptionClass:
    import xml.etree.ElementTree as ET

import libvirt

def get_channel(uuid):
    conn = libvirt.openReadOnly()
    if not conn:
        return None
    try:
        dom = conn.lookupByUUIDString(uuid)
        xml = dom.XMLDesc()
        root = ET.fromstring(xml)
        node = root.find(".//devices/channel/[@type='unix'][2]/source")
        channel_path = node.attrib.get('path', None)
        return channel_path
    finally:
        conn.close()

