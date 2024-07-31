import {
  ButtonItem,
  PanelSection,
  PanelSectionRow
} from "@decky/ui";

import { callable, definePlugin } from '@decky/api';

import { useEffect, useState } from "react";
import { FaRegSquare, FaRegSquareCheck, FaRegSquareMinus, FaGear } from "react-icons/fa6";

import { Network, NodeStatus } from "./services/zerotier";

const info = callable<[], NodeStatus>("info");
const listnetworks = callable<[], Network[]>("list_networks");

function Content () {
  const [counter,   setCounter  ] = useState(0);
  const [nodeState, setNodeState] = useState<NodeStatus>({address: "None" , online: false, version: 'None'});
  const [networks , setNetworks ] = useState<Network[]>([]);

  useEffect(() => {
    info().then(response => {
      setNodeState(response);
    });

    listnetworks().then(response => {
      setNetworks(response.map(network => network as Network));
    })
  }, []);

  const onClick1 = async () => {
      setCounter(counter + 1);
      listnetworks().then(response => {
        setNetworks(response.map(network => network as Network));
      })
  };

  const networksList = networks.map(network => 
    <PanelSectionRow key={network.id}>
      <ButtonItem
        label={network.name}
        icon={network.status == "OK"? <FaRegSquareCheck /> : <FaRegSquare />}
        description={network.id}
        layout="inline"
      >
        <FaGear />
      </ButtonItem>
    </PanelSectionRow>
  );

  return (
    <div>
      <PanelSection title="Service">
        <PanelSectionRow>
          {"My Address: " + nodeState.address}<br />
          {"Online: " + nodeState.online}<br />
          {"Zerotier Version: " + nodeState.version}<br />
        </PanelSectionRow>
        <PanelSectionRow>
          <ButtonItem layout="below" onClick={onClick1}> Update {counter} </ButtonItem>
        </PanelSectionRow>
      </PanelSection>
      <PanelSection title="Networks">
        {networksList}
      </PanelSection>
    </div>
  );
};

export default definePlugin(() => {

  return {
    name: "Decky ZeroTier",
    version: "0.0.1",
    content: <Content />,
    icon: <svg fill="currentColor" height="1em" width="1em" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg"><path d="M4.01 0A3.999 3.999 0 0 0 .014 4v16c0 2.209 1.79 4 3.996 4h15.98a3.998 3.998 0 0 0 3.996-4V4c0-2.209-1.79-4-3.996-4zm-.672 2.834h17.326a.568.568 0 1 1 0 1.137h-8.129c.021.059.033.123.033.19v1.804A6.06 6.06 0 0 1 18.057 12c0 3.157-2.41 5.75-5.489 6.037v2.56a.568.568 0 1 1-1.136 0v-2.56A6.061 6.061 0 0 1 5.943 12a6.06 6.06 0 0 1 5.489-6.035V4.16c0-.066.012-.13.033-.19H3.338a.568.568 0 1 1 0-1.136zm8.094 4.307A4.89 4.89 0 0 0 7.113 12a4.89 4.89 0 0 0 4.319 4.86zm1.136 0v9.718A4.892 4.892 0 0 0 16.888 12a4.892 4.892 0 0 0-4.32-4.86z"/></svg>,
  };
});
