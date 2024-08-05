import { FaRegSquareCheck, FaRegSquare, FaRegSquareMinus, FaGear } from 'react-icons/fa6';

import { Network } from '../services/zerotier';
import { ButtonItem } from '@decky/ui';

const NetworkStatusIcon: React.FC<{ status: string }> = ({ status }) => {
  switch (status) {
    case 'OK':
      return <FaRegSquareCheck />;
    case 'DISCONNECTED':
      return <FaRegSquare />;
    default:
      return <FaRegSquareMinus />;
  }
};

const NetworkButton: React.FC<{network: Network}> = ({ network }) => {
  return(
    <div className='network-button'>
      <ButtonItem
        label={network.name}
        icon={<NetworkStatusIcon status={network.status} />}
        description={network.id}
        layout="inline"
      >
        <FaGear />
      </ButtonItem>
    </div>
  )
};

export default NetworkButton;