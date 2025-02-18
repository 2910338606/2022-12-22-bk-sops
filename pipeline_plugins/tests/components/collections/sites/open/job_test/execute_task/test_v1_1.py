# -*- coding: utf-8 -*-
"""
Tencent is pleased to support the open source community by making 蓝鲸智云PaaS平台社区版 (BlueKing PaaS Community
Edition) available.
Copyright (C) 2017 THL A29 Limited, a Tencent company. All rights reserved.
Licensed under the MIT License (the "License"); you may not use this file except in compliance with the License.
You may obtain a copy of the License at
http://opensource.org/licenses/MIT
Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on
an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the
specific language governing permissions and limitations under the License.
"""

from django.test import TestCase

import ujson as json
from mock import MagicMock

from pipeline.component_framework.test import (
    ComponentTestMixin,
    ComponentTestCase,
    CallAssertion,
    ExecuteAssertion,
    ScheduleAssertion,
    Call,
    Patcher,
)
from pipeline_plugins.components.collections.sites.open.job.execute_task.v1_1 import JobExecuteTaskComponent
from pipeline_plugins.components.collections.sites.open.job import base

base.LOG_VAR_SEARCH_CONFIGS.append({"re": "<##(.+?)##>", "kv_sep": "="})


class JobExecuteTaskComponentTest(TestCase, ComponentTestMixin):
    def cases(self):
        return [
            EXECUTE_JOB_FAIL_CASE,
            INVALID_CALLBACK_DATA_CASE,
            JOB_EXECUTE_NOT_SUCCESS_CASE,
            GET_GLOBAL_VAR_FAIL_CASE,
            EXECUTE_SUCCESS_CASE,
            GET_VAR_ERROR_SUCCESS_CASE,
            INVALID_IP_CASE,
            IP_IS_EXIST_CASE,
        ]

    def component_cls(self):
        return JobExecuteTaskComponent


class MockClient(object):
    def __init__(
        self,
        execute_job_return,
        get_global_var_return=None,
        get_job_instance_log_return=None,
        get_job_instance_ip_log_return=None,
        get_job_instance_status=None,
    ):
        self.set_bk_api_ver = MagicMock()
        self.jobv3 = MagicMock()
        self.jobv3.execute_job_plan = MagicMock(return_value=execute_job_return)
        self.jobv3.get_job_instance_global_var_value = MagicMock(return_value=get_global_var_return)
        self.jobv3.get_job_instance_log = MagicMock(return_value=get_job_instance_log_return)
        self.jobv3.get_job_instance_ip_log = MagicMock(return_value=get_job_instance_ip_log_return)
        self.jobv3.get_job_instance_status = MagicMock(return_value=get_job_instance_status)


# mock path
# 因为v1.1版本的JobExecuteTaskService类直接继承了JobExecuteTaskServiceBase类,所以mock路径也使用其父类的路径
GET_CLIENT_BY_USER = (
    "pipeline_plugins.components.collections.sites.open.job.execute_task.execute_task_base.get_client_by_user"
)
CC_GET_IPS_INFO_BY_STR = "pipeline_plugins.components.utils.sites.open.utils.cc_get_ips_info_by_str"
GET_NODE_CALLBACK_URL = (
    "pipeline_plugins.components.collections.sites.open.job.execute_task.execute_task_base.get_node_callback_url"
)
GET_JOB_INSTANCE_URL = (
    "pipeline_plugins.components.collections.sites.open.job.execute_task.execute_task_base.get_job_instance_url"
)

GET_VAR_ERROR_SUCCESS_GET_LOG_RETURN = {"code": 0, "result": False, "message": "success", "data": []}

