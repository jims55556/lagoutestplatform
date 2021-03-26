from django.shortcuts import render
from testplatform.models import Project, Sign, Environment, Interface, Case, Plan, Report
from django.http import HttpResponseRedirect, HttpResponse, JsonResponse
from django.contrib import messages
from execute import Execute
import time
from django.contrib import auth
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required


def index(request):
    return render(request, "login.html")


@login_required
def logout(request):
    ppp = auth.logout(request)
    return HttpResponseRedirect("/index/")




# Create your views here.
# 项目增删改查
def project_index(request):
    prj_list = Project.objects.all()
    return render(request, "testplatform/project/index.html", {"prj_list": prj_list})

#新增项目
def project_add(request):
    if request.method == 'POST':
        prj_name = request.POST['prj_name']
        name_same = Project.objects.filter(prj_name=prj_name)
        if name_same:
            messages.error(request, "项目已存在")
        else:
            description = request.POST['description']
            sign_id = request.POST['sign']
            sign = Sign.objects.get(sign_id=sign_id)
            prj = Project(prj_name=prj_name, description=description, sign=sign)
            prj.save()
            return HttpResponseRedirect("/testplatform/project/")
    sign_list = Sign.objects.all()
    return render(request, "testplatform/project/add.html", {"sign_list": sign_list})

#修改项目
def project_update(request):
    if request.method == 'POST':
        prj_id = request.POST['prj_id']
        prj_name = request.POST['prj_name']
        name_exit = Project.objects.filter(prj_name=prj_name).exclude(prj_id=prj_id)
        if name_exit:
            # messages.error(request, "项目已存在")
            return HttpResponse("项目已存在")
        else:
            description = request.POST['description']
            sign_id = request.POST['sign_id']
            sign = Sign.objects.get(sign_id=sign_id)
            Project.objects.filter(prj_id=prj_id).update(prj_name=prj_name, description=description,sign=sign)
            return HttpResponseRedirect("/testplatform/project/")
    prj_id = request.GET['prj_id']
    prj = Project.objects.get(prj_id=prj_id)
    sign_list = Sign.objects.all()
    return render(request, "testplatform/project/update.html", {"prj": prj, "sign_list": sign_list})

#删除项目
def project_delete(request):
    if request.method == 'GET':
        prj_id = request.GET['prj_id']
        Project.objects.filter(prj_id=prj_id).delete()
        return HttpResponseRedirect("testplatform/project/")


# 接口增删改查
def interface_index(request):
    if_list = Interface.objects.all()
    return render(request, "testplatform/interface/index.html", {"if_list": if_list})

#新增测试接口
def interface_add(request):
    if request.method == 'POST':
        if_name = request.POST['if_name']
        prj_id = request.POST['prj_id']
        project = Project.objects.get(prj_id=prj_id)
        url = request.POST['url']
        method = request.POST['method']
        data_type = request.POST['data_type']
        is_sign = request.POST['is_sign']
        description = request.POST['description']
        request_header_data = request.POST['request_header_data']
        request_body_data = request.POST['request_body_data']
        response_header_data = request.POST['response_header_data']
        response_body_data = request.POST['response_body_data']
        interface = Interface(if_name=if_name, url=url, project=project, method=method, data_type=data_type,
                          is_sign=is_sign, description=description, request_header_param=request_header_data,
                          request_body_param=request_body_data, response_header_param=response_header_data,
                          response_body_param=response_body_data)
        interface.save()
        return HttpResponseRedirect("/testplatform/interface/")
    prj_list = Project.objects.all()
    return render(request, "testplatform/interface/add.html", {"prj_list": prj_list})

#更新接口
def interface_update(request):
    if request.method == 'POST':
        env_id = request.POST['env_id']
        env_name = request.POST['env_name']
        prj_id = request.POST['prj_id']
        project = Project.objects.get(prj_id=prj_id)
        url = request.POST['url']
        private_key = request.POST['private_key']
        description = request.POST['description']
        Environment.objects.filter(env_id=env_id).update(env_name=env_name, url=url, project=project,
                                                         private_key=private_key, description=description)
        return HttpResponseRedirect("/testplatform/env/")
    if_id = request.GET['if_id']
    interface = Interface.objects.get(if_id=if_id)
    prj_list = Project.objects.all()
    return render(request, "testplatform/interface/update.html", {"interface": interface, "prj_list": prj_list})


