import { callable } from "@decky/api";
import { ConfirmModal, DialogSubHeader, Field, ToggleField } from "@decky/ui";
import { Network } from "../model";
import { useState } from "react";

export interface NetworkDetailModalProps {
  network: Network;
  closeModal: () => void;
}

/**
 * A modal component that displays detailed information and settings for a ZeroTier network.
 *
 * @param network - The network object to display information for.
 * @param closeModal - A function to be called when the modal should be closed.
 * @returns A React functional component that renders the modal.
 */
const NetworkDetailModal: React.FC<NetworkDetailModalProps> = ({ network, closeModal }) => {
  const joinNetwork = callable<[netID: string], Network[]>("join_network");
  const disconnectNetwork = callable<[netID: string], Network[]>("disconnect_network");
  const forgetNetwork = callable<[netID: string], Network[]>("forget_network");
  const updateNetwork = callable<[netID: string, option: string, value: boolean], Network[]>("update_network");

  const [net, setNet] = useState<Network>(network);

  /**
   * Handles changes to network options and updates the network state.
   *
   * @param option - The network option to update. {allowDNS, allowDefault, allowManaged, allowGlobal}
   * @param value - The new value for the network option.
   */
  const handleOnChange = (option: string, value: boolean) => {
    setNet(prevState => ({ ...prevState, [option]: value }));
    updateNetwork(net.id, option, value);
  }

  if (net.status === "DISCONNECTED") {
    return (
      <ConfirmModal
        strTitle={net.name ? net.name : "UNKNOW NAME"}
        strOKButtonText="Connect"
        strMiddleButtonText="Forget"
        onOK={() => {
          joinNetwork(net.id);
          // toaster.toast({ title: "Connecting network...", body: net.id });
          closeModal();
        }}
        onMiddleButton={() => {
          forgetNetwork(net.id);
          // toaster.toast({ title: "Forgetting network...", body: net.id });
          closeModal();
        }}
        onCancel={closeModal}
      />
    )
  } else {
    return (
      <ConfirmModal
        strTitle={net.name ? net.name : "UNKNOW NAME"}
        strOKButtonText="Disconnect"
        onOK={() => {
          disconnectNetwork(net.id);
          closeModal();
        }}
        strCancelButtonText="Close"
        onCancel={closeModal}
      >
        <DialogSubHeader style={{ textTransform: "none" }}>
          {"Network ID: " + net.id}<br />
          {"Status: " + net.status}<br />
          {"Type: " + net.type}<br />
          {"Device: " + net.portDeviceName}<br />
          {"MAC Address: " + net.mac}
        </DialogSubHeader>
        <Field label={"Assigned Address: "} />
        {net.assignedAddresses.map(addr => <Field indentLevel={2} label={addr} />)}
        <ToggleField label="Allow Managed Address" disabled={net.status !== "OK"} checked={net.allowManaged} onChange={(val) => handleOnChange("allowManaged", val)} />
        <ToggleField label="Allow DNS Configuration" disabled={net.status !== "OK"} checked={net.allowDNS} onChange={(val) => handleOnChange("allowDNS", val)} />
        <ToggleField label="Allow Default Router Override" disabled={net.status !== "OK"} checked={net.allowDefault} onChange={(val) => handleOnChange("allowDefault", val)} />
        <ToggleField label="Allow Assignment of Global IPs" disabled={net.status !== "OK"} checked={net.allowGlobal} onChange={(val) => handleOnChange("allowGlobal", val)} />
      </ConfirmModal>
    )
  }
};

export default NetworkDetailModal;