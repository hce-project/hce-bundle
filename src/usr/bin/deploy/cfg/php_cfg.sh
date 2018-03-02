#! /bin/bash
#
#

INC="${HOME}/hce-node-tests/api/php/inc"
PHP="/usr/bin/php"

# hce_cli API
hce_cli_api="cli_parse_arguments cli_prettyPrintJson cli_getScreenSize cli_getASCIITreeFromArray"

# hce_kvdb API
hce_kvdb_api="HCE_KVDB_request HCE_KVDB_prepare_post_request HCE_KVDB_parse_response \
  HCE_KVDB_prepare_request_array HCE_KVDB_import_from_xml_file HCE_KVDB_import_from_json_file \
  HCE_KVDB_highlight_hashes_add "

# highlighter API
hce_highlighter_api="HCE_HLTR_request HCE_HLTR_prepare_request_array"

# HCE node API
hce_node_api="hce_connection_create hce_connection_delete hce_message_send \
  hce_message_receive hce_unique_client_id hce_unique_message_id hce_admin_message_create \
  hce_unique_id"

# HCE Sphinx API
hce_sphinx_api="hce_sphinx_admin_request hce_sphinx_prepare_request hce_sphinx_parse_response \
  hce_sphinx_admin_message_create hce_sphinx_exec hce_sphinx_search_create_json \
  hce_sphinx_search_prepare_parameters hce_sphinx_search_parse_json hce_sphinx_search_result_get"

# HCE NODE DRCE API
hce_drce_api="hce_drce_exec_create_parameters_array hce_drce_exec_prepare_request \
  hce_drce_exec_prepare_request_admin hce_drce_exec_parse_response hce_drce_exec_parse_response_json \
  "
# HCE NODE Manager API
manager="hce_manage_get_help hce_manage_node_get_handler_properties hce_manage_node_get_info \
  hce_manage_node_handler_command hce_manage_nodes_get_info hce_manage_command_cluster_structure_check \
  hce_manage_node_detect_role hce_manage_node_set_structure_relations \
  hce_manage_command_cluster_node_handler_command "

# the list of above mentioned API groups
api_groups="hce_cli_api hce_kvdb_api hce_highlighter_api hce_node_api hce_sphinx_api \
  hce_drce_api manager"