EXECUTE_SUCCESS_GET_STATUS_RETURN = {
    "result": True,
    "code": 0,
    "message": "",
    "data": {
        "finished": True,
        "job_instance": {
            "job_instance_id": 100,
            "bk_biz_id": 1,
            "name": "API Quick execution script1521089795887",
            "create_time": 1605064271000,
            "status": 4,
            "start_time": 1605064271000,
            "end_time": 1605064272000,
            "total_time": 1000,
        },
        "step_instance_list": [
            {
                "status": 4,
                "total_time": 1000,
                "name": "API Quick execution scriptxxx",
                "step_instance_id": 75,
                "execute_count": 0,
                "create_time": 1605064271000,
                "end_time": 1605064272000,
                "type": 1,
                "start_time": 1605064271000,
                "step_ip_result_list": [
                    {
                        "ip": "1.1.1.1",
                        "bk_cloud_id": 0,
                        "status": 9,
                        "tag": "tag",
                        "exit_code": 0,
                        "error_code": 0,
                        "start_time": 1605064271000,
                        "end_time": 1605064272000,
                        "total_time": 1000,
                    },
                    {
                        "ip": "1.1.1.2",
                        "bk_cloud_id": 0,
                        "status": 9,
                        "tag": "tag",
                        "exit_code": 0,
                        "error_code": 0,
                        "start_time": 1605064271000,
                        "end_time": 1605064272000,
                        "total_time": 1000,
                    },
                ],
            }
        ],
    },
}

EXECUTE_SUCCESS_GET_IP_LOG_RETURN = {
    "result": True,
    "code": 0,
    "message": "",
    "data": {
        "ip": "10.0.0.1",
        "bk_cloud_id": 0,
        "log_content": "<SOPS_VAR>key1:value1</SOPS_VAR>\ngsectl\n-rwxr-xr-x 1\n"
        "<SOPS_VAR>key4:   v   </SOPS_VAR><SOPS_VAR>key5:  </SOPS_VAR>"
        "<SOPS_VAR>key6:v:v</SOPS_VAR><SOPS_VAR>key empty</SOPS_VAR>"
        "<SOPS_VAR>:1</SOPS_VAR><SOPS_VAR>:1   fgdshgdsh</SOPS_VAR>"
        "<##{key}=v##><##{key}notvar##>"
        "&lt;SOPS_VAR&gt;key2:value2&lt;/SOPS_VAR&gt;\n"
        "dfg&lt;SOPS_VAR&gt;key3:value3&lt;/SOPS_VAR&gt;"
        "&lt;SOPS_VAR&gt;k: v  &lt;/SOPS_VAR&gt;"
        "&lt;SOPS_VAR&gt;k1: :v  &lt;/SOPS_VAR&gt;"
        "&lt;SOPS_VAR&gt;k1      &lt;/SOPS_VAR&gt;"
        "&lt;##{key2}=v##&gt;&lt;##{key3}=var##&gt;",
    },
}

# mock clients
EXECUTE_JOB_CALL_FAIL_CLIENT = MockClient(execute_job_return={"result": False, "message": "message token"})
INVALID_CALLBACK_DATA_CLIENT = MockClient(
    execute_job_return={"result": True, "data": {"job_instance_id": 56789, "job_instance_name": "job_name_token"}}
)
JOB_EXECUTE_NOT_SUCCESS_CLIENT = MockClient(
    execute_job_return={"result": True, "data": {"job_instance_id": 56789, "job_instance_name": "job_name_token"}}
)
GET_GLOBAL_VAR_CALL_FAIL_CLIENT = MockClient(
    execute_job_return={"result": True, "data": {"job_instance_id": 56789, "job_instance_name": "job_name_token"}},
    get_global_var_return={"result": False, "message": "global var message token"},
)
EXECUTE_SUCCESS_CLIENT = MockClient(
    execute_job_return={"result": True, "data": {"job_instance_id": 56789, "job_instance_name": "job_name_token"}},
    get_global_var_return={
        "result": True,
        "data": {
            "step_instance_var_list": [
                {
                    "global_var_list": [
                        {"type": 1, "name": "key_1", "value": "new_value_1"},
                        {"type": 1, "name": "key_2", "value": "new_value_2"},
                    ]
                }
            ]
        },
    },
    get_job_instance_ip_log_return=EXECUTE_SUCCESS_GET_IP_LOG_RETURN,
    get_job_instance_status=EXECUTE_SUCCESS_GET_STATUS_RETURN,
)

