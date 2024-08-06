import { FaRegSquareCheck, FaRegSquare, FaRegSquareMinus, FaGear } from 'react-icons/fa6';

import { Network } from '../model';
import { DialogButton, Field } from '@decky/ui';
const NetworkStatusIcon: React.FC<{ status: string }> = ({ status }) => {
  const size = 20;

  switch (status) {
    case 'OK':
      return <FaRegSquareCheck size={size} />;
    case 'DISCONNECTED':
      return <FaRegSquare size={size} />;
    default:
      return <FaRegSquareMinus size={size} />;
  }
};

/**
 * A React functional component that renders a network button with a status icon and a configuration button.
 *
 * @param network - The network object containing information about the network.
 * @param onClick - A callback function that will be called when the configuration button is clicked.
 *
 * @returns A React element representing the network button.
 */
const NetworkButton: React.FC<{ network: Network, onClick: () => void }> = ({ network, onClick }) => {
  const name = network.name ? network.name : network.status;

  return (
    <Field
      label={<>
        <style>{`.dz-network-label { padding: 0px; margin: 0px; } .dz-network-label > div:nth-of-type(2) { margin-top: 4px; }`}</style>
        <Field label={name} description={network.id} className='dz-network-label' bottomSeparator='none' />
      </>}
      icon={<NetworkStatusIcon status={network.status} />}
      childrenLayout='inline'
    >
      <DialogButton onClick={onClick} style={{ minWidth: 'unset', padding: '10px', lineHeight: '12px' }}>
        <FaGear />
      </DialogButton>
    </Field>
  )
};

export default NetworkButton;