import json

RAW_TREE_TEMPLATE_TREE = (
    '{"id":"507222858","starter_template":"0","starter_template_tool":"",'
    '"name":"AI Author Assist Test","description":"","tags":"",'
    '"template":"buttons","root_node_id":"1","org_id":"530566","view":"Q",'
    '"zoom_level":"100","unlinked_node_x":"0","unlinked_node_y":"0",'
    '"live":"0","ga_acct":"","active":"1",'
    '"create_date":"2023-04-14T19:04:11.000000Z",'
    '"last_opened":"2023-04-14T19:04:11.000000Z","last_modified":"2023-04-14T'
    '19:04:11.000000Z","show_attribution":"1","css_include":"https://somecss.'
    'com/","save_lock":"0","last_overview":"S","in_gallery":"0",'
    '"hide_from_agent_portal":"0","cidr":"","sso_restricted":"0",'
    '"is_private":"0","app_id":"0","app_message":"","language":"en",'
    '"collect_enhanced_data":"0","init_form_variables":"0",'
    '"tree_name_var":"0","tree_id_var":"0","last_tree_name_var":"0",'
    '"last_tree_id_var":"0","container_url_var":"0",'
    '"address_verification":"0","email_verification":"0",'
    '"phone_verification":"0","script_code":"","enable_push_live":"1",'
    '"feedback_email":"","nopermalink":"1","notitle":"0","show_history":"0",'
    '"show_breadcrumbs":"0","hide_back_button":"0",'
    '"show_restart_button":"1","show_feedback":"0","show_session_notes":"0",'
    '"show_search_all":"0","keep_vars_on_back":"0",'
    '"merge_vars_not_fixed":"0","transition":"none",'
    '"transition_speed":"500","responsive_videos":"1","lazyload":"0",'
    '"disable_scroll":"0","scroll_parent_to_top":"0","cache_tree":"0",'
    '"locale":"","date_format":"","google_translate":"","persist_names":"",'
    '"persist_node_ids":"","is_process":"0","dev_version_updated":"1",'
    '"disable_autocomplete":"0","form_report_vars":"","nodes":{"1":{'
    '"type":"Content","is_root":"1","node_name":"","page_title":"Paper '
    'Airplane","content":"<p id=\\"isPasted\\">This is node 1</p>",'
    '"question":"","keywords":"","confirmation_text":"","notes":"",'
    '"project_node_id":"1","score_var":"","x":"-1","y":"0","width":"150",'
    '"height":"75","level":"0","buttons_across":"0","resolution_state":"?",'
    '"hide_back_restart":"0","hide_persistent_buttons":"0",'
    '"hide_from_search":"0","repeat_form":"1","form_columns":"1","email":"",'
    '"email_bcc":"","email_return_url":"","email_subject":"",'
    '"email_preheader":"","email_reply_to":"","email_sender_name":"",'
    '"email_body":"","email_send_now":"0","email_include_session_data":"1",'
    '"email_data_privacy":"0","link":"","link_new_tab":"0",'
    '"link_direct":"1","open_tree_id":"0","open_tree_node_id":"0",'
    '"return_tree_node_id":"0","randomize_scoring":"0",'
    '"advanced_logic_node":"0","tag":"","jsmessage":"","value":"1",'
    '"probability":"500","updated":"0","display_order":"1",'
    '"score_running_total":"1","continuation_node_id":"0",'
    '"continuation_button_text":"","allow_pdf_download":"0",'
    '"doc_node_type":"html","pdf_url_variable":"pdf_url",'
    '"escalate_after":"0","search_scope":"0","formfields":{},"buttons":{'
    '"0":{"project_node_id":"1","button_text":"Next","hover_text":"",'
    '"button_link":"2","rank":"1","button_data":"","logic_expression":"",'
    '"wizard_skip":"0","value":"0","op":"","updated":"0"},'
    '"1":{"project_node_id":"1","button_text":"No Title","hover_text":"",'
    '"button_link":"3","rank":"2","button_data":"","logic_expression":"",'
    '"wizard_skip":"0","value":"0","op":"","updated":"0"}},"app_messages":{'
    '}},"2":{"type":"Content","is_root":"0","node_name":"",'
    '"page_title":"Calm down an angry customer","content":"<p '
    'id=\\"isPasted\\">Dealing with nodes</p>","question":"","keywords":"",'
    '"confirmation_text":"","notes":"","project_node_id":"2","score_var":"",'
    '"x":"-1","y":"0","width":"150","height":"75","level":"0",'
    '"buttons_across":"0","resolution_state":"?","hide_back_restart":"0",'
    '"hide_persistent_buttons":"0","hide_from_search":"0","repeat_form":"1",'
    '"form_columns":"1","email":"","email_bcc":"","email_return_url":"",'
    '"email_subject":"","email_preheader":"","email_reply_to":"",'
    '"email_sender_name":"","email_body":"","email_send_now":"0",'
    '"email_include_session_data":"1","email_data_privacy":"0","link":"",'
    '"link_new_tab":"0","link_direct":"1","open_tree_id":"0",'
    '"open_tree_node_id":"0","return_tree_node_id":"0",'
    '"randomize_scoring":"0","advanced_logic_node":"0","tag":"",'
    '"jsmessage":"","value":"1","probability":"500","updated":"0",'
    '"display_order":"2","score_running_total":"1",'
    '"continuation_node_id":"0","continuation_button_text":"",'
    '"allow_pdf_download":"0","doc_node_type":"html",'
    '"pdf_url_variable":"pdf_url","escalate_after":"0","search_scope":"0",'
    '"formfields":{},"buttons":{},"app_messages":{}},"3":{"type":"Content",'
    '"is_root":"0","node_name":"","page_title":"New Node","content":"<h1>And '
    'other node</h1>","question":"","keywords":"","confirmation_text":"",'
    '"notes":"","project_node_id":"3","score_var":"","x":"-1","y":"0",'
    '"width":"150","height":"75","level":"0","buttons_across":"0",'
    '"resolution_state":"?","hide_back_restart":"0",'
    '"hide_persistent_buttons":"0","hide_from_search":"0","repeat_form":"1",'
    '"form_columns":"1","email":"","email_bcc":"","email_return_url":"",'
    '"email_subject":"","email_preheader":"","email_reply_to":"",'
    '"email_sender_name":"","email_body":"","email_send_now":"0",'
    '"email_include_session_data":"1","email_data_privacy":"0","link":"",'
    '"link_new_tab":"0","link_direct":"1","open_tree_id":"0",'
    '"open_tree_node_id":"0","return_tree_node_id":"0",'
    '"randomize_scoring":"0","advanced_logic_node":"0","tag":"",'
    '"jsmessage":"","value":"1","probability":"500","updated":"-1",'
    '"display_order":"3","score_running_total":"1",'
    '"continuation_node_id":"0","continuation_button_text":"",'
    '"allow_pdf_download":"0","doc_node_type":"html",'
    '"pdf_url_variable":"pdf_url","escalate_after":"0","search_scope":"0",'
    '"formfields":{},"buttons":{},"app_messages":{}}},"predefined_vars":{}}'
)