GET_VAR_ERROR_SUCCESS_CLIENT = MockClient(
    execute_job_return={"result": True, "data": {"job_instance_id": 56789, "job_instance_name": "job_name_token"}},
    get_global_var_return={
        "result": True,
        "data": {
            "step_instance_var_list": [
                {
                    "global_var_list": [
                        {"type": 1, "name": "key_1", "value": "new_value_1"},
                        {"type": 1, "name": "key_2", "value": "new_value_2"},
                    ]
                }
            ]
        },
    },
    get_job_instance_log_return=GET_VAR_ERROR_SUCCESS_GET_LOG_RETURN,
    get_job_instance_ip_log_return=EXECUTE_SUCCESS_GET_IP_LOG_RETURN,
    get_job_instance_status=EXECUTE_SUCCESS_GET_STATUS_RETURN,
)

# test cases
EXECUTE_JOB_FAIL_CASE = ComponentTestCase(
    name="v1.1 execute_job call failed case",
    inputs={
        "job_global_var": [
            {"category": 1, "name": "key_1", "value": "value_1"},
            {"category": 1, "name": "key_2", "value": "value_2"},
            {"category": 3, "name": "key_3", "value": "1.1.1.1,2.2.2.2"},
        ],
        "job_task_id": 12345,
        "biz_cc_id": 1,
    },
    parent_data={"executor": "executor_token", "biz_cc_id": 1},
    execute_assertion=ExecuteAssertion(
        success=False,
        outputs={
            "ex_data": ("调用作业平台(JOB)接口jobv3.execute_job_plan返回失败, params={params}, " "error=message token").format(
                params=json.dumps(
                    {
                        "bk_scope_type": "biz",
                        "bk_scope_id": "1",
                        "bk_biz_id": 1,
                        "job_plan_id": 12345,
                        "global_var_list": [
                            {"name": "key_1", "value": "value_1"},
                            {"name": "key_2", "value": "value_2"},
                            {
                                "name": "key_3",
                                "server": {
                                    "ip_list": [
                                        {"ip": "1.1.1.1", "bk_cloud_id": 1},
                                        {"ip": "2.2.2.2", "bk_cloud_id": 1},
                                    ],
                                },
                            },
                        ],
                        "callback_url": "url_token",
                    }
                )
            )
        },
    ),
    schedule_assertion=None,
    execute_call_assertion=[
        CallAssertion(
            func=CC_GET_IPS_INFO_BY_STR,
            calls=[Call(username="executor_token", biz_cc_id=1, ip_str="1.1.1.1,2.2.2.2", use_cache=False)],
        ),
        CallAssertion(
            func=EXECUTE_JOB_CALL_FAIL_CLIENT.jobv3.execute_job_plan,
            calls=[
                Call(
                    {
                        "bk_scope_type": "biz",
                        "bk_scope_id": "1",
                        "bk_biz_id": 1,
                        "job_plan_id": 12345,
                        "global_var_list": [
                            {"name": "key_1", "value": "value_1"},
                            {"name": "key_2", "value": "value_2"},
                            {
                                "name": "key_3",
                                "server": {
                                    "ip_list": [
                                        {"ip": "1.1.1.1", "bk_cloud_id": 1},
                                        {"ip": "2.2.2.2", "bk_cloud_id": 1},
                                    ],
                                },
                            },
                        ],
                        "callback_url": "url_token",
                    }
                )
            ],
        ),
    ],
    patchers=[
        Patcher(target=GET_CLIENT_BY_USER, return_value=EXECUTE_JOB_CALL_FAIL_CLIENT),
        Patcher(
            target=CC_GET_IPS_INFO_BY_STR,
            return_value={"ip_result": [{"InnerIP": "1.1.1.1", "Source": 1}, {"InnerIP": "2.2.2.2", "Source": 1}]},
        ),
        Patcher(target=GET_NODE_CALLBACK_URL, return_value="url_token"),
    ],
)

