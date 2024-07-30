import os
import subprocess as sp
import threading
import json
import asyncio

# The decky plugin module is located at decky-loader/plugin
# For easy intellisense checkout the decky-loader code one directory up
# or add the `decky-loader/plugin` path to `python.analysis.extraPaths` in `.vscode/settings.json`
import decky

ZT_ONE = os.path.join(decky.DECKY_PLUGIN_DIR, 'bin', 'zerotier-one')
ZT_HOME = decky.DECKY_PLUGIN_SETTINGS_DIR

class Plugin:
    async def apiproxy(self, command) -> dict:
        # Change LD_LIBRARY_PATH to include system paths for libssl
        env = os.environ.copy()
        env['LD_LIBRARY_PATH'] = '/usr/lib:/usr/lib64'

        cmd = [ZT_ONE, '-q', '-j', f'-D{ZT_HOME}', command]
        decky.logger.info(cmd)
        
        try:
            output = sp.check_output(cmd, env=env)
        except sp.CalledProcessError as e:
            decky.logger.error(f'Error running ZeroTier-CLI: {e.output.decode("utf-8")}', exc_info=True)
            return {'error': str(e)}
        
        output = json.loads() 
        decky.logger.info(output)

        return output
        
    # Asyncio-compatible long-running code, executed in a task when the plugin is loaded
    async def _main(self) -> None:
        decky.logger.info('Starting ZeroTier...')

        # Change LD_LIBRARY_PATH to include system paths for libssl
        env = os.environ.copy()
        env['LD_LIBRARY_PATH'] = '/usr/lib:/usr/lib64'

        cmd = [ZT_ONE, ZT_HOME]
        decky.logger.info(cmd)
        self.task = sp.Popen(cmd, stdout=sp.PIPE, stderr=sp.PIPE, env=env)

        while True:
            # Retrieve stdout and stderr line by line from subprocess
            stdout = self.task.stdout.readline().decode('utf-8').strip()
            stderr = self.task.stderr.readline().decode('utf-8').strip()
            if self.task.returncode is not None:
                decky.logger.info(f'[ZeroTier]: Exited with code({self.task.returncode})')
                break
            if stdout:
                decky.logger.info(f'[ZeroTier]: {stdout}')
            if stderr:
                decky.logger.error(f'[ZeroTier]: {stderr}')


    # Function called first during the unload process, utilize this to handle your plugin being stopped, but not
    # completely removed
    async def _unload(self) -> None:
        decky.logger.info('Stopping ZeroTier...')
        try:
            self.task.terminate()
        except:
            decky.logger.error(f'Failed to stop ZeroTier (PID: {self.task.pid})', exc_info=True)


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
