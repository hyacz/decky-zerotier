import os
import stat
import json
import asyncio
from subprocess import CalledProcessError

# The decky plugin module is located at decky-loader/plugin
# For easy intellisense checkout the decky-loader code one directory up
# or add the `decky-loader/plugin` path to `python.analysis.extraPaths` in `.vscode/settings.json`
import decky

ZT_ONE = os.path.join(decky.DECKY_PLUGIN_DIR, 'bin', 'zerotier-one')
ZT_HOME = decky.DECKY_PLUGIN_SETTINGS_DIR
ZT_NETCONF = os.path.join(ZT_HOME, 'decky_networks.json')

# Force LD_LIBRARY_PATH to include system paths for libssl
env = os.environ.copy()
env['LD_LIBRARY_PATH'] = '/usr/lib:/usr/lib64'

class Plugin:
    @staticmethod
    async def zerotier_cli(command: list[str]) -> tuple[bytes, bytes]:
        """
        Executes the ZeroTier-CLI command with the provided arguments.

        Parameters:
        command (list[str]): A list of strings representing the command and its arguments.

        Returns:
        tuple[bytes, bytes]: A tuple containing the standard output and standard error of the command.

        Raises:
        CalledProcessError: If the ZeroTier-CLI command returns a non-zero exit code.
        """
        cmd = [ZT_ONE, '-q', '-j', f'-D{ZT_HOME}', *command]

        proc = await asyncio.create_subprocess_exec(
            *cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.STDOUT,
            env=env
        )
        
        stdout, stderr = await proc.communicate()

        if proc.returncode == 0:
            decky.logger.info(' '.join(cmd))
            decky.logger.info(f'ZeroTier-CLI exited with code {proc.returncode}')
            decky.logger.info(stdout.decode('utf-8'))
        else:
            decky.logger.error(f'ZeroTier-CLI exited with code {proc.returncode}')
            decky.logger.error(stdout.decode('utf-8'))
            raise CalledProcessError(proc.returncode, cmd, stdout=stdout, stderr=stderr)

        return stdout, stderr


    @staticmethod
    async def _read_stream(stream, cb):
        """
        Reads a stream line by line and calls a callback function with each line.

        This function is designed to be used with asyncio's StreamReader objects, such as those returned by
        asyncio.subprocess.PIPE. It reads the stream line by line, decodes the bytes to a UTF-8 string, strips
        leading/trailing whitespace, and then calls the provided callback function with the decoded line.

        Parameters:
        stream (asyncio.StreamReader): The stream to read from.
        cb (callable): A function that takes a single string argument. This function will be called for each
                        line read from the stream.

        Returns:
        None
        """
        while True:
            line = await stream.readline()
            if line:
                cb(line.decode('utf-8').strip())
            else:
                break


    async def info(self) -> dict:
        """
        Retrieves information about the ZeroTier network interface.

        This function executes the ZeroTier-CLI command with the 'info' argument and returns the parsed JSON response.
        The JSON response contains various details about the ZeroTier network interface.
        {
            "address": "8ad1b*****",
            "clock": 1722903840676,
            "config": {
                "settings": {
                    "allowTcpFallbackRelay": true,
                    "forceTcpRelay": false,
                    "homeDir": "/home/deck/homebrew/settings/decky-zerotier",
                    "listeningOn": [],
                    "portMappingEnabled": true,
                    "primaryPort": 9993,
                    "secondaryPort": 28820,
                    "softwareUpdate": "disable",
                    "softwareUpdateChannel": "release",
                    "surfaceAddresses": [],
                    "tertiaryPort": 23494
                }
            },
            "online": false,
            "planetWorldId": 1496*****,
            "planetWorldTimestamp": 1644592324813,
            "publicIdentity": "8ad1b5d1a4:0:5be4396e895539bcd221491*********************************************************************************************************",
            "tcpFallbackActive": false,
            "version": "1.14.0",
            "versionBuild": 0,
            "versionMajor": 1,
            "versionMinor": 14,
            "versionRev": 0
        }

        Parameters:
        None

        Returns:
        dict: A dictionary containing the parsed JSON response from the ZeroTier-CLI 'info' command.

        Raises:
        CalledProcessError: If the ZeroTier-CLI command returns a non-zero exit code.
        """
        stdout, _ = await self.zerotier_cli(['info'])
        return json.loads(stdout.decode('utf-8'))


    async def list_networks(self) -> list[dict]:
        """
        Retrieves a list of ZeroTier networks and their configurations.

        This function executes the ZeroTier-CLI 'listnetworks' command, and merges it with the ZT_NETCONF file. 
        If the ZT_NETCONF file exists, it adds any missing networks with a 'DISCONNECTED' status.
        Finally written back to the ZT_NETCONF file.

        [{
            "allowDNS": false,
            "allowDefault": false,
            "allowGlobal": false,
            "allowManaged": true,
            "assignedAddresses": ["10.10.0.***/24"],
            "bridge": false,
            "broadcastEnabled": true,
            "dhcp": false,
            "dns": {
            "domain": "",
            "servers": []
            },
            "id": "48d6023*********",
            "mac": "da:05:ab:**:**:**",
            "mtu": 2800,
            "multicastSubscriptions": [{
                "adi": 0,
                "mac": "01:00:5e:**:**:**"
            }],
            "name": "GamingRoom",
            "netconfRevision": 20,
            "nwid": "48d6023*********",
            "portDeviceName": "ztos******",
            "portError": 0,
            "routes": [{
                "flags": 0,
                "metric": 0,
                "target": "10.10.0.0/24",
                "via": null
            }],
            "status": "OK",
            "type": "PUBLIC"
        }]

        Parameters:
        None

        Returns:
        list[dict]: A list of dictionaries, where each dictionary represents a ZeroTier network. Each dictionary
                contains the following keys: 'id', 'name', 'private', 'status', and 'routes'.

        Raises:
        CalledProcessError: If the ZeroTier-CLI command returns a non-zero exit code.
        """
        stdout, _ = await self.zerotier_cli(['listnetworks'])
        networks = json.loads(stdout.decode('utf-8'))

        if os.path.exists(ZT_NETCONF):
            with open(ZT_NETCONF, 'r') as f:
                netconf = []

                try:
                    netconf = json.load(f)
                except json.JSONDecodeError:
                    decky.logger.warning('Invalid JSON in networks conf')

                for net in netconf:
                    if net['id'] not in [n['id'] for n in networks]:
                        net['status'] = 'DISCONNECTED'
                        networks.append(net)

        with open(ZT_NETCONF, 'w') as f:
            json.dump(networks, f)
            
        return networks
    

    async def join_network(self, network_id: str) -> list[dict]:
        """
        Joins a ZeroTier network with the specified network ID.

        This function executes the ZeroTier-CLI 'join' command with the provided network ID.

        Parameters:
        network_id (str): The ID of the ZeroTier network to join.

        Returns:
        list[dict]: Same as the `list_networks` method.

        Raises:
        CalledProcessError: If the ZeroTier-CLI command returns a non-zero exit code.
        """
        stdout, _ = await self.zerotier_cli(['join', network_id])
        decky.logger.info(f'Joined network {network_id}: {stdout.decode("utf-8").strip()}')

        return await self.list_networks()
    
    async def disconnect_network(self, network_id: str) -> list[dict]:
        """
        Disconnects from a ZeroTier network with the specified network ID.

        This function executes the ZeroTier-CLI 'leave' command with the provided network ID.
        And save the network with 'DISCONNECTED' status to the local network configuration file (ZT_NETCONF).

        Parameters:
        network_id (str): The ID of the ZeroTier network to disconnect from.

        Returns:
        list[dict]: Same as the `list_networks` method.

        Raises:
        CalledProcessError: If the ZeroTier-CLI command returns a non-zero exit code.
        """
        networks = await self.list_networks()
        stdout, _ = await self.zerotier_cli(['leave', network_id])
        decky.logger.info(f'Left network {network_id}: {stdout.decode("utf-8").strip()}')

        networks_ = []
        for net in networks:
            if net['id'] == network_id:
                net['status'] = 'DISCONNECTED'
            networks_.append(net)

        with open(ZT_NETCONF, 'w') as f:
            json.dump(networks, f)
        
        return networks
    
    async def forget_network(self, network_id: str) -> list[dict]:
        """
        Forgets a ZeroTier network with the specified network ID.

        This function executes the ZeroTier-CLI 'leave' command with the provided network ID,
        and removes the network from the local network configuration file (ZT_NETCONF).

        Parameters:
        network_id (str): The ID of the ZeroTier network to forget.

        Returns:
        list[dict]: A list of dictionaries, where each dictionary represents a ZeroTier network. Each dictionary
                    contains the following keys: 'id', 'name', 'private', 'status', and 'routes'.

        Raises:
        CalledProcessError: If the ZeroTier-CLI command returns a non-zero exit code.
        """
        stdout, _ = await self.zerotier_cli(['leave', network_id])
        decky.logger.info(f'Forgotten network {network_id}: {stdout.decode("utf-8").strip()}')

        if os.path.exists(ZT_NETCONF):
            with open(ZT_NETCONF, 'r') as f:
                netconf = json.load(f)
            netconf_ = [net for net in netconf if net['id']!= network_id]
            with open(ZT_NETCONF, 'w') as f:
                json.dump(netconf_, f)

        return await self.list_networks()
    
    async def update_network(self, network_id: str, option: str, value: bool) -> list[dict]:
        """
        Updates a specific network configuration option for a ZeroTier network.

        This function executes the ZeroTier-CLI 'set' command with the provided network ID, option, and value.

        Parameters:
        network_id (str): The ID of the ZeroTier network to update.
        option (str): The network configuration option to update. 
            'allowDNS': Allow DNS Configuration
            'allowDefault':Allow Default Router Override
            'allowManaged: Allow Managed Address
            'allowGlobal':Allow Assignment of Global IPs
        value (bool): The new value for the specified network configuration option.

        Returns:
        list[dict]: Same as the `list_networks` method.

        Raises:
        CalledProcessError: If the ZeroTier-CLI command returns a non-zero exit code.
        """
        stdout, _ = await self.zerotier_cli(['set', network_id, f'{option}={int(value)}'])
        decky.logger.info(f'Update network {network_id}: {stdout.decode("utf-8").strip()}')

        return await self.list_networks()
        
    # Asyncio-compatible long-running code, executed in a task when the plugin is loaded
    async def _main(self) -> None:
        decky.logger.info('Starting ZeroTier...')

        # Check if the ZeroTier-One binary exists
        if not os.path.exists(ZT_ONE):
            decky.logger.error(f'ZeroTier-One binary not found at {ZT_ONE}')
            return
        
        # Set the executable permission for the ZeroTier-One binary
        st = os.stat(ZT_ONE)
        os.chmod(ZT_ONE, st.st_mode | stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH)
        
        cmd = [ZT_ONE, ZT_HOME]
        decky.logger.info(' '.join(cmd))
        
        self.process = await asyncio.create_subprocess_exec(
            *cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.STDOUT,
            env=env
        )

        await self._read_stream(self.process.stdout, decky.logger.info)
        
        self.process.wait()


    # Function called first during the unload process, utilize this to handle your plugin being stopped, but not
    # completely removed
    async def _unload(self) -> None:
        decky.logger.info('Stopping ZeroTier...')


    # Function called after `_unload` during uninstall, utilize this to clean up processes and other remnants of your
    # plugin that may remain on the system
    async def _uninstall(self) -> None:
        self._unload()
        decky.logger.info('Uninstalling decky-zerotier...')
        # TODO: Clean up your plugin's resources here
        pass

    # Migrations that should be performed before entering `_main()`.
    async def _migration(self) -> None:
        pass
        # decky.logger.info('Migrating')
        # # Here's a migration example for logs:
        # # - `~/.config/decky-template/template.log` will be migrated to `decky.decky_LOG_DIR/template.log`
        # decky.migrate_logs(os.path.join(decky.DECKY_USER_HOME,
        #                                        '.config', 'decky-template', 'template.log'))
        # # Here's a migration example for settings:
        # # - `~/homebrew/settings/template.json` is migrated to `decky.decky_SETTINGS_DIR/template.json`
        # # - `~/.config/decky-template/` all files and directories under this root are migrated to `decky.decky_SETTINGS_DIR/`
        # decky.migrate_settings(
        #     os.path.join(decky.DECKY_HOME, 'settings', 'template.json'),
        #     os.path.join(decky.DECKY_USER_HOME, '.config', 'decky-template'))
        # # Here's a migration example for runtime data:
        # # - `~/homebrew/template/` all files and directories under this root are migrated to `decky.decky_RUNTIME_DIR/`
        # # - `~/.local/share/decky-template/` all files and directories under this root are migrated to `decky.decky_RUNTIME_DIR/`
        # decky.migrate_runtime(
        #     os.path.join(decky.DECKY_HOME, 'template'),
        #     os.path.join(decky.DECKY_USER_HOME, '.local', 'share', 'decky-template'))