INVALID_CALLBACK_DATA_CASE = ComponentTestCase(
    name="v1.1 invalid callback case",
    inputs={
        "job_global_var": [
            {"category": 1, "name": "key_1", "value": "value_1"},
            {"category": 1, "name": "key_2", "value": "value_2"},
            {"category": 3, "name": "key_3", "value": "1.1.1.1,2.2.2.2"},
        ],
        "job_task_id": 12345,
        "biz_cc_id": 1,
    },
    parent_data={"executor": "executor_token", "biz_cc_id": 1},
    execute_assertion=ExecuteAssertion(
        success=True,
        outputs={
            "job_inst_url": "instance_url_token",
            "job_inst_id": 56789,
            "job_inst_name": "job_name_token",
            "client": INVALID_CALLBACK_DATA_CLIENT,
        },
    ),
    schedule_assertion=ScheduleAssertion(
        success=False,
        outputs={
            "job_inst_url": "instance_url_token",
            "job_inst_id": 56789,
            "job_inst_name": "job_name_token",
            "client": INVALID_CALLBACK_DATA_CLIENT,
            "ex_data": "invalid callback_data, " "job_instance_id: None, status: None",
        },
        callback_data={},
    ),
    execute_call_assertion=[
        CallAssertion(
            func=CC_GET_IPS_INFO_BY_STR,
            calls=[Call(username="executor_token", biz_cc_id=1, ip_str="1.1.1.1,2.2.2.2", use_cache=False)],
        ),
        CallAssertion(
            func=INVALID_CALLBACK_DATA_CLIENT.jobv3.execute_job_plan,
            calls=[
                Call(
                    {
                        "bk_scope_type": "biz",
                        "bk_scope_id": "1",
                        "bk_biz_id": 1,
                        "job_plan_id": 12345,
                        "global_var_list": [
                            {"name": "key_1", "value": "value_1"},
                            {"name": "key_2", "value": "value_2"},
                            {
                                "name": "key_3",
                                "server": {
                                    "ip_list": [
                                        {"ip": "1.1.1.1", "bk_cloud_id": 1},
                                        {"ip": "2.2.2.2", "bk_cloud_id": 1},
                                    ],
                                },
                            },
                        ],
                        "callback_url": "url_token",
                    }
                )
            ],
        ),
    ],
    patchers=[
        Patcher(target=GET_CLIENT_BY_USER, return_value=INVALID_CALLBACK_DATA_CLIENT),
        Patcher(
            target=CC_GET_IPS_INFO_BY_STR,
            return_value={"ip_result": [{"InnerIP": "1.1.1.1", "Source": 1}, {"InnerIP": "2.2.2.2", "Source": 1}]},
        ),
        Patcher(target=GET_NODE_CALLBACK_URL, return_value="url_token"),
        Patcher(target=GET_JOB_INSTANCE_URL, return_value="instance_url_token"),
    ],
)

