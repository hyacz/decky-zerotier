export interface NodeStatus {
  address: string;
  online: boolean;
  version: string;
}

export interface Network {
  allowDNS: boolean;
  allowDefault: boolean;
  allowManaged: boolean;
  allowGlobal: boolean;
  assignedAddresses: string[];
  id: string;
  mac: string;
  name: string;
  portDeviceName: string;
  status: string;
  type: string;
}