#删除接口
def interface_delete(request):
    if request.method == 'GET':
        if_id = request.GET['if_id']
        Interface.objects.filter(if_id=if_id).delete()
        return HttpResponseRedirect("/testplatform/interface/")

# 测试用例增删改查
def case_index(request):
    case_list = Case.objects.all()
    return render(request, "testplatform/case/index.html", {"case_list": case_list})

#新增测试用例
def case_add(request):
    if request.method == 'POST':
        case_name = request.POST['case_name']
        prj_id = request.POST['prj_id']
        project = Project.objects.get(prj_id=prj_id)
        description = request.POST['description']
        content = request.POST['content']
        case = Case(case_name=case_name, project=project, description=description, content=content)
        case.save()
        return HttpResponseRedirect("/testplatform/case/")
    prj_list = Project.objects.all()
    return render(request, "testplatform/case/add.html", {"prj_list": prj_list})

#执行单个测试用例
def case_run(request):
    if request.method == 'POST':
        case_id = request.POST['case_id']
        env_id = request.POST['env_id']
        execute = Execute(case_id, env_id)
        case_result = execute.run_case()
        return JsonResponse(case_result)

# 计划增删改查
def plan_index(request):
    plan_list = Plan.objects.all()
    return render(request, "testplatform/plan/index.html", {"plan_list": plan_list})

# 新增计划
def plan_add(request):
    if request.method == 'POST':
        plan_name = request.POST['plan_name']
        prj_id = request.POST['prj_id']
        project = Project.objects.get(prj_id=prj_id)
        env_id = request.POST['env_id']
        environment = Environment.objects.get(env_id=env_id)
        description = request.POST['description']
        content = request.POST.getlist("case_id")
        plan = Plan(plan_name=plan_name, project=project, environment=environment, description=description, content=content)
        plan.save()
        return HttpResponseRedirect("/testplatform/plan/")
    prj_list = Project.objects.all()
    return render(request, "testplatform/plan/add.html", {"prj_list": prj_list})

#执行测试计划（批量运行测试用例）
def plan_run(request):
    if request.method == 'POST':
        plan_id = request.POST['plan_id']
        plan = Plan.objects.get(plan_id=plan_id)
        env_id = plan.environment.env_id
        case_id_list = eval(plan.content)
        case_num = len(case_id_list)
        content = []
        pass_num = 0
        fail_num = 0
        error_num = 0
        for case_id in case_id_list:
            execute = Execute(case_id, env_id)
            case_result = execute.run_case()
            content.append(case_result)
            if case_result["result"] == "pass":
                pass_num += 1
            if case_result["result"] == "fail":
                fail_num += 1
            if case_result["result"] == "error":
                error_num += 1
        report_name = plan.plan_name + "-" + time.strftime("%Y%m%d%H%M%S")
        if Report.objects.filter(plan=plan):
            Report.objects.filter(plan=plan).update(report_name=report_name, content=content, case_num=case_num,
                                                    pass_num=pass_num, fail_num=fail_num, error_num=error_num)
        else:
            report = Report(plan=plan, report_name=report_name, content=content, case_num=case_num,
                            pass_num=pass_num, fail_num=fail_num, error_num=error_num)
            report.save()
        return HttpResponse(plan.plan_name + " 执行成功！")


def report_index(request):
    plan_id = request.GET['plan_id']
    report = Report.objects.get(plan_id=plan_id)
    report_content = eval(report.content)
    return render(request, "report.html", {"report": report, "report_content": report_content})