JOB_EXECUTE_NOT_SUCCESS_CASE = ComponentTestCase(
    name="v1.1 job execute not success case",
    inputs={
        "job_global_var": [
            {"category": 1, "name": "key_1", "value": "value_1"},
            {"category": 1, "name": "key_2", "value": "value_2"},
            {"category": 3, "name": "key_3", "value": "1.1.1.1,2.2.2.2"},
        ],
        "job_task_id": 12345,
        "biz_cc_id": 1,
    },
    parent_data={"executor": "executor_token", "biz_cc_id": 1},
    execute_assertion=ExecuteAssertion(
        success=True,
        outputs={
            "job_inst_url": "instance_url_token",
            "job_inst_id": 56789,
            "job_inst_name": "job_name_token",
            "client": JOB_EXECUTE_NOT_SUCCESS_CLIENT,
        },
    ),
    schedule_assertion=ScheduleAssertion(
        success=False,
        outputs={
            "job_inst_url": "instance_url_token",
            "job_inst_id": 56789,
            "job_inst_name": "job_name_token",
            "client": JOB_EXECUTE_NOT_SUCCESS_CLIENT,
            "ex_data": {
                "exception_msg": ("任务执行失败，<a href='%s' target='_blank'>" "前往作业平台(JOB)查看详情</a>") % "instance_url_token",
                "task_inst_id": 56789,
                "show_ip_log": True,
            },
        },
        callback_data={"job_instance_id": 56789, "status": 1},
    ),
    execute_call_assertion=[
        CallAssertion(
            func=CC_GET_IPS_INFO_BY_STR,
            calls=[Call(username="executor_token", biz_cc_id=1, ip_str="1.1.1.1,2.2.2.2", use_cache=False)],
        ),
        CallAssertion(
            func=JOB_EXECUTE_NOT_SUCCESS_CLIENT.jobv3.execute_job_plan,
            calls=[
                Call(
                    {
                        "bk_scope_type": "biz",
                        "bk_scope_id": "1",
                        "bk_biz_id": 1,
                        "job_plan_id": 12345,
                        "global_var_list": [
                            {"name": "key_1", "value": "value_1"},
                            {"name": "key_2", "value": "value_2"},
                            {
                                "name": "key_3",
                                "server": {
                                    "ip_list": [
                                        {"ip": "1.1.1.1", "bk_cloud_id": 1},
                                        {"ip": "2.2.2.2", "bk_cloud_id": 1},
                                    ],
                                },
                            },
                        ],
                        "callback_url": "url_token",
                    }
                )
            ],
        ),
    ],
    patchers=[
        Patcher(target=GET_CLIENT_BY_USER, return_value=JOB_EXECUTE_NOT_SUCCESS_CLIENT),
        Patcher(
            target=CC_GET_IPS_INFO_BY_STR,
            return_value={"ip_result": [{"InnerIP": "1.1.1.1", "Source": 1}, {"InnerIP": "2.2.2.2", "Source": 1}]},
        ),
        Patcher(target=GET_NODE_CALLBACK_URL, return_value="url_token"),
        Patcher(target=GET_JOB_INSTANCE_URL, return_value="instance_url_token"),
    ],
)

GET_GLOBAL_VAR_FAIL_CASE = ComponentTestCase(
    name="v1.1 get global var fail case",
    inputs={
        "job_global_var": [
            {"category": 1, "name": "key_1", "value": "value_1"},
            {"category": 1, "name": "key_2", "value": "value_2"},
            {"category": 3, "name": "key_3", "value": "1.1.1.1,2.2.2.2"},
        ],
        "job_task_id": 12345,
        "biz_cc_id": 1,
        "is_tagged_ip": False,
    },
    parent_data={"executor": "executor_token", "biz_cc_id": 1},
    execute_assertion=ExecuteAssertion(
        success=True,
        outputs={
            "job_inst_url": "instance_url_token",
            "job_inst_id": 56789,
            "job_inst_name": "job_name_token",
            "client": GET_GLOBAL_VAR_CALL_FAIL_CLIENT,
        },
    ),
    schedule_assertion=ScheduleAssertion(
        success=False,
        outputs={
            "job_inst_url": "instance_url_token",
            "job_inst_id": 56789,
            "job_inst_name": "job_name_token",
            "client": GET_GLOBAL_VAR_CALL_FAIL_CLIENT,
            "job_tagged_ip_dict": {},
            "ex_data": (
                "调用作业平台(JOB)接口jobv3.get_job_instance_global_var_value"
                "返回失败, params={params}, error=global var message token"
            ).format(
                params=json.dumps(
                    {"bk_scope_type": "biz", "bk_scope_id": "1", "bk_biz_id": 1, "job_instance_id": 56789}
                )
            ),
        },
        callback_data={"job_instance_id": 56789, "status": 3},
    ),
    execute_call_assertion=[
        CallAssertion(
            func=CC_GET_IPS_INFO_BY_STR,
            calls=[Call(username="executor_token", biz_cc_id=1, ip_str="1.1.1.1,2.2.2.2", use_cache=False)],
        ),
        CallAssertion(
            func=GET_GLOBAL_VAR_CALL_FAIL_CLIENT.jobv3.execute_job_plan,
            calls=[
                Call(
                    {
                        "bk_scope_type": "biz",
                        "bk_scope_id": "1",
                        "bk_biz_id": 1,
                        "job_plan_id": 12345,
                        "global_var_list": [
                            {"name": "key_1", "value": "value_1"},
                            {"name": "key_2", "value": "value_2"},
                            {
                                "name": "key_3",
                                "server": {
                                    "ip_list": [
                                        {"ip": "1.1.1.1", "bk_cloud_id": 1},
                                        {"ip": "2.2.2.2", "bk_cloud_id": 1},
                                    ],
                                },
                            },
                        ],
                        "callback_url": "url_token",
                    }
                )
            ],
        ),
    ],
    schedule_call_assertion=[
        CallAssertion(
            func=GET_GLOBAL_VAR_CALL_FAIL_CLIENT.jobv3.get_job_instance_global_var_value,
            calls=[Call({"bk_scope_type": "biz", "bk_scope_id": "1", "bk_biz_id": 1, "job_instance_id": 56789})],
        )
    ],
    patchers=[
        Patcher(target=GET_CLIENT_BY_USER, return_value=GET_GLOBAL_VAR_CALL_FAIL_CLIENT),
        Patcher(
            target=CC_GET_IPS_INFO_BY_STR,
            return_value={"ip_result": [{"InnerIP": "1.1.1.1", "Source": 1}, {"InnerIP": "2.2.2.2", "Source": 1}]},
        ),
        Patcher(target=GET_NODE_CALLBACK_URL, return_value="url_token"),
        Patcher(target=GET_JOB_INSTANCE_URL, return_value="instance_url_token"),
    ],
)

