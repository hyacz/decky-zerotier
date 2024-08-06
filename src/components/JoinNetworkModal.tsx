import { callable, toaster } from "@decky/api";
import { ConfirmModal, DialogBody, Focusable, TextField } from "@decky/ui";
import { Network } from "../model";
import { useState } from "react";

const JoinNetworkModal: React.FC<{ closeModal: () => void }> = ({ closeModal }) => {
  const joinNetwork = callable<[string], Network[]>("join_network");
  const [netID, setNetID] = useState<string>("abcde");
  const [bOKDisabled, setBOKDisabled] = useState<boolean>(true);

  return (
    <ConfirmModal
      strTitle="Join New Network..."
      strDescription="Please enter the 16-digit network ID to join."
      strOKButtonText="Join"
      bOKDisabled={bOKDisabled}
      onCancel={closeModal}
      onOK={() => {
        joinNetwork(netID)
        toaster.toast({ title: "Joining network...", body: netID });
        closeModal();
      }}

    >
      <DialogBody>
        <Focusable>
          <TextField
            spellCheck="false"
            onChange={(evt) => {
              setNetID(evt.target.value);
              setBOKDisabled(evt.target.value.trim().length !== 16);
            }}
          />
        </Focusable>
      </DialogBody>
    </ConfirmModal>
  )
}

export default JoinNetworkModal;