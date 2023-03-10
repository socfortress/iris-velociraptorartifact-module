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
from jinja2 import Template
import iris_interface.IrisInterfaceStatus as InterfaceStatus
# Imports for datastore handling
import app
from app import db
from app.datamgmt.datastore.datastore_db import datastore_get_root
from app.datamgmt.datastore.datastore_db import datastore_get_standard_path
from app.datamgmt.manage.manage_attribute_db import add_tab_attribute_field
from app.models import DataStoreFile
from app.util import stream_sha256sum
#import marshmallow
import datetime

#import argparse
import json
import grpc
import time
#import yaml

import pyvelociraptor
from pyvelociraptor import api_pb2
from pyvelociraptor import api_pb2_grpc


class VelociraptorartifactHandler(object):
    def __init__(self, mod_config, server_config, logger):
        self.mod_config = mod_config
        self.server_config = server_config
        self.velociraptorartifact = self.get_velociraptorartifact_instance()
        self.log = logger
        self.config = pyvelociraptor.LoadConfigFile(
            self.mod_config.get("velo_api_config"),
        )

    def get_velociraptorartifact_instance(self):
        """
        Returns an velociraptorartifact API instance depending if the key is premium or not

        :return: { cookiecutter.keyword }} Instance
        """
        url = self.mod_config.get('velociraptorartifact_url')
        key = self.mod_config.get('velociraptorartifact_key')
        proxies = {}

        if self.server_config.get('http_proxy'):
            proxies['https'] = self.server_config.get('HTTPS_PROXY')

        if self.server_config.get('https_proxy'):
            proxies['http'] = self.server_config.get('HTTP_PROXY')

        # TODO!
        # Here get your velociraptorartifact instance and return it
        # ex: return velociraptorartifactApi(url, key)
        return "<TODO>"

    def gen_domain_report_from_template(self, html_template, velociraptorartifact_report) -> InterfaceStatus:
        """
        Generates an HTML report for Domain, displayed as an attribute in the IOC

        :param html_template: A string representing the HTML template
        :param misp_report: The JSON report fetched with velociraptorartifact API
        :return: InterfaceStatus
        """
        template = Template(html_template)
        context = velociraptorartifact_report
        pre_render = dict({"results": []})

        for velociraptorartifact_result in context:
            pre_render["results"].append(velociraptorartifact_result)

        try:
            rendered = template.render(pre_render)

        except Exception:
            print(traceback.format_exc())
            self.log.error(traceback.format_exc())
            return InterfaceStatus.I2Error(traceback.format_exc())

        return InterfaceStatus.I2Success(data=rendered)

    def handle_asset(self, asset):
        """
        Handles an Asset and runs the configured Velociraptorartifact queries

        :param ioc: Asset
        :return: IIStatus
        """
        artifact = self.mod_config.get("velo_artifact")
        self.log.info(f'Running artifact {artifact} on asset {asset.asset_name}')

        creds = grpc.ssl_channel_credentials(
            root_certificates=self.config["ca_certificate"].encode("utf8"),
            private_key=self.config["client_private_key"].encode("utf8"),
            certificate_chain=self.config["client_cert"].encode("utf8"),
        )

        options = (("grpc.ssl_target_name_override", "VelociraptorServer"),)

        with grpc.secure_channel(
            self.config["api_connection_string"],
            creds,
            options,
        ) as channel:
            stub = api_pb2_grpc.APIStub(channel)

            client_query = (
                "select client_id from clients(search='host:" + asset.asset_name + "')"
            )

            # Send initial request
            client_request = api_pb2.VQLCollectorArgs(
                max_wait=1,
                Query=[
                    api_pb2.VQLRequest(
                        Name="ClientQuery",
                        VQL=client_query,
                    ),
                ],
            )

            for client_response in stub.Query(client_request):
                try:
                    client_results = json.loads(client_response.Response)
                    global client_id
                    client_id = client_results[0]["client_id"]
                    self.info.log(f'Found client id: {client_id}')
                except Exception:
                    self.log.info({"message": "Could not find a suitable client."})
                    pass

            # Define initial query
            init_query = (
                "SELECT collect_client(client_id='"
                + client_id
                + "', artifacts=['"
                + artifact
                + "']) FROM scope()"
            )

            # Send initial request
            request = api_pb2.VQLCollectorArgs(
                max_wait=1,
                Query=[
                    api_pb2.VQLRequest(
                        Name="Query",
                        VQL=init_query,
                    ),
                ],
            )

            for response in stub.Query(request):
                try:
                    init_results = json.loads(response.Response)
                    flow = list(init_results[0].values())[0]
                    flow_id = str(flow["flow_id"])
                    # Define second query
                    flow_query = (
                        "SELECT * from flows(client_id='"
                        + str(flow["request"]["client_id"])
                        + "', flow_id='"
                        + flow_id
                        + "')"
                    )
                    state = "RUNNING"

                    # Check to see if the flow has completed
                    while state != "FINISHED":
                        followup_request = api_pb2.VQLCollectorArgs(
                            max_wait=10,
                            Query=[
                                api_pb2.VQLRequest(
                                    Name="QueryForFlow",
                                    VQL=flow_query,
                                ),
                            ],
                        )

                        for followup_response in stub.Query(followup_request):
                            try:
                                flow_results = json.loads(followup_response.Response)
                            except Exception:
                                pass
                        state = flow_results[0]["state"]
                        global artifact_results
                        artifact_results = flow_results[0]["artifacts_with_results"]
                        self.log.info({"message": state})
                        time.sleep(1.0)
                        if state == "FINISHED":
                            asset.asset_tags = f"{asset.asset_tags},{artifact}:collected"
                            time.sleep(5)
                            break

                    # Grab the source from the artifact
                    source_results = []
                    for artifact in artifact_results:
                        source_query = (
                            "SELECT * from source(client_id='"
                            + str(flow["request"]["client_id"])
                            + "', flow_id='"
                            + flow_id
                            + "', artifact='"
                            + artifact
                            + "')"
                        )
                        source_request = api_pb2.VQLCollectorArgs(
                            max_wait=10,
                            Query=[
                                api_pb2.VQLRequest(
                                    Name="SourceQuery",
                                    VQL=source_query,
                                ),
                            ],
                        )
                        for source_response in stub.Query(source_request):
                            try:
                                source_result = json.loads(source_response.Response)
                                source_results += source_result
                                #Add results to datastore
                                # store client config in datastore
                               # self.add_to_datastore(case, artifact_results)
                            except Exception:
                                pass
                        try:
                            self.log.info(f'Found {len(source_results)} results for {artifact}')
                            #Convert json dict to string
                            string_results = json.dumps(source_results)
                            encoded_results = string_results.encode()
                            file_hash = stream_sha256sum(encoded_results)
                            dsp = datastore_get_root(asset.case_id)
                            dsf = DataStoreFile()
                            dsf.file_original_name = f"{artifact}"
                            dsf.file_description = f"Velociraptor client config for {artifact}."
                            dsf.file_tags = "Velociraptor"
                            dsf.file_password = ""
                            dsf.file_is_ioc = False
                            dsf.file_is_evidence = False
                            dsf.file_case_id = asset.case_id
                            dsf.file_date_added = datetime.datetime.now()
                            dsf.added_by_user_id = asset.user_id
                            dsf.file_local_name = 'tmp_config'
                            dsf.file_parent_id = dsp.path_id
                            dsf.file_sha256 = file_hash
                            db.session.add(dsf)
                            db.session.commit()
                            dsf.file_local_name = datastore_get_standard_path(dsf, asset.case_id).as_posix()
                            db.session.commit()
                            self.log.info("Uploading file to datastore")
                            with open(dsf.file_local_name, 'wb') as fout:
                                fout.write(encoded_results)
                                setattr(self, 'file_local_path', str(dsf.file_local_name))

                            self.log.info("Adding new attribute Velociraptor Report to Asset")

                            status = self.gen_domain_report_from_template(
                                html_template=self.mod_config.get(
                                    "velociraptorartifact_domain_report_template",
                                ),
                                velociraptorartifact_report=source_results,
                            )
                            rendered_report = status.get_data()

                            add_tab_attribute_field(
                                asset,
                                tab_name=artifact,
                                field_name="HTML report",
                                field_type="html",
                                field_value=rendered_report,
                            )

                        except Exception:
                            self.log.error(traceback.format_exc())
                            return InterfaceStatus.I2Error(traceback.format_exc())

                    return InterfaceStatus.I2Success("Successfully processed report")

                except Exception:
                    pass