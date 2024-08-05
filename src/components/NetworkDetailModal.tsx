import { callable, toaster } from "@decky/api";
import { ConfirmModal, DialogBody, DialogControlsSection, DialogControlsSectionHeader, DialogSubHeader, Focusable, TextField, ToggleField } from "@decky/ui";
import { Network } from "../services/zerotier";
import { useState } from "react";

export interface NetworkDetailModalProps {
  network: Network;
  closeModal: () => void;
}

const NetworkDetailModal: React.FC<NetworkDetailModalProps> = ({ network, closeModal }) => {
  const joinNetwork = callable<[netID: string], Network[]>("join_network");
  const disconnectNetwork = callable<[netID: string], Network[]>("disconnect_network");
  const forgetNetwork = callable<[netID: string], Network[]>("forget_network");
  const updateNetwork = callable<[netID: string, allowDNS: boolean, allowDefault: boolean, allowManaged: boolean, allowGlobal:boolean], Network[]>("update_network");

  const [net, setNet] = useState<Network>(network);

  if (net.status === "DISCONNECTED") {
    return (
      <ConfirmModal
        strTitle={net.name ? net.name : "UNKNOW NAME"}
        strOKButtonText="Connect"
        strMiddleButtonText="Forget"
        onOK={() => {
          joinNetwork(net.id);
          toaster.toast({title: "Connecting network...", body: net.id});
          closeModal();
        }}
        onMiddleButton={() => {
          forgetNetwork(net.id);
          toaster.toast({title: "Forgetting network...", body: net.id});
          closeModal();
        }}
        onCancel={closeModal}
      />
    )
  } else {
    return (
      <ConfirmModal
        strTitle={net.name ? net.name : "UNKNOW NAME"}
        strDescription="Please enter the 16-digit network ID to join."
        onCancel={closeModal}
        onOK={() => {
          updateNetwork(net.id, net.allowDNS, net.allowDefault, net.allowManaged, net.allowGlobal);
          toaster.toast({title: "Update network...", body: net.id});
          closeModal();
        }}
      >
        <DialogSubHeader>{network.id}</DialogSubHeader>
        <DialogControlsSection>
        111
        </DialogControlsSection>
        <DialogControlsSectionHeader>Settings</DialogControlsSectionHeader>
        <DialogControlsSection>
          <ToggleField label="allowDNS" checked={net.allowDNS} onChange={(evt) => setNet({...net, allowDNS: evt})} />
          <ToggleField label="allowDefault" checked={net.allowDefault} onChange={(evt) => setNet({...net, allowDefault: evt})} />
        </DialogControlsSection>
        
        
      </ConfirmModal>
    )
  }
};

export default NetworkDetailModal;