def findata(request):
    if request.method == 'POST':
        pass
    if request.method == 'GET':
        get_type = request.GET["type"]
        if get_type == "get_all_if_by_prj_id":
            prj_id = request.GET["prj_id"]
            # 返回字典列表
            if_list = Interface.objects.filter(project=prj_id).all().values()
            # list(if_list)将QuerySet转换成list
            return JsonResponse(list(if_list), safe=False)
        if get_type == "get_if_by_if_id":
            if_id = request.GET["if_id"]
            # 查询并将结果转换为json
            interface = Interface.objects.filter(if_id=if_id).values()
            return JsonResponse(list(interface), safe=False)
        if get_type == "get_env_by_prj_id":
            prj_id = request.GET["prj_id"]
            # 查询并将结果转换为json
            env = Environment.objects.filter(project_id=prj_id).values()
            return JsonResponse(list(env), safe=False)
        if get_type == "get_all_case_by_prj_id":
            prj_id = request.GET["prj_id"]
            # 查询并将结果转换为json
            env = Case.objects.filter(project_id=prj_id).values()
            return JsonResponse(list(env), safe=False)

# 加密方式增删改查
def sign_index(request):
    sign_list = Sign.objects.all()
    return render(request, "testplatform/sign/sign_index.html", {"sign_list": sign_list})

#新增加密方式
def sign_add(request):
    if request.method == 'POST':
        sign_name = request.POST['sign_name']
        description = request.POST['description']
        sign = Sign(sign_name=sign_name, description=description)
        sign.save()
        return HttpResponseRedirect("/testplatform/sign/")
    return render(request, "testplatform/sign/sign_add.html")

# 更新加密方式
def sign_update(request):
    if request.method == 'POST':
        sign_id = request.POST['sign_id']
        sign_name = request.POST['sign_name']
        description = request.POST['description']
        Sign.objects.filter(sign_id=sign_id).update(sign_name=sign_name, description=description)
        return HttpResponseRedirect("/testplatform/sign/")
    sign_id = request.GET['sign_id']
    sign = Sign.objects.get(sign_id=sign_id)
    return render(request, "testplatform/sign/sign_update.html", {"sign": sign})

# 测试环境增删改查
def env_index(request):
    env_list = Environment.objects.all()
    return render(request, "testplatform/env/index.html", {"env_list": env_list})

# 新增测试环境
def env_add(request):
    if request.method == 'POST':
        env_name = request.POST['env_name']
        prj_id = request.POST['prj_id']
        project = Project.objects.get(prj_id=prj_id)
        url = request.POST['url']
        private_key = request.POST['private_key']
        description = request.POST['description']
        env = Environment(env_name=env_name, url=url, project=project,
                           private_key=private_key, description=description)
        env.save()
        return HttpResponseRedirect("/testplatform/env/")
    prj_list = Project.objects.all()
    return render(request, "testplatform/env/add.html", {"prj_list": prj_list})

# 测试环境更新
def env_update(request):
    if request.method == 'POST':
        env_id = request.POST['env_id']
        env_name = request.POST['env_name']
        prj_id = request.POST['prj_id']
        project = Project.objects.get(prj_id=prj_id)
        url = request.POST['url']
        private_key = request.POST['private_key']
        description = request.POST['description']
        Environment.objects.filter(env_id=env_id).update(env_name=env_name, url=url, project=project, private_key=private_key, description=description)
        return HttpResponseRedirect("/testplatform/env/")
    env_id = request.GET['env_id']
    env =Environment.objects.get(env_id=env_id)
    prj_list = Project.objects.all()
    return render(request, "testplatform/env/update.html", {"env": env, "prj_list": prj_list})

# 测试环境删除
def env_delete(request):
    if request.method == 'GET':
        env_id = request.GET['env_id']
        Environment.objects.filter(env_id=env_id).delete()
        return HttpResponseRedirect("/testplatform/env/")

#注册用户
def register(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        password2 = request.POST.get('password2')
        if password != password2:  # 判断两次密码是否相同
            message = "两次输入的密码不同！"
            return render(request, 'register.html', locals())
        user_obj = auth.authenticate(username=username, password=password)
        if not user_obj:
            User.objects.create_user(username=username, password= password)
            return HttpResponse("用户注册成功！")
        else:
            message = "用户名已经存在！"
            return render(request, 'register.html', locals())
    else:
        return render(request, "register.html")

#登录
def login(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user_obj = auth.authenticate(username=username, password=password)
        if not user_obj:
            return HttpResponseRedirect("/testplatform/login/")
        else:
            auth.login(request, user_obj)
            # path = request.GET.get("next") or "/indexnew/"
            # print(path)
            username = user_obj.username
            return  render(request, 'index.html', locals())
    else:
        return render(request, "login.html")