RAW_TREE_TEMPLATE = {"details": [{"value": RAW_TREE_TEMPLATE_TREE}]}

BRONZE_TREE_METADATA_TEMPLATE = json.loads(
    '{"id": "507222858", "name": "<h1>AI Author Assist Test</h1>", '
    '"description": "this is some <b>text</b>", "tags": ["tree", "tag"], '
    '"org_id": "530566", "active": true, "create_date": '
    '"2023-04-14T19:04:11.000000Z", "last_opened": '
    '"2023-04-14T19:04:11.000000Z", "last_modified": "2023-04-14T19:04:11.'
    '000000Z", "is_private": false, "language": "en"}'
)


BRONZE_TREE_NODES_TEMPLATE = json.loads(
    '{"content": "<p id=\\"isPasted\\">This is node 1</p>", "keywords": ['
    '"a", "few", "keywords"], "page_title": "Paper <b>Airplane</b>", '
    '"question": "This is a<br /> question!", "tag": ["some", "tag"]}'
)

BRONZE_TREE_TEMPLATE = {
    "meta": BRONZE_TREE_METADATA_TEMPLATE,
    "nodes": {"1": BRONZE_TREE_NODES_TEMPLATE},
}

SILVER_TREE_METADATA_TEMPLATE = json.loads(
    '{"id": "125365649", "name": "Test Tree", "description": "this is a '
    'description", "tags": ["\\"zt_trees_trees\\".\\"test\\"", "\\"'
    'zt_trees_trees\\".\\"tag\\""], "org_id": "531868", "active": true, '
    '"create_date": "2021-03-04T11:17:03.000000Z", "last_opened": "2023-05-'
    '22T18:20:29.000000Z", "last_modified": "2023-05-22 18:20:28.000000Z", '
    '"is_private": false, "language": "en"}'
)

SILVER_TREE_NODES_TEMPLATE = json.loads(
    '{"content": {"page_title": "test title", "content": "test content of a '
    'node", "question": "Is this a question?"}, "meta": {"keywords": ["key", '
    '"word"], "tag": ["tag", "other"]}}'
)

SILVER_TREE_TEMPLATE = {
    "meta": SILVER_TREE_METADATA_TEMPLATE,
    "nodes": {"1": SILVER_TREE_NODES_TEMPLATE},
}
