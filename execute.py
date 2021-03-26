#!/usr/bin/python
# coding:utf-8


from testplatform.models import Project, Environment, Interface, Case
import requests
import re
import json
from signtype import get_sign

class Execute():
    def __init__(self, case_id, env_id):
        self.case_id = case_id
        self.env_id = env_id
        #获取测试环境相关信息
        self.prj_id, self.env_url, self.private_key = self.get_env(self.env_id)
        #获取sign_type
        self.sign_type = self.get_sign(self.prj_id)

        self.extract_dict = {}
        self.glo_var = {}
        self.step_json = []

    def run_case(self):
        case = Case.objects.get(case_id=self.case_id)
        step_list = eval(case.content)
        case_run = {"case_id": self.case_id, "case_name": case.case_name, "result": "pass"}
        case_step_list = []

        for step in step_list:
            step_info = self.executecase(step)
            case_step_list.append(step_info)
            if step_info["result"] == "fail":
                case_run["result"] = "fail"
                break
            if step_info["result"] == "error":
                case_run["result"] = "error"
                break
        case_run["step_list"] = case_step_list
        return case_run




    def executecase(self, step_content):
        if_id = step_content["if_id"]
        interface = Interface.objects.get(if_id=if_id)
        #提取所有变量名，变量格式为$variable
        var_list = self.extract_variables(step_content)
        print(var_list)
        # 检查是否存在变量,有变量就替换成相关参数名提取的value值
        if var_list:
            for var_name in var_list:
                var_value = self.get_param(var_name, step_content)
                if var_value is None:
                    var_value = self.get_param(var_name, self.step_json)
                if var_value is None:
                    var_value = self.extract_dict[var_name]
                step_content = json.loads(self.replace_var(step_content, var_name, var_value))
        if_dict = {"url": interface.url, "header": step_content["header"], "body": step_content["body"]}
        # 签名
        if interface.is_sign:
            if_dict["body"] = get_sign(self.sign_type, if_dict["body"], self.private_key)
        if_dict["url"] = self.env_url + interface.url
        if_dict["if_id"] = if_id
        if_dict["if_name"] = step_content["if_name"]
        if_dict["method"] = interface.method
        if_dict["data_type"] = interface.data_type

        try:
            res = self.call_interface(if_dict["method"], if_dict["url"], if_dict["header"],
                                                 if_dict["body"], if_dict["data_type"])
            if_dict["res_status_code"] = res.status_code
            if_dict["res_content"] = res.text
        except requests.RequestException as e:
            if_dict["result"] = "Error"
            if_dict["msg"] = str(e)
            return if_dict
        #如果需要提取参数值，将参数和value放到self.extract_dict中
        if step_content["extract"]:
            self.get_extract(step_content["extract"], if_dict["res_content"])
        if step_content["validators"]:
            if_dict["result"], if_dict["msg"] = self.validators_result(step_content["validators"], if_dict["res_content"])
        else:
            if_dict["result"] = "pass"
            if_dict["msg"] = {}
        return if_dict



    # 验证结果
    def validators_result(self, validators_list, res):
        msg = ""
        result = ""
        for var_field in validators_list:
            check_filed = var_field["check"]
            expect_filed = var_field["expect"]
            check_filed_value = self.get_param(check_filed, res)
            if check_filed_value == expect_filed:
                result = "pass"
                msg = ""
            else:
                result = "fail"
                msg = "字段: " + check_filed + " 实际值为：" + str(check_filed_value) + " 与期望值：" + expect_filed + " 不符"
                break
        return result, msg

    # 在response中提取参数, 并放到列表中
    def get_extract(self, extract_dict, res):
        for key, value in extract_dict.items():
            key_value = self.get_param(key, res)
            self.extract_dict[key] = key_value




    # 替换内容中的变量, 返回字符串型
    def replace_var(self, content, var_name, var_value):
        if not isinstance(content, str):
            content = json.dumps(content)
        var_name = "$" + var_name
        content = content.replace(str(var_name), str(var_value))
        return content



    # 从内容中提取所有变量名, 变量格式为$variable,返回变量名list
    def extract_variables(self, content):
        variable_regexp = r"\$([\w_]+)"
        if not isinstance(content, str):
            content = str(content)
        try:
            return re.findall(variable_regexp, content)
        except TypeError:
            return []

    # 在内容中获取某一参数的值
    def get_param(self, param, content):
        param_val = None
        if isinstance(content, str):
            # content = json.loads(content)
            try:
                content = json.loads(content)
            except:
                content = ""
        if isinstance(content, dict):
            param_val = self.get_param_reponse(param, content)
        if isinstance(content, list):
            dict_data = {}
            for i in range(len(content)):
                try:
                    dict_data[str(i)] = eval(content[i])
                except:
                    dict_data[str(i)] = content[i]
            param_val = self.get_param_reponse(param, dict_data)
        if param_val is None:
            return param_val
        else:
            if "$" + param == param_val:
                param_val = None
            return param_val

    #返回字典某个参数的value值
    def get_param_reponse(self, param_name, dict_data, default=None):
        for k, v in dict_data.items():
            if k == param_name:
                return v
            else:
                if isinstance(v, dict):
                    ret = self.get_param_reponse(param_name, v)
                    if ret is not default:
                        return ret
                if isinstance(v, list):
                    for i in v:
                        if isinstance(i, dict):
                            ret = self.get_param_reponse(param_name, i)
                            if ret is not default:
                                return ret
                        else:
                            pass
        return default



    # 获取测试环境
    def get_env(self, env_id):
        env = Environment.objects.get(env_id=env_id)
        prj_id = env.project.prj_id
        return prj_id, env.url, env.private_key

    # 获取签名方式
    def get_sign(self, prj_id):
        """
        sign_type: 签名方式
        """
        prj = Project.objects.get(prj_id=prj_id)
        sign_type = prj.sign.sign_id
        return sign_type


    # 发送请求
    def call_interface(self, method, url, header, data, content_type='json'):
        print(url, header, data)
        if method == "post":
            if content_type == "json":
                res = requests.post(url=url, json=data, headers=header, verify=False)
            if content_type == "data":
                res = requests.post(url=url, data=data, headers=header, verify=False)
        if method == "get":
            res = requests.get(url=url, params=data, headers=header, verify=False)
        print(res.status_code, res.text)
        return res

if __name__=="__main__":
    execute = Execute(4, 1)
    aa={"if_id":"2","if_name":"测试接口2","header":{},"body":{},"extract":{"text":""},"validators":[{"check":"type","comparator":"eq","expect":"video"}]}
    # execute.step(aa)
    bb = {"if_id": "2", "if_name": "测试接口2", "header": {"userid":"$userid"}, "body": {}, "extract": {"text": "我是最棒的！"},
          "validators": [{"check": "type", "comparator": "eq", "expect": "video"}]}
    # print(execute.extract_variables(bb))
    #print(execute.get_param_reponse('comparator',bb))

    #print(execute.get_param('validators', bb))
    #print(execute.replace_var(bb,"userid","test"))
    # cc={"msg":""}
    dd={"code":0,"data":{"datetime":"2020-11-12 16:37:28","week":5,"month":11,"hour":16,"year":2020,"day":12,"timestamp":1605170248069,"minute":37,"second":28},"msg":"success"}
    # execute.get_extract(cc,dd)
    # print(execute.extract_dict)
    ee=[{"check":"msg","comparator":"eq","expect":"fail"}]

    print(execute.validators_result(ee,dd))

    # case_result = execute.run_case()