EXECUTE_SUCCESS_CASE = ComponentTestCase(
    name="v1.1 execute success case",
    inputs={
        "job_global_var": [
            {"category": 1, "name": "key_1", "value": "value_1"},
            {"category": 1, "name": "key_2", "value": "value_2"},
            {"category": 3, "name": "key_3", "value": "1.1.1.1,2.2.2.2"},
            {"category": 3, "name": "key_3", "value": "0:4.4.4.4,0:3.3.3.3"},
        ],
        "job_task_id": 12345,
        "is_tagged_ip": True,
        "biz_cc_id": 1,
        "biz_across": True,
    },
    parent_data={"executor": "executor_token", "biz_cc_id": 1},
    execute_assertion=ExecuteAssertion(
        success=True,
        outputs={
            "job_inst_url": "instance_url_token",
            "job_inst_id": 56789,
            "job_inst_name": "job_name_token",
            "client": EXECUTE_SUCCESS_CLIENT,
        },
    ),
    schedule_assertion=ScheduleAssertion(
        success=True,
        outputs={
            "job_inst_url": "instance_url_token",
            "job_inst_id": 56789,
            "job_inst_name": "job_name_token",
            "client": EXECUTE_SUCCESS_CLIENT,
            "job_tagged_ip_dict": {"tag": "1.1.1.1,1.1.1.2"},
            "key_1": "new_value_1",
            "key_2": "new_value_2",
            "log_outputs": {
                "key1": "value1",
                "key4": "   v   ",
                "key5": "  ",
                "key6": "v:v",
                "key2": "value2",
                "{key}": "v",
                "key3": "value3",
                "k": " v  ",
                "k1": " :v  ",
                "{key2}": "v",
                "{key3}": "var",
            },
        },
        callback_data={"job_instance_id": 56789, "status": 3},
    ),
    execute_call_assertion=[
        CallAssertion(
            func=CC_GET_IPS_INFO_BY_STR,
            calls=[Call(username="executor_token", biz_cc_id=1, ip_str="1.1.1.1,2.2.2.2", use_cache=False)],
        ),
        CallAssertion(
            func=EXECUTE_SUCCESS_CLIENT.jobv3.execute_job_plan,
            calls=[
                Call(
                    {
                        "bk_scope_type": "biz",
                        "bk_scope_id": "1",
                        "bk_biz_id": 1,
                        "job_plan_id": 12345,
                        "global_var_list": [
                            {"name": "key_1", "value": "value_1"},
                            {"name": "key_2", "value": "value_2"},
                            {
                                "name": "key_3",
                                "server": {
                                    "ip_list": [
                                        {"ip": "1.1.1.1", "bk_cloud_id": 1},
                                        {"ip": "2.2.2.2", "bk_cloud_id": 1},
                                    ],
                                },
                            },
                            {
                                "name": "key_3",
                                "server": {
                                    "ip_list": [
                                        {"ip": "4.4.4.4", "bk_cloud_id": "0"},
                                        {"ip": "3.3.3.3", "bk_cloud_id": "0"},
                                    ],
                                },
                            },
                        ],
                        "callback_url": "url_token",
                    }
                )
            ],
        ),
    ],
    schedule_call_assertion=[
        CallAssertion(
            func=EXECUTE_SUCCESS_CLIENT.jobv3.get_job_instance_global_var_value,
            calls=[Call({"bk_scope_type": "biz", "bk_scope_id": "1", "bk_biz_id": 1, "job_instance_id": 56789})],
        )
    ],
    patchers=[
        Patcher(target=GET_CLIENT_BY_USER, return_value=EXECUTE_SUCCESS_CLIENT),
        Patcher(
            target=CC_GET_IPS_INFO_BY_STR,
            return_value={"ip_result": [{"InnerIP": "1.1.1.1", "Source": 1}, {"InnerIP": "2.2.2.2", "Source": 1}]},
        ),
        Patcher(target=GET_NODE_CALLBACK_URL, return_value="url_token"),
        Patcher(target=GET_JOB_INSTANCE_URL, return_value="instance_url_token"),
    ],
)

