#!/usr/bin/env python3
#
#
#  IRIS velociraptorartifact Source Code
#  Copyright (C) 2023 - SOCFortress
#  info@socfortress.co
#  Created by SOCFortress - 2023-01-30
#
#  License MIT

module_name = "Velociraptor Artifact"
module_description = (
    "Module to interact with Velociraptor API to run artifacts agaisnt Assets."
    " Questions - info@socfortress.co"
)
interface_version = 1.1
module_version = 1.0

pipeline_support = False
pipeline_info = {}


module_configuration = [
    {
        "param_name": "velo_api_config",
        "param_human_name": "velo API config file",
        "param_description": (
            "Specify the full path to the API config file (yaml) to be used by"
            " pyvelociraptor. This must be accessible from the DFIR-IRIS container"
        ),
        "default": None,
        "mandatory": True,
        "type": "string",
    },
    {
        "param_name": "velo_artifact",
        "param_human_name": "Velociraptor artifact to run",
        "param_description": (
            "Specify the artifact to be collected via Velociraptor - I.E"
            " Windows.Applications.Chrome.History"
        ),
        "default": None,
        "mandatory": True,
        "type": "string",
    },
    {
        "param_name": "velociraptorartifact_manual_hook_enabled",
        "param_human_name": "Manual triggers on Assets",
        "param_description": "Set to True to offers possibility to manually triggers the module via the UI",
        "default": True,
        "mandatory": True,
        "type": "bool",
        "section": "Triggers"
    },# TODO: careful here, remove backslashes from \{\{ results| tojson(indent=4) \}\}
    {
        "param_name": "velociraptorartifact_domain_report_template",
        "param_human_name": "Domain report template",
        "param_description": "Domain report template used to add a new custom attribute to the target IOC",
        "default": "<div class=\"row\">\n    <div class=\"col-12\">\n        <div "
                   "class=\"accordion\">\n            <h3>velociraptorartifact raw results</h3>\n\n           "
                   " <div class=\"card\">\n                <div class=\"card-header "
                   "collapsed\" id=\"drop_r_velociraptorartifact\" data-toggle=\"collapse\" "
                   "data-target=\"#drop_raw_velociraptorartifact\" aria-expanded=\"false\" "
                   "aria-controls=\"drop_raw_velociraptorartifact\" role=\"button\">\n                    <div "
                   "class=\"span-icon\">\n                        <div "
                   "class=\"flaticon-file\"></div>\n                    </div>\n              "
                   "      <div class=\"span-title\">\n                        velociraptorartifact raw "
                   "results\n                    </div>\n                    <div "
                   "class=\"span-mode\"></div>\n                </div>\n                <div "
                   "id=\"drop_raw_velociraptorartifact\" class=\"collapse\" aria-labelledby=\"drop_r_velociraptorartifact\" "
                   "style=\"\">\n                    <div class=\"card-body\">\n              "
                   "          <div id='velociraptorartifact_raw_ace'>{{ results| tojson(indent=4) }}</div>\n  "
                   "                  </div>\n                </div>\n            </div>\n    "
                   "    </div>\n    </div>\n</div> \n<script>\nvar velociraptorartifact_in_raw = ace.edit("
                   "\"velociraptorartifact_raw_ace\",\n{\n    autoScrollEditorIntoView: true,\n    minLines: "
                   "30,\n});\nvelociraptorartifact_in_raw.setReadOnly(true);\nvelociraptorartifact_in_raw.setTheme("
                   "\"ace/theme/tomorrow\");\nvelociraptorartifact_in_raw.session.setMode("
                   "\"ace/mode/json\");\nvelociraptorartifact_in_raw.renderer.setShowGutter("
                   "true);\nvelociraptorartifact_in_raw.setOption(\"showLineNumbers\", "
                   "true);\nvelociraptorartifact_in_raw.setOption(\"showPrintMargin\", "
                   "false);\nvelociraptorartifact_in_raw.setOption(\"displayIndentGuides\", "
                   "true);\nvelociraptorartifact_in_raw.setOption(\"maxLines\", "
                   "\"Infinity\");\nvelociraptorartifact_in_raw.session.setUseWrapMode("
                   "true);\nvelociraptorartifact_in_raw.setOption(\"indentedSoftWrap\", "
                   "true);\nvelociraptorartifact_in_raw.renderer.setScrollMargin(8, 5);\n</script> ",
        "mandatory": False,
        "type": "textfield_html",
        "section": "Templates"
    }
    
]