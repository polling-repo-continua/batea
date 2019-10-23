# batea: context-driven asset ranking using anomaly detection
# Copyright (C) 2019-  Delve Labs inc.
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301, USA.

from .feature import FeatureBase
from collections import Counter
import numpy as np


class IpOctetFeature(FeatureBase):

    def __init__(self, octet):
        self.octet = octet
        super().__init__(name=f"ip_octet_{octet}")

    def _transform(self, hosts):
        f = lambda x: int(x.ipv4.exploded.split('.')[self.octet])
        return f


class TotalPortCountFeature(FeatureBase):

    def __init__(self):
        super().__init__(name="port_count")

    def _transform(self, hosts):
        f = lambda x: len(x.ports)
        return f


class OpenPortCountFeature(FeatureBase):

    def __init__(self):
        super().__init__(name="open_port_count")

    def _transform(self, hosts):
        f = lambda x: len([port for port in x.ports if port.state == 'open'])
        return f


class LowPortCountFeature(FeatureBase):

    def __init__(self):
        super().__init__(name="low_port_count")

    def _transform(self, hosts):
        f = lambda x: len([port for port in x.ports if port.state == 'open' and port.port <= 9999])
        return f


class TCPPortCountFeature(FeatureBase):

    def __init__(self):
        super().__init__(name="tcp_port_count")

    def _transform(self, hosts):
        f = lambda x: len([port for port in x.ports if port.state == 'open' and port.protocol == 'tcp'])
        return f


class NamedServiceCountFeature(FeatureBase):

    def __init__(self):
        super().__init__(name="named_service_count")

    def _transform(self, hosts):
        f = lambda x: len([port for port in x.ports if port.service != "unknown"])
        return f


class BannerCountFeature(FeatureBase):

    def __init__(self):
        super().__init__(name="software_banner_count")

    def _transform(self, hosts):
        f = lambda x: len([port for port in x.ports if port.software])
        return f


class MaxBannerLengthFeature(FeatureBase):

    def __init__(self):
        super().__init__(name="max_banner_length")

    def _transform(self, hosts):
        f = lambda x: max([port.get_banner_length() for port in x.ports], default=0)
        return f


class WindowsOSFeature(FeatureBase):
    def __init__(self):
        super().__init__(name="is_windows")

    def _transform(self, hosts):
        f = lambda x: 1 if x.os_info is not None and 'windows' in x.os_info.get('name', '').lower() else 0
        return f


class LinuxOSFeature(FeatureBase):
    def __init__(self):
        super().__init__(name="is_linux")

    def _transform(self, hosts):
        f = lambda x: 1 if x.os_info is not None and 'linux' in x.os_info.get('name', '').lower() else 0
        return f


class HttpServerCountFeature(FeatureBase):
    def __init__(self):
        super().__init__(name="http_server_count")

    def _transform(self, hosts):
        f = lambda x: len([port for port in x.ports if 'http' in port.service])
        return f


class DatabaseCountFeature(FeatureBase):
    def __init__(self):
        super().__init__(name="database_count")

    def _transform(self, hosts):
        db_ports = [1433, 1434, 3306, 5432, 1521, 1830, 9200, 9300, 7000, 7001, 9042, 6379, 5984]
        db_services = ['sql', 'mysql', 'mssql', 'oracle', 'elasticsearch', 'cassandra', 'mongo', 'redis', 'couchdb']

        f = lambda x: len([port for port in x.ports if port.port in db_ports or port.service in db_services])
        return f


class CommonWindowsDomainAdminFeature(FeatureBase):
    def __init__(self):
        super().__init__(name="windows_domain_admin_count")

    def _transform(self, hosts):
        admin_ports = [53, 88, 389, 636, 445]
        f = lambda x: len([port for port in x.ports if port.port in admin_ports])
        return f


class CommonWindowsDomainMemberFeature(FeatureBase):
    def __init__(self):
        super().__init__(name="windows_domain_member_count")

    def _transform(self, hosts):
        member_ports = [25, 135, 137, 139, 3268, 3269]
        f = lambda x: len([port for port in x.ports if port.port in member_ports])
        return f


class PortEntropyFeature(FeatureBase):
    def __init__(self):
        super().__init__(name="port_entropy")

    def _transform(self, hosts):
        port_list = [port.port for host in hosts for port in host.ports]
        frequency = Counter(port_list)
        total = len(port_list)
        f = lambda x: -sum([(frequency[p.port]/total)*np.log2(frequency[p.port]/total) for p in x.ports])
        return f


class HostnameLengthFeature(FeatureBase):
        def __init__(self):
            super().__init__(name="hostname_length")

        def _transform(self, hosts):
            f = lambda x: len(x.hostname) if x.hostname is not None else 0
            return f


class HostnameEntropyFeature(FeatureBase):
    def __init__(self):
        super().__init__(name="hostname_entropy")

    def _transform(self, hosts):
        char_list = []
        hostname_chars = [list(host.hostname) if host.hostname is not None else '' for host in hosts]
        for hostname in hostname_chars:
            char_list.extend(hostname)
        frequency = Counter(char_list)
        total = len(char_list)

        f = lambda x: -sum([(frequency[c]/total)*np.log2(frequency[c]/total) for c in x.hostname or ''])
        return f