GET_VAR_ERROR_SUCCESS_CASE = ComponentTestCase(
    name="v1.1 get var failed but execute result must be success",
    inputs={
        "job_global_var": [
            {"category": 1, "name": "key_1", "value": "value_1"},
            {"category": 1, "name": "key_2", "value": "value_2"},
            {"category": 3, "name": "key_3", "value": "1.1.1.1,2.2.2.2"},
        ],
        "job_task_id": 12345,
        "biz_cc_id": 1,
        "is_tagged_ip": True,
    },
    parent_data={"executor": "executor_token", "biz_cc_id": 1},
    execute_assertion=ExecuteAssertion(
        success=True,
        outputs={
            "job_inst_url": "instance_url_token",
            "job_inst_id": 56789,
            "job_inst_name": "job_name_token",
            "client": GET_VAR_ERROR_SUCCESS_CLIENT,
        },
    ),
    schedule_assertion=ScheduleAssertion(
        success=True,
        outputs={
            "job_inst_url": "instance_url_token",
            "job_inst_id": 56789,
            "job_inst_name": "job_name_token",
            "client": GET_VAR_ERROR_SUCCESS_CLIENT,
            "job_tagged_ip_dict": {"tag": "1.1.1.1,1.1.1.2"},
            "key_1": "new_value_1",
            "key_2": "new_value_2",
            "log_outputs": {
                "key1": "value1",
                "key4": "   v   ",
                "key5": "  ",
                "key6": "v:v",
                "key2": "value2",
                "{key}": "v",
                "key3": "value3",
                "k": " v  ",
                "k1": " :v  ",
                "{key2}": "v",
                "{key3}": "var",
            },
        },
        callback_data={"job_instance_id": 56789, "status": 3},
    ),
    execute_call_assertion=[
        CallAssertion(
            func=CC_GET_IPS_INFO_BY_STR,
            calls=[Call(username="executor_token", biz_cc_id=1, ip_str="1.1.1.1,2.2.2.2", use_cache=False)],
        ),
        CallAssertion(
            func=GET_VAR_ERROR_SUCCESS_CLIENT.jobv3.execute_job_plan,
            calls=[
                Call(
                    {
                        "bk_scope_type": "biz",
                        "bk_scope_id": "1",
                        "bk_biz_id": 1,
                        "job_plan_id": 12345,
                        "global_var_list": [
                            {"name": "key_1", "value": "value_1"},
                            {"name": "key_2", "value": "value_2"},
                            {
                                "name": "key_3",
                                "server": {
                                    "ip_list": [
                                        {"ip": "1.1.1.1", "bk_cloud_id": 1},
                                        {"ip": "2.2.2.2", "bk_cloud_id": 1},
                                    ],
                                },
                            },
                        ],
                        "callback_url": "url_token",
                    }
                )
            ],
        ),
    ],
    schedule_call_assertion=[
        CallAssertion(
            func=GET_VAR_ERROR_SUCCESS_CLIENT.jobv3.get_job_instance_global_var_value,
            calls=[Call({"bk_scope_type": "biz", "bk_scope_id": "1", "bk_biz_id": 1, "job_instance_id": 56789})],
        )
    ],
    patchers=[
        Patcher(target=GET_CLIENT_BY_USER, return_value=GET_VAR_ERROR_SUCCESS_CLIENT),
        Patcher(
            target=CC_GET_IPS_INFO_BY_STR,
            return_value={"ip_result": [{"InnerIP": "1.1.1.1", "Source": 1}, {"InnerIP": "2.2.2.2", "Source": 1}]},
        ),
        Patcher(target=GET_NODE_CALLBACK_URL, return_value="url_token"),
        Patcher(target=GET_JOB_INSTANCE_URL, return_value="instance_url_token"),
    ],
)

