#!/usr/bin/env python3
#
#
#  IRIS velociraptorartifact Source Code
#  Copyright (C) 2023 - SOCFortress
#  info@socfortress.co
#  Created by SOCFortress - 2023-01-30
#
#  License MIT

import traceback
from pathlib import Path

import iris_interface.IrisInterfaceStatus as InterfaceStatus
from iris_interface.IrisModuleInterface import IrisPipelineTypes, IrisModuleInterface, IrisModuleTypes

import iris_velociraptorartifact_module.IrisVelociraptorartifactConfig as interface_conf
from iris_velociraptorartifact_module.velociraptorartifact_handler.velociraptorartifact_handler import VelociraptorartifactHandler


class IrisVelociraptorartifactInterface(IrisModuleInterface):
    """
    Provide the interface between Iris and velociraptorartifactHandler
    """
    name = "IrisVelociraptorartifactInterface"
    _module_name = interface_conf.module_name
    _module_description = interface_conf.module_description
    _interface_version = interface_conf.interface_version
    _module_version = interface_conf.module_version
    _pipeline_support = interface_conf.pipeline_support
    _pipeline_info = interface_conf.pipeline_info
    _module_configuration = interface_conf.module_configuration
    
    _module_type = IrisModuleTypes.module_processor
    
     
    def register_hooks(self, module_id: int):
        """
        Registers all the hooks

        :param module_id: Module ID provided by IRIS
        :return: Nothing
        """
        self.module_id = module_id
        module_conf = self.module_dict_conf
        if module_conf.get('velociraptorartifact_manual_hook_enabled'):
            status = self.register_to_hook(module_id, iris_hook_name='on_manual_trigger_asset',
                                           manual_hook_name='Run Velociraptor Artifact')
            if status.is_failure():
                self.log.error(status.get_message())
                self.log.error(status.get_data())

            else:
                self.log.info("Successfully registered on_manual_trigger_asset hook")

        else:
            self.deregister_from_hook(module_id=self.module_id, iris_hook_name='on_manual_trigger_asset')


    def hooks_handler(self, hook_name: str, hook_ui_name: str, data: any):
        """
        Hooks handler table. Calls corresponding methods depending on the hooks name.

        :param hook_name: Name of the hook which triggered
        :param hook_ui_name: Name of the ui hook
        :param data: Data associated with the trigger.
        :return: Data
        """

        self.log.info(f'Received {hook_name}')
        if hook_name in ['on_manual_trigger_asset']:
            status = self._handle_asset(data=data)

        else:
            self.log.critical(f'Received unsupported hook {hook_name}')
            return InterfaceStatus.I2Error(data=data, logs=list(self.message_queue))

        if status.is_failure():
            self.log.error(f"Encountered error processing hook {hook_name}")
            return InterfaceStatus.I2Error(data=data, logs=list(self.message_queue))

        self.log.info(f"Successfully processed hook {hook_name}")
        return InterfaceStatus.I2Success(data=data, logs=list(self.message_queue))


    def _handle_asset(self, data) -> InterfaceStatus.IIStatus:
        """
        Handle the IOC data the module just received. The module registered
        to on_postload hooks, so it receives instances of IOC object.
        These objects are attached to a dedicated SQlAlchemy session so data can
        be modified safely.

        :param data: Data associated to the hook, here IOC object
        :return: IIStatus
        """

        velociraptorartifact_handler = VelociraptorartifactHandler(mod_config=self.module_dict_conf,
                               server_config=self.server_dict_conf,
                               logger=self.log)

        in_status = InterfaceStatus.IIStatus(code=InterfaceStatus.I2CodeNoError)

        for asset in data:
            # Check that the IOC we receive is of type the module can handle and dispatch
            if 'Linux -' in asset.asset_type.asset_name:
                status = velociraptorartifact_handler.handle_asset(asset=asset, case=asset)
                in_status = InterfaceStatus.merge_status(in_status, status)

            if 'Windows -' in asset.asset_type.asset_name:
                status = velociraptorartifact_handler.handle_asset(asset=asset, case=asset)
                in_status = InterfaceStatus.merge_status(in_status, status)

            #elif element.ioc_type.type_name in ['md5', 'sha224', 'sha256', 'sha512']:
            #    status = velociraptorartifact_handler.handle_hash(ioc=element)
            #    in_status = InterfaceStatus.merge_status(in_status, status)
            #
            # elif element.ioc_type.type_name in etc...

            else:
                self.log.error(f'Asset type {asset.asset_type.asset_name} not handled by velociraptorartifact module. Skipping')

        return in_status(data=data)
    
