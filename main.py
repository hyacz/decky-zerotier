import os
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
        while True:
            line = await stream.readline()
            if line:
                cb(line.decode('utf-8').strip())
            else:
                break
    
    async def info(self) -> dict:
        stdout, _ = await self.zerotier_cli(['info'])
        return json.loads(stdout.decode('utf-8'))

    async def list_networks(self) -> list[dict]:
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
        stdout, _ = await self.zerotier_cli(['join', network_id])
        decky.logger.info(f'Joined network {network_id}: {stdout.decode("utf-8").strip()}')

        return await self.list_networks()
    
    async def disconnect_network(self, network_id: str) -> list[dict]:
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
        stdout, _ = await self.zerotier_cli(['leave', network_id])
        decky.logger.info(f'Forgotten network {network_id}: {stdout.decode("utf-8").strip()}')

        if os.path.exists(ZT_NETCONF):
            with open(ZT_NETCONF, 'r') as f:
                netconf = json.load(f)
            netconf_ = [net for net in netconf if net['id']!= network_id]
            with open(ZT_NETCONF, 'w') as f:
                json.dump(netconf_, f)

        return await self.list_networks()
    
    # Asyncio-compatible long-running code, executed in a task when the plugin is loaded
    async def _main(self) -> None:
        decky.logger.info('Starting ZeroTier...')

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
