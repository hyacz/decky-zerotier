import { FaRegSquareCheck, FaRegSquare, FaRegSquareMinus, FaGear } from 'react-icons/fa6';

import { Network } from '../services/zerotier';
import { DialogButton, Field } from '@decky/ui';

const NetworkStatusIcon: React.FC<{ status: string }> = ({ status }) => {
  const size = 20;

  switch (status) {
    case 'OK':
      return <FaRegSquareCheck size={size}/>;
    case 'DISCONNECTED':
      return <FaRegSquare size={size}/>;
    default:
      return <FaRegSquareMinus size={size}/>;
  }
};

const NetworkButton: React.FC<{network: Network}> = ({ network }) => {
  const name = network.name? network.name : network.status;
  return(
    <Field
      label={<>
        <style>{`.dz-network-label { padding: 0px; margin: 0px; } .dz-network-label > div:nth-of-type(2) { margin-top: 4px; }`}</style>
        <Field label={name} description={network.id} className='dz-network-label' bottomSeparator='none' />
      </>}
      icon={<NetworkStatusIcon status={network.status} />}
      childrenLayout='inline'
    >
      <DialogButton style={{ minWidth: 'unset', padding: '10px', lineHeight: '12px' }}>
        <FaGear />
      </DialogButton>
    </Field>
  )
};

export default NetworkButton;