INVALID_IP_CASE = ComponentTestCase(
    name="v1.1 invalid ip case",
    inputs={
        "job_global_var": [
            {"category": 1, "name": "key_1", "value": "value_1"},
            {"category": 1, "name": "key_2", "value": "value_2"},
            {"category": 3, "name": "key_3", "value": "1.1.1.1,2.2.2.2"},
        ],
        "job_task_id": 12345,
        "biz_cc_id": 1,
    },
    parent_data={"executor": "executor_token", "biz_cc_id": 1},
    execute_assertion=ExecuteAssertion(
        success=False, outputs={"ex_data": "无法从配置平台(CMDB)查询到对应 IP，请确认输入的 IP 是否合法。查询失败 IP： 1.1.1.1,2.2.2.2"}
    ),
    schedule_assertion=None,
    execute_call_assertion=[
        CallAssertion(
            func=CC_GET_IPS_INFO_BY_STR,
            calls=[Call(username="executor_token", biz_cc_id=1, ip_str="1.1.1.1,2.2.2.2", use_cache=False)],
        ),
    ],
    patchers=[
        Patcher(target=GET_CLIENT_BY_USER, return_value=EXECUTE_SUCCESS_CLIENT),
        Patcher(target=CC_GET_IPS_INFO_BY_STR, return_value={"ip_result": []}),
    ],
)

IP_IS_EXIST_CASE = ComponentTestCase(
    name="v1.1 ip is exist case",
    inputs={
        "job_global_var": [
            {"category": 1, "name": "key_1", "value": "value_1"},
            {"category": 1, "name": "key_2", "value": "value_2"},
            {"category": 3, "name": "key_3", "value": "1.1.1.1,2.2.2.2"},
        ],
        "job_task_id": 12345,
        "biz_cc_id": 1,
        "ip_is_exist": True,
    },
    parent_data={"executor": "executor_token", "biz_cc_id": 1},
    execute_assertion=ExecuteAssertion(
        success=False, outputs={"ex_data": "无法从配置平台(CMDB)查询到对应 IP，请确认输入的 IP 是否合法。查询失败 IP： 1.1.1.1,2.2.2.2"}
    ),
    schedule_assertion=None,
    execute_call_assertion=[
        CallAssertion(
            func=CC_GET_IPS_INFO_BY_STR,
            calls=[Call(username="executor_token", biz_cc_id=1, ip_str="1.1.1.1,2.2.2.2", use_cache=False)],
        ),
    ],
    patchers=[
        Patcher(target=GET_CLIENT_BY_USER, return_value=EXECUTE_SUCCESS_CLIENT),
        Patcher(target=CC_GET_IPS_INFO_BY_STR, return_value={"ip_result": [{"InnerIP": "1.1.1.1", "Source": 1}]}),
    ],
)
