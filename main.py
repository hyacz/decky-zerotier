import os
import subprocess
import json

# The decky plugin module is located at decky-loader/plugin
# For easy intellisense checkout the decky-loader code one directory up
# or add the `decky-loader/plugin` path to `python.analysis.extraPaths` in `.vscode/settings.json`
import decky_plugin as decky

ZT_ONE = os.path.join(decky.DECKY_PLUGIN_DIR, 'bin', 'zerotier-one')
ZT_HOME = decky.DECKY_PLUGIN_SETTINGS_DIR

class Plugin:
    
    async def plugin_info(self):
        # Call plugin_info only once preferably
        decky.logger.debug('[backend] PluginInfo:\n\tPluginName: {}\n\tPluginVersion: {}\n\tDeckyVersion: {}'.format(
            decky.decky_NAME,
            decky.decky_VERSION,
            decky.DECKY_VERSION
        ))
        pluginInfo = {
            "name": decky.decky_NAME,
            "version": decky.decky_VERSION
        }
        return pluginInfo

    # A normal method. It can be called from JavaScript using call_plugin_function("method_1", argument1, argument2)
    async def add(self, left, right):
        return left + right

    # Asyncio-compatible long-running code, executed in a task when the plugin is loaded
    async def _main(self):
        decky.logger.info("Starting ZeroTier...")
        self.task = subprocess.run([ZT_ONE, f"-D{ZT_HOME}", "-d"],
                                    stdout=subprocess.PIPE,
                                    stderr=subprocess.PIPE)
        for line in self.task.stdout:
            decky.logger.debug(f"[ZeroTier]: {line.decode("utf-8").strip()}")


    # Function called first during the unload process, utilize this to handle your plugin being stopped, but not
    # completely removed
    async def _unload(self):
        decky.logger.info("Stop ZeroTier...")
        try:
            self.task.terminate()
        except:
            decky.logger.error(f"Failed to stop ZeroTier (PID: {self.task.pid})", exc_info=True)


    # Function called after `_unload` during uninstall, utilize this to clean up processes and other remnants of your
    # plugin that may remain on the system
    async def _uninstall(self):
        self._unload()
        decky.logger.info("Uninstalling decky-zerotier...")
        # TODO: Clean up your plugin's resources here
        pass

    # Migrations that should be performed before entering `_main()`.
    async def _migration(self):
        pass
        # decky.logger.info("Migrating")
        # # Here's a migration example for logs:
        # # - `~/.config/decky-template/template.log` will be migrated to `decky.decky_LOG_DIR/template.log`
        # decky.migrate_logs(os.path.join(decky.DECKY_USER_HOME,
        #                                        ".config", "decky-template", "template.log"))
        # # Here's a migration example for settings:
        # # - `~/homebrew/settings/template.json` is migrated to `decky.decky_SETTINGS_DIR/template.json`
        # # - `~/.config/decky-template/` all files and directories under this root are migrated to `decky.decky_SETTINGS_DIR/`
        # decky.migrate_settings(
        #     os.path.join(decky.DECKY_HOME, "settings", "template.json"),
        #     os.path.join(decky.DECKY_USER_HOME, ".config", "decky-template"))
        # # Here's a migration example for runtime data:
        # # - `~/homebrew/template/` all files and directories under this root are migrated to `decky.decky_RUNTIME_DIR/`
        # # - `~/.local/share/decky-template/` all files and directories under this root are migrated to `decky.decky_RUNTIME_DIR/`
        # decky.migrate_runtime(
        #     os.path.join(decky.DECKY_HOME, "template"),
        #     os.path.join(decky.DECKY_USER_HOME, ".local", "share", "decky-template"))
