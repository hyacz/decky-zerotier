import {
  ButtonItem,
  definePlugin,
  PanelSection,
  PanelSectionRow,
  staticClasses,
} from "@decky/ui";
import { FC, useEffect, useState } from "react";
import { FaRegSquare, FaRegSquareCheck, FaGear } from "react-icons/fa6";

import { call, callable } from '@decky/api';

import { Network, NodeStatus } from "./services/zerotier";

const response = await call<[string], NodeStatus>('apiproxy', 'info');
console.log(response);

const Content: FC = () => {
  const apiproxy = callable<[command: string], any>("apiproxy");

  const [counter,   setCounter  ] = useState(0);
  const [address,   setAddress  ] = useState<string>("None");
  const [nodeState, setNodeState] = useState<NodeStatus>({address: "None" , online: false, version: 'None'});
  const [networks , setNetworks ] = useState<Network[]>([]);

  // useEffect(() => {
  //   // 从后端获取初始数据
  //   (async () => {
  //     axios.get(ztServer + '/status', { headers: { 'X-ZT1-AUTH': await call<[], string>('authtoken') } })
  //       .then(response => {
  //         setNodeState({
  //           address: response.data.address,
  //           online: response.data.online,
  //           version: response.data.version
  //         })
  //       });
  //   })
  // }, []);

  const onClick = async () => {
      setCounter(counter + 1);
      const response = await apiproxy("info");
      console.log(response);
      setAddress(response.address)
      setNodeState({
        address: response.address,
        online: response.online,
        version: response.version
      })
  };

  const onClick2 = async () => {
    setCounter(counter + 1);
    const response = await call<[string], NodeStatus>('apiproxy', 'info');
    console.log(response);
    setAddress(response.address)
    setNodeState({
      address: response.address,
      online: response.online,
      version: response.version
    })
  };

  const onClick3 = async () => {
    setCounter(counter + 1);
    setAddress(address + "1");
  };

  return (
    <div>
      <PanelSection title="Service">
        <PanelSectionRow>
          {"My Address: " + nodeState.address + " address: " + address}
        </PanelSectionRow>
        <PanelSectionRow>
          <ButtonItem layout="below" onClick={onClick}> Update {counter} </ButtonItem>
        </PanelSectionRow>
        <PanelSectionRow>
          {"My Address: " + nodeState.address + " address: " + address}
        </PanelSectionRow>
        <PanelSectionRow>
          <ButtonItem layout="below" onClick={onClick2}> Update {counter} </ButtonItem>
        </PanelSectionRow>
        <PanelSectionRow>
          {"My Address: " + nodeState.address + " address: " + address}
        </PanelSectionRow>
        <PanelSectionRow>
          <ButtonItem layout="below" onClick={onClick3}> Update {counter} </ButtonItem>
        </PanelSectionRow>
      </PanelSection>
      <PanelSection title="Networks">
        <PanelSectionRow>
          <ButtonItem
            label="Gaming Room"
            icon={<FaRegSquare />}
            description="48d6023c467a8fd8"
            layout="inline"
          >
            <FaGear />
          </ButtonItem>
          <ButtonItem
            label="hyacz's Network"
            icon={<FaRegSquareCheck />}
            description="e5cd7a9e1c8e5527"
            layout="inline"
          >
            <FaGear />
          </ButtonItem>
        </PanelSectionRow>
      </PanelSection>
    </div>
  );
};

export default definePlugin(() => {

  return {
    title: <div className={staticClasses.Title}>Decky ZeroTier</div>,
    content: <Content />,
    icon: <svg fill="currentColor" height="1em" width="1em" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg"><path d="M4.01 0A3.999 3.999 0 0 0 .014 4v16c0 2.209 1.79 4 3.996 4h15.98a3.998 3.998 0 0 0 3.996-4V4c0-2.209-1.79-4-3.996-4zm-.672 2.834h17.326a.568.568 0 1 1 0 1.137h-8.129c.021.059.033.123.033.19v1.804A6.06 6.06 0 0 1 18.057 12c0 3.157-2.41 5.75-5.489 6.037v2.56a.568.568 0 1 1-1.136 0v-2.56A6.061 6.061 0 0 1 5.943 12a6.06 6.06 0 0 1 5.489-6.035V4.16c0-.066.012-.13.033-.19H3.338a.568.568 0 1 1 0-1.136zm8.094 4.307A4.89 4.89 0 0 0 7.113 12a4.89 4.89 0 0 0 4.319 4.86zm1.136 0v9.718A4.892 4.892 0 0 0 16.888 12a4.892 4.892 0 0 0-4.32-4.86z"/></svg>,
  };
});
