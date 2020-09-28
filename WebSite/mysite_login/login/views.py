from django.shortcuts import render,redirect
from django.core.paginator import Paginator , PageNotAnInteger,EmptyPage
from . import models
from .forms import UserForm,Content,RegisterForm
import pymysql
import math
import random
import datetime
import os.path,shutil
import NAIS.NAIS as recommend

# Create your views here.
recommendNum=10



def login(request):
    if request.session.get('is_login',None):
        return redirect('/index')
    if request.method == "POST":
        login_form=UserForm(request.POST)
        message="请检查填写的内容！"

        # username = request.POST.get('username')
        # password = request.POST.get('password')
        if login_form.is_valid():
            username = login_form.cleaned_data['username']
            password = login_form.cleaned_data['password']
            try:
                user = models.User.objects.get(name=username)
                if user.password == password:
                    request.session['is_login'] = True
                    request.session['user_id'] = user.id
                    request.session['user_name'] = user.name
                    request.session['emai']=user.email
                    try:
                        content = models.Content.objects.get(name=username)
                        request.session['habit']=content.habit
                        request.session['address']=content.address
                    except:
                        pass
                    return redirect('/index/')
                else:
                    message = "密码不正确！"
            except:
                message = "用户不存在！"
        return render(request, 'login/login.html', locals())
    login_form=UserForm()
    return render(request, 'login/login.html',locals())


def register(request):
    if request.session.get('is_login', None):
        # 登录状态不允许注册。你可以修改这条原则！
        return redirect("/index/")
    if request.method == "POST":
        register_form = RegisterForm(request.POST)
        message = "请检查填写的内容！"
        if register_form.is_valid():  # 获取数据
            username = register_form.cleaned_data['username']
            password1 = register_form.cleaned_data['password1']
            password2 = register_form.cleaned_data['password2']
            email = register_form.cleaned_data['email']
            sex = register_form.cleaned_data['sex']
            if password1 != password2:  # 判断两次密码是否相同
                message = "两次输入的密码不同！"
                return render(request, 'login/register.html', locals())
            else:
                same_name_user = models.User.objects.filter(name=username)
                if same_name_user:  # 用户名唯一
                    message = '用户已经存在，请重新选择用户名！'
                    return render(request, 'login/register.html', locals())
                same_email_user = models.User.objects.filter(email=email)
                if same_email_user:  # 邮箱地址唯一
                    message = '该邮箱地址已被注册，请使用别的邮箱！'
                    return render(request, 'login/register.html', locals())
                # 当一切都OK的情况下，创建新用户
                new_user = models.User.objects.create()
                new_user.name = username
                new_user.password = password1
                new_user.email = email
                new_user.sex = sex
                new_user.save()
                return redirect('/login/')  # 自动跳转到登录页面
    register_form = RegisterForm()
    return render(request, 'login/register.html',locals())

def message(request):
    if request.method == "POST":
        content=Content(request.POST)
        message = "请检查填写的内容！"
        habit=request.POST.get('habit')
        address=request.POST.get('address')
        if habit is not None and address is not None:  # 获取数据
            username = request.session['user_name']
            # habit = content.cleaned_data['habit']
            # address = content.cleaned_data['address']
            # 当一切都OK的情况下，创建新用户
            new_habit = models.Content.objects.create()
            new_habit.name = username
            new_habit.habit=habit
            new_habit.address=address
            new_habit.save()
            request.session['habit']=habit
            request.session['address']=address
            return redirect('/login/')  # 自动跳转到登录页面
    content_form = Content()
    return render(request,'login/message.html',locals())

def change(request):
    if request.method == "POST":
        content=Content(request.POST)
        password=request.POST.get('password')
        password1=request.POST.get('password1')
        password2=request.POST.get('password2')
        username = request.session['user_name']
        if password==models.User.objects.get(name=username).password:
            if password2==password1:
                models.User.objects.filter(name=username).update(password=password1)
                return redirect('/logout/')
            else:
                message="前后密码不一致"
                return render(request, 'login/change.html', locals())
        else:
            message="密码错误"
            return render(request, 'login/change.html', locals())
    register_form = Content()
    login_form = UserForm()
    return render(request,'login/change.html',locals())

def logout(request):
    if not request.session.get('is_login', None):
        # 如果本来就未登录，也就没有登出一说
        return redirect("/index.html")
    request.session.flush()
    return redirect('/index.html')


def places(request,flag,type):
    if flag=="1":
        good_list = select2()
    elif flag=="2":
        good_list=selectbytype(type)
    elif flag=="3":
        if request.session.get('goodlist', None):
            good_list=request.session['goodlist']
        else:
            choice = request.POST.get('choice')
            content = request.POST.get('content')
            if choice == "name":
                good_list = selectbypartname(content)
                request.session['goodlist']=good_list
            elif choice == "type":
                good_list = selectbytype(content)
                request.session['goodlist']=good_list
            elif choice == "director":
                good_list = selectbydirector(content)
                request.session['goodlist']=good_list
            elif choice == "actor":
                good_list = selectbyactor(content)
                request.session['goodlist']=good_list
            else:
                pass
    else:
        pass
    # 值1：所有的数据
    # 值2：每一页的数据
    # 值3：当最后一页数据少于n条，将数据并入上一页
    if request.method=="POST":
        if request.session.get('is_login', None):
            pass
        else:
            login_message="请先登录，再进行高级搜索"
        if request.POST.get('order')=="默认排序":
            request.session['order']=request.POST.get('order')
            request.session['way']=request.POST.get('way')
            request.session['date_from']=None
            request.session['date_to']=None
        else:
            request.session['order']=request.POST.get('order')
            request.session['way']=request.POST.get('way')
            request.session['date_from']=request.POST.get('date_from')
            request.session['date_to']=request.POST.get('date_to')
    if request.session.get('is_login', None):
        order=request.session['order']
        way=request.session['way']
        date_from=request.session['date_from']
        date_to=request.session['date_to']
        if date_from is not None:
            date=date_from.split('/')
            if len(date)>1:
                date_from=date[2]+'-'+date[0]+'-'+date[1]
        if date_to is not None:
            date=date_to.split('/')
            if len(date)>1:
                date_to=date[2]+'-'+date[0]+'-'+date[1]
        if order is not None:
            if order=="时间":
                temp=[]
                if date_from is not None:
                    if date_to is not None:
                        for i in good_list:
                            if i['date']>=date_from and i['date']<=date_to:
                                temp.append(i)
                    else:
                        for i in good_list:
                            if i['date']>=date_from:
                                temp.append(i)
                else:
                    if date_to is not None:
                        for i in good_list:
                            if i['date']<=date_to:
                                temp.append(i)
                    else:
                        for i in good_list:
                            temp.append(i)
                if way=="升序":
                    good_list=sorted(temp,key=lambda temp:temp['date'])
                else:
                    good_list=sorted(temp,key=lambda temp:temp['date'],reverse=True)
            elif order=="收藏数":
                temp=[]
                for i in good_list:
                    movie_list=selectCommentbyMovie(i['name'])
                    count=0
                    for j in movie_list:
                        if j['collect']=="已收藏":
                            count=count+1
                    i['collect']=count
                    temp.append(i)
                if way=="升序":
                    good_list=sorted(temp,key=lambda temp:temp['collect'])
                else:
                    good_list=sorted(temp,key=lambda temp:temp['collect'],reverse=True)
            else:
                if way=="降序":
                    good_list.reverse()
    paginator = Paginator(good_list, 12)
    movie_num=len(good_list)
    if movie_num==0:
        message="无搜索结果"
    try:
        # GET请求方式，get()获取指定Key值所对应的value值
        # 获取index的值，如果没有，则设置使用默认值1
        num = request.GET.get('index', '1')
        # 获取第几页
        now=int(num)
        sum=math.ceil(len(good_list)/12)
        temp=sum-now
        if sum<5:
            pagerange=list(range(1,sum+1))
        elif temp<3:
            pagerange = list(range(sum-4, sum+1))
        elif now<3:
            pagerange = list(range(1, 6))
        else:
            pagerange=list(range(now-2,now+3))
        page = paginator.page(num)
    except PageNotAnInteger:
        # 如果输入的页码数不是整数，那么显示第一页数据
        page = paginator.page(1)
    except EmptyPage:
        page = paginator.page(paginator.num_pages)

    # 将当前页页码，以及当前页数据传递到index.html
    return render(request, "places.html",locals())

def home(request,flag):
    if flag=="1":
        flag_movie="1"
        good_list = selectCommentbyUser(request.session['user_name'])
        collectCount=0
        commentCount=0
        for i in good_list:
            if i['collect'] == "已收藏":
                collectCount+=1
            if i['comment'] is not None:
                commentCount+=1
        return render(request, "home.html", locals())
    elif flag=="2":
        good_list=selectCommentbyUser(request.session['user_name'])
        temp=[]
        for i in good_list:
            if i['collect']=="已收藏":
                temp.append(i)
        good_list=temp
        # print(good_list)
    elif flag=="3":
        good_list=selectCommentbyUser(request.session['user_name'])
        temp=[]
        for i in good_list:
            if i['comment'] is not None:
                temp.append(i)
        good_list=temp
    else:
        pass
    # 值1：所有的数据
    # 值2：每一页的数据
    # 值3：当最后一页数据少于n条，将数据并入上一页

    paginator = Paginator(good_list, 9)
    movie_num=len(good_list)
    if movie_num==0:
        message="尚无记录"
    try:
        # GET请求方式，get()获取指定Key值所对应的value值
        # 获取index的值，如果没有，则设置使用默认值1
        num = request.GET.get('index', '1')
        # 获取第几页
        now=int(num)
        sum=math.ceil(len(good_list)/9)
        temp=sum-now
        if sum<5:
            pagerange=list(range(1,sum+1))
        elif temp<3:
            pagerange = list(range(sum-4, sum+1))
        elif now<3:
            pagerange = list(range(1, 6))
        else:
            pagerange=list(range(now-2,now+3))
        page = paginator.page(num)
    except PageNotAnInteger:
        # 如果输入的页码数不是整数，那么显示第一页数据
        page = paginator.page(1)
    except EmptyPage:
        page = paginator.page(paginator.num_pages)

    # 将当前页页码，以及当前页数据传递到index.html
    return render(request, "home.html",locals())

def admin_home(request,flag):
    if flag=="1":
        flag_home=True
        return render(request,"admin_home.html",locals())
    elif flag=="2":
        if request.method=="POST":
            for user in selectuser():
                if request.POST.get(user['name'])==user['name']:
                    updateUserStatus(user['name'])
        flag_usermanage=True
        good_list = selectuser()
    elif flag=="3":
        flag_commentmanage=True
        if request.method=="POST":
            for comment in selectCommentbyReview():
                if request.POST.get(str(comment['id']))=="pass":
                    updateCommentStatus(comment['id'],"已通过")
                elif request.POST.get(str(comment['id']))=="refuse":
                    updateCommentStatus(comment['id'],"未通过")
                else:
                    pass
        good_list=selectCommentbyReview()
    elif flag=="4":
        flag_insertmovie=True
        good_list=[]
        if request.method=="POST":
            dic = {}
            dic['movieid'] = request.POST.get('movieid')
            dic['name'] = request.POST.get('name')
            dic['director'] = request.POST.get('director')
            dic['writer'] = request.POST.get('writer')
            dic['actors'] = request.POST.get('actors')
            dic['type'] = request.POST.get('type')
            dic['date'] = request.POST.get('date')
            dic['timelong'] = request.POST.get('timelong')
            dic['IMDburl'] = request.POST.get('IMDburl')
            dic['introduction'] = request.POST.get('introduction')
            dic['trailerurl'] = request.POST.get('trailerurl')
            dic['movieurl'] = request.POST.get('movieurl')
            file_obj = request.FILES.get('file')
            models.Picture.objects.create(name=dic['name'], img=file_obj)
            shutil.move("mysite_login//static//cover//img//" + str(file_obj),"mysite_login//static//cover//" + dic['name'] + ".jpg")
            insertMovie(dic)
            type=dic['type'].split(' ')
            typeEng=[]
            with open('mysite_login/NAIS/ml-latest/typeMapTable.txt','r',encoding='utf-8') as f:
                line=f.readline()
                while line is not None and line!='':
                    for i in type:
                        if i==line.split('::')[1].rstrip('\n'):
                            typeEng.append(line.split('::')[0])
                            break
                    line=f.readline()
            typeEng1=[]
            typeEng1.append(typeEng)
            print(typeEng1)
            recommend.getNewItem(typeEng1)
            file = open('mysite_login/NAIS/ml-latest/moviesType.txt', 'a')
            data = ''
            data = dic['movieid'] + '::' + dic['name'] + '::'
            for i in typeEng:
                if i != typeEng[-1]:
                    data = data + i + '|'
            data = data + typeEng[-1]
            file.write(data + '\n')
            return redirect('/search_result.html/1/'+dic['name'])
    else:
        pass
    paginator = Paginator(good_list, 9)
    num_list = len(good_list)
    if num_list == 0:
        message = "尚无记录"
    try:
        # GET请求方式，get()获取指定Key值所对应的value值
        # 获取index的值，如果没有，则设置使用默认值1
        num = request.GET.get('index', '1')
        # 获取第几页
        now = int(num)
        sum = math.ceil(len(good_list) / 9)
        temp = sum - now
        if sum < 5:
            pagerange = list(range(1, sum + 1))
        elif temp < 3:
            pagerange = list(range(sum - 4, sum + 1))
        elif now < 3:
            pagerange = list(range(1, 6))
        else:
            pagerange = list(range(now - 2, now + 3))
        page = paginator.page(num)
    except PageNotAnInteger:
        # 如果输入的页码数不是整数，那么显示第一页数据
        page = paginator.page(1)
    except EmptyPage:
        page = paginator.page(paginator.num_pages)

    # 将当前页页码，以及当前页数据传递到index.html
    return render(request, "admin_home.html", locals())

def search_result(request,flag,moviename):
    movie_data = selectbyname1(moviename)
    list=recommend.recommendByMovie(movie_data['movieid'])
    print(movie_data['movieid'])
    print(list)
    recommend_list=[]
    recommend_count=0
    for i in list:
        if recommend_count==recommendNum:
            break
        if checkMovie(i):
            recommend_list.append(i)
            recommend_count+=1
    print(recommend_list)
    recommend_list = selectbyId(recommend_list)
    if request.session.get('user_id',None):
        print(request.session['user_id'])
        insertInteraction(request.session['user_id'],movie_data['movieid'])
    elif request.session.get('user_name',None):
        if request.session['user_name']=='test0':
            print(0)
            insertInteraction(0, movie_data['movieid'])
    if flag=="1":
        movie_data=selectbyname1(moviename)#此处可删除进行优化
        if request.session.get('is_login',None):
            flag_collect =selectcollect(request.session['user_name'],moviename)
            if request.method=="POST":
                comment=request.POST.get('comment')
                insertcomment(request.session['user_name'],moviename,comment,datetime.datetime.now().strftime('%Y-%m-%d'))
            comment_data=selectCommentbyMovie(moviename)
            count_collect=0
            temp=[]
            for i in comment_data:
                if i['status']=="已通过":
                    temp.append(i)
                if i['collect']=="已收藏":
                    count_collect=count_collect+1
                if i['username']==request.session['user_name']:
                    if i['status']=="未审核":
                        comment_old_review=True
                    elif i['status']=="未通过":
                        comment_old_refuse=True
                    comment_old=i['comment']
            comment_data=temp
        else:
            comment_data = []
            for i in selectCommentbyMovie(moviename):
                if i['status']=="已通过":
                    comment_data.append(i)
    elif flag=="2":
        movie_data = selectbyname1(moviename)
        if request.session.get('is_login', None):
            updatecollect(request.session['user_name'], moviename)
            flag_collect = selectcollect(request.session['user_name'], moviename)
            if request.method == "POST":
                comment = request.POST.get('comment')
                insertcomment(request.session['user_name'], moviename,comment,
                              datetime.datetime.now().strftime('%Y-%m-%d'))
            comment_data = selectCommentbyMovie(moviename)
            count_collect=0
            temp=[]
            for i in comment_data:
                if i['status']=="已通过":
                    temp.append(i)
                if i['collect']=="已收藏":
                    count_collect=count_collect+1
                if i['username'] == request.session['user_name']:
                    if i['status']=="未审核":
                        comment_old_review=True
                    elif i['status']=="未通过":
                        comment_old_refuse=True
                    comment_old = i['comment']
            comment_data=temp
        else:
            comment_data = []
            for i in selectCommentbyMovie(moviename):
                if i['status'] == "已通过":
                    comment_data.append(i)
    elif flag=="3":
        movie_data = selectbyname1(moviename)
        moviechange_flag=1
        if request.session.get('is_admin', None):
            flag_collect = selectcollect(request.session['user_name'], moviename)
            if request.method == "POST":
                dic={}
                dic['name'] = request.POST.get('name')
                dic['director'] = request.POST.get('director')
                dic['writer'] = request.POST.get('writer')
                dic['actors'] = request.POST.get('actors')
                dic['type'] = request.POST.get('type')
                dic['date'] = request.POST.get('date')
                dic['timelong'] = request.POST.get('timelong')
                dic['IMDburl'] = request.POST.get('IMDburl')
                dic['introduction'] = request.POST.get('introduction')
                dic['trailerurl'] = request.POST.get('trailerurl')
                dic['movieurl'] = request.POST.get('movieurl')
                updateMovie(movie_data['movieid'],dic)
                return redirect('/search_result.html/1/' + dic['name'])
            comment_data = []
            for i in selectCommentbyMovie(moviename):
                if i['status'] == "已通过":
                    comment_data.append(i)
        else:
            message="您无权访问此处"

    else:
        message="输入有误"
    return render(request,"search_result.html",locals())


def contact(request):
    if request.session.get('is_login', None):
        return redirect('index.html')
    if request.method == "POST":
        message = "请检查填写的内容！"

        username = request.POST.get('username')
        password = request.POST.get('password')
        identity=request.POST.get('identity')
        if username is not None and password is not None and identity is not None:
            if identity=="admin":
                try:
                    admin = models.Admin.objects.get(name=username)
                    if admin.password == password:
                        request.session['is_login'] = True
                        request.session['is_admin']=True
                        request.session['user_name'] = admin.name
                        request.session['status']=True
                        request.session['order'] = "默认排序"
                        request.session['way'] = "升序"
                        request.session['date_from'] = None
                        request.session['date_to'] = None
                        return redirect('/admin_home.html/1')
                    else:
                        message = "密码不正确！"
                except:
                    message = "管理员不存在！"
            else:
                try:
                    user = models.User.objects.get(name=username)
                    if user.password == password:
                        request.session['is_login'] = True
                        request.session['user_id'] = user.id
                        request.session['user_name'] = user.name
                        if user.status=="正常":
                            request.session['status']=True
                        request.session['order'] = "默认排序"
                        request.session['way'] = "升序"
                        request.session['date_from'] = None
                        request.session['date_to'] = None
                        try:
                            content = models.Content.objects.get(name=username)
                            request.session['habit'] = content.habit
                            request.session['address'] = content.address
                        except:
                            pass
                        return redirect('/index.html')
                    else:
                        message = "密码不正确！"
                except:
                    message = "用户不存在！"
        return render(request, 'contact.html', locals())
    register_form = RegisterForm()
    return render(request, "contact.html",locals())

def index1(request):
    request.session['goodlist']=None
    if request.session.get('is_admin', None):
        recommend_list=[1,2,3,4,5,6,7,8,9,0]
        recommend_list=selectbyId(recommend_list)
    elif request.session.get('is_login', None):
        list = recommend.recommendByUser(request.session['user_id'])
        print(list)
        recommend_list = []
        recommend_count = 0
        for i in list:
            if recommend_count == recommendNum:
                break
            if checkMovie(i):
                recommend_list.append(i)
                recommend_count += 1
        print(recommend_list)
        recommend_list = selectbyId(recommend_list)

    movie_feature_all=selectbytype("剧情")
    count_feature=random.sample(range(0,len(movie_feature_all)),5)
    movie_feature=[]
    for i in count_feature:
        movie_feature.append(movie_feature_all[i])
    # movie_war_all = selectbytype("战争")
    # count_war = random.sample(range(0, len(movie_war_all)), 5)
    # movie_war = []
    # for i in count_war:
    #     movie_war.append(movie_war_all[i])
    movie_act_all = selectbytype("动作")
    count_act = random.sample(range(0, len(movie_act_all)), 5)
    movie_act = []
    for i in count_act:
        movie_act.append(movie_act_all[i])
    movie_science_all = selectbytype("科幻")
    count_science = random.sample(range(0, len(movie_science_all)), 5)
    movie_science = []
    for i in count_science:
        movie_science.append(movie_science_all[i])
    movie_horrible_all = selectbytype("恐怖")
    count_horrible = random.sample(range(0, len(movie_horrible_all)), 5)
    movie_horrible = []
    for i in count_horrible:
        movie_horrible.append(movie_horrible_all[i])
    movie_love_all = selectbytype("爱情")
    count_love = random.sample(range(0, len(movie_love_all)), 5)
    movie_love = []
    for i in count_love:
        movie_love.append(movie_love_all[i])
    movie_panic_all = selectbytype("惊悚")
    count_panic = random.sample(range(0, len(movie_panic_all)), 5)
    movie_panic = []
    for i in count_panic:
        movie_panic.append(movie_panic_all[i])
    movie_comedy_all = selectbytype("喜剧")
    count_comedy = random.sample(range(0, len(movie_comedy_all)), 5)
    movie_comedy = []
    for i in count_comedy:
        movie_comedy.append(movie_comedy_all[i])
    return render(request, "index.html",locals())

def register1(request):
    if request.session.get('is_login', None):
        # 登录状态不允许注册。你可以修改这条原则！
        return redirect("index.html")
    if request.method == "POST":
        username = request.POST.get('username')
        password1 = request.POST.get('password1')
        password2 = request.POST.get('password2')
        email = request.POST.get('email')
        sex = request.POST.get('sex')
        message = "请检查填写的内容！"
        if username is not None and password1 is not None and password2 is not None and email is not None and sex is not None:  # 获取数据
            if password1 != password2:  # 判断两次密码是否相同
                message = "两次输入的密码不同！"
                return render(request, 'register.html', locals())
            else:
                same_name_user = models.User.objects.filter(name=username)
                if same_name_user:  # 用户名唯一
                    message = '用户已经存在，请重新选择用户名！'
                    return render(request, 'register.html', locals())
                same_email_user = models.User.objects.filter(email=email)
                if same_email_user:  # 邮箱地址唯一
                    message = '该邮箱地址已被注册，请使用别的邮箱！'
                    return render(request, 'register.html', locals())
                # 当一切都OK的情况下，创建新用户
                new_user = models.User.objects.create()
                new_user.name = username
                new_user.password = password1
                new_user.email = email
                new_user.sex = sex
                new_user.save()
                return redirect('contact.html')  # 自动跳转到登录页面
    register_form = RegisterForm()
    return render(request, 'register.html',locals())

def change1(request):
    if request.method == "POST":
        content=Content(request.POST)
        password=request.POST.get('password')
        password1=request.POST.get('password1')
        password2=request.POST.get('password2')
        username = request.session['user_name']
        if password==models.User.objects.get(name=username).password:
            if password2==password1:
                models.User.objects.filter(name=username).update(password=password1)
                return redirect('/logout/')
            else:
                message="两次输入的密码不同！"
                return render(request, 'change.html', locals())
        else:
            message="旧密码错误！"
            return render(request, 'change.html', locals())
    register_form = Content()
    login_form = UserForm()
    return render(request,'change.html',locals())

def delete_comment(request,moviename,id):
    db = pymysql.connect("localhost", "root", "123456", "data")
    # 使用cursor()方法获取操作游标
    cursor = db.cursor()
    sql = "delete from comment where id = '{}'".format(id)
    try:
        # 执行sql语句
        cursor.execute(sql)
        # 提交到数据库执行
        db.commit()
        print("数据修改成功")
    except:
        # 如果发生错误则回滚
        db.rollback()
        # 关闭数据库连接
    db.close()
    return redirect('/search_result.html/1/'+moviename)

def select1():
    # 打开数据库连接
    db = pymysql.connect("localhost", 'root', '123456', 'data')
    # 获取游标
    cursor = db.cursor()
    # SQL 查询语句
    sql = "select * from movie"
    try:
        cursor.execute(sql)
        result = cursor.fetchall()  # 获取查询内容
        data=[]
        for list in result:
            dic = {}
            dic['top']=list[0]
            dic['name'] = list[1]
            dic['director'] = list[2]
            dic['writer'] = list[3]
            dic['actors'] = list[4]
            dic['type'] = list[5]
            dic['date'] = list[6]
            dic['timelong'] = list[7]
            dic['IMDburl'] = list[8]
            dic['introduction'] = list[9]
            dic['trailerurl'] = list[10]
            dic['movieurl'] = list[11]
            data.append(dic)
        # print(data)
    except:
        print("数据查询异常")
        db.rollback()  # 回滚
    db.close()
    return data

def select2():
    # 打开数据库连接
    db = pymysql.connect("localhost", 'root', '123456', 'data')
    # 获取游标
    cursor = db.cursor()
    # SQL 查询语句
    sql = "select * from movie3"
    try:
        cursor.execute(sql)
        result = cursor.fetchall()  # 获取查询内容
        data=[]
        for list in result:
            dic = {}
            dic['name'] = list[0]
            dic['director'] = list[1]
            dic['writer'] = list[2]
            dic['actors'] = list[3]
            dic['type'] = list[4]
            dic['date'] = list[5]
            dic['timelong'] = list[6]
            dic['IMDburl'] = list[7]
            dic['introduction'] = list[8]
            dic['trailerurl'] = list[9]
            dic['movieurl'] = list[10]
            data.append(dic)
        # print(data)
    except:
        print("数据查询异常")
        db.rollback()  # 回滚
    db.close()
    return data

def selectuser():
    db = pymysql.connect("localhost", 'root', '123456', 'testdatabase')
    # 获取游标
    cursor = db.cursor()
    # SQL 查询语句
    sql = "select * from login_user"
    try:
        cursor.execute(sql)
        result = cursor.fetchall()  # 获取查询内容
        data=[]
        for list in result:
            dic = {}
            dic['name'] = list[1]
            dic['email'] = list[3]
            dic['sex'] = list[4]
            dic['time'] = list[5].strftime("%Y-%m-%d %H:%M:%S")
            dic['status']=list[6]
            data.append(dic)
    except:
        print("数据查询异常")
        db.rollback()  # 回滚
    db.close()
    return data

def selectbyname1(str):
    # 打开数据库连接
    db = pymysql.connect("localhost", 'root', '123456', 'data')
    # 获取游标
    cursor = db.cursor()
    # SQL 查询语句
    sql = "select * from movie3 where name = '{}'".format(str)
    try:
        cursor.execute(sql)
        result = cursor.fetchall()  # 获取查询内容
        dic={}
        dic['name'] = result[0][0]
        dic['director'] = result[0][1]
        dic['writer'] = result[0][2]
        dic['actors'] = result[0][3]
        dic['type'] = result[0][4]
        dic['date'] = result[0][5]
        dic['timelong'] = result[0][6]
        dic['IMDburl'] = result[0][7]
        dic['introduction'] = result[0][8]
        dic['trailerurl'] = result[0][9]
        dic['movieurl'] = result[0][10]
        dic['movieid']=result[0][11]
    except:
        print("数据查询异常")
        db.rollback()  # 回滚
    db.close()
    return dic

def selectbyId(list):
    # 打开数据库连接
    db = pymysql.connect("localhost", 'root', '123456', 'data')
    # 获取游标
    cursor = db.cursor()
    # SQL 查询语句
    data=[]
    try:
        for id in list:
            sql="select * from movie3 where movieid = '{}'".format(id)
            cursor.execute(sql)
            dic={}
            result = cursor.fetchall()  # 获取查询内容
            dic['name'] = result[0][0]
            dic['director'] = result[0][1]
            dic['writer'] = result[0][2]
            dic['actors'] = result[0][3]
            dic['type'] = result[0][4]
            dic['date'] = result[0][5]
            dic['timelong'] = result[0][6]
            dic['IMDburl'] = result[0][7]
            dic['introduction'] = result[0][8]
            dic['trailerurl'] = result[0][9]
            dic['movieurl'] = result[0][10]
            dic['movieid']=result[0][11]
            data.append(dic)
    except:
        print("数据查询异常")
        db.rollback()  # 回滚
    db.close()
    return data

def selectbypartname(str):
    # 打开数据库连接
    db = pymysql.connect("localhost", 'root', '123456', 'data')
    # 获取游标
    cursor = db.cursor()
    # SQL 查询语句
    sql = "select * from movie3 where name like '%{}%'".format(str)
    try:
        cursor.execute(sql)
        result = cursor.fetchall()  # 获取查询内容
        data=[]
        for list in result:
            dic = {}
            dic['name'] = list[0]
            dic['director'] = list[1]
            dic['writer'] = list[2]
            dic['actors'] = list[3]
            dic['type'] = list[4]
            dic['date'] = list[5]
            dic['timelong'] = list[6]
            dic['IMDburl'] = list[7]
            dic['introduction'] = list[8]
            dic['trailerurl'] = list[9]
            dic['movieurl'] = list[10]
            data.append(dic)
        # print(data)
    except:
        print("数据查询异常")
        db.rollback()  # 回滚
    db.close()
    return data

def selectbytype(str):
    # 打开数据库连接
    db = pymysql.connect("localhost", 'root', '123456', 'data')
    # 获取游标
    cursor = db.cursor()
    # SQL 查询语句
    sql = "select * from movie3 where type like '%{}%'".format(str)
    try:
        cursor.execute(sql)
        result = cursor.fetchall()  # 获取查询内容
        data=[]
        for list in result:
            dic = {}
            dic['name'] = list[0]
            dic['director'] = list[1]
            dic['writer'] = list[2]
            dic['actors'] = list[3]
            dic['type'] = list[4]
            dic['date'] = list[5]
            dic['timelong'] = list[6]
            dic['IMDburl'] = list[7]
            dic['introduction'] = list[8]
            dic['trailerurl'] = list[9]
            dic['movieurl'] = list[10]
            data.append(dic)
        # print(data)
    except:
        print("数据查询异常")
        db.rollback()  # 回滚
    db.close()
    return data

def selectbydirector(str):
    # 打开数据库连接
    db = pymysql.connect("localhost", 'root', '123456', 'data')
    # 获取游标
    cursor = db.cursor()
    # SQL 查询语句
    sql = "select * from movie3 where director like '%{}%'".format(str)
    try:
        cursor.execute(sql)
        result = cursor.fetchall()  # 获取查询内容
        data=[]
        for list in result:
            dic = {}
            dic['name'] = list[0]
            dic['director'] = list[1]
            dic['writer'] = list[2]
            dic['actors'] = list[3]
            dic['type'] = list[4]
            dic['date'] = list[5]
            dic['timelong'] = list[6]
            dic['IMDburl'] = list[7]
            dic['introduction'] = list[8]
            dic['trailerurl'] = list[9]
            dic['movieurl'] = list[10]
            data.append(dic)
        # print(data)
    except:
        print("数据查询异常")
        db.rollback()  # 回滚
    db.close()
    return data

def selectbyactor(str):
    # 打开数据库连接
    db = pymysql.connect("localhost", 'root', '123456', 'data')
    # 获取游标
    cursor = db.cursor()
    # SQL 查询语句
    sql = "select * from movie3 where actors like '%{}%'".format(str)
    try:
        cursor.execute(sql)
        result = cursor.fetchall()  # 获取查询内容
        data=[]
        for list in result:
            dic = {}
            dic['name'] = list[0]
            dic['director'] = list[1]
            dic['writer'] = list[2]
            dic['actors'] = list[3]
            dic['type'] = list[4]
            dic['date'] = list[5]
            dic['timelong'] = list[6]
            dic['IMDburl'] = list[7]
            dic['introduction'] = list[8]
            dic['trailerurl'] = list[9]
            dic['movieurl'] = list[10]
            data.append(dic)
        # print(data)
    except:
        print("数据查询异常")
        db.rollback()  # 回滚
    db.close()
    return data

def selectCommentbyMovie(moviename):
    # 打开数据库连接
    db = pymysql.connect("localhost", 'root', '123456', 'data')
    # 获取游标
    cursor = db.cursor()
    # SQL 查询语句
    sql = "select * from comment where moviename = '{}'".format(moviename)
    data = []
    try:
        cursor.execute(sql)
        result = cursor.fetchall()  # 获取查询内容
        for list in result:
            dic = {}
            dic['username'] = list[0]
            dic['collect']=list[2]
            dic['comment'] = list[3]
            dic['time'] = list[4]
            dic['status']=list[5]
            dic['id']=list[6]
            data.append(dic)
        # print(data)
    except:
        print("数据查询异常")
        db.rollback()  # 回滚
    db.close()
    return data

def selectCommentbyReview():
    # 打开数据库连接
    db = pymysql.connect("localhost", 'root', '123456', 'data')
    # 获取游标
    cursor = db.cursor()
    # SQL 查询语句
    sql = "select * from comment where status='未审核' order by date desc"
    try:
        cursor.execute(sql)
        result = cursor.fetchall()  # 获取查询内容
        data=[]
        for list in result:
            dic = {}
            dic['username'] = list[0]
            dic['moviename']=list[1]
            dic['collect']=list[2]
            dic['comment'] = list[3]
            dic['time'] = list[4]
            dic['status']=list[5]
            dic['id']=list[6]
            data.append(dic)
        # print(data)
    except:
        print("数据查询异常")
        db.rollback()  # 回滚
    db.close()
    return data

def selectCommentbyUser(username):
    # 打开数据库连接
    db = pymysql.connect("localhost", 'root', '123456', 'data')
    # 获取游标
    cursor = db.cursor()
    # SQL 查询语句
    sql = "select * from comment where username = '{}'".format(username)
    try:
        cursor.execute(sql)
        result = cursor.fetchall()  # 获取查询内容
        data=[]
        for list in result:
            dic = {}
            dic['moviename'] = list[1]
            dic['collect']=list[2]
            dic['comment'] = list[3]
            dic['time'] = list[4]
            dic['status']=list[5]
            data.append(dic)
        # print(data)
    except:
        print("数据查询异常")
        db.rollback()  # 回滚
    db.close()
    return data

def insertcomment(username, moviename,comment, date):
    # 打开数据库连接
    db = pymysql.connect("localhost", "root", "123456", "data")
    # 使用cursor()方法获取操作游标
    cursor = db.cursor()
    # 电影简介内容出现""双引号 无法直接插入数据表中 需要进行处理
    # 使用正则替换，便可以插入数据表中
    # SQL 插入语句
    sql = "INSERT INTO comment (username, moviename,collect,comment,date,status) VALUES ('{}', '{}','{}','{}','{}','{}')"\
        .format(username, moviename,"未收藏",comment,date,"未审核")
    # SQL 查询语句
    sql2 = "select * from comment where username='{}' and moviename='{}'".format(username,moviename)
    sql3="update comment set comment = '{}',date = '{}',status='{}' where username='{}' and moviename='{}'"\
        .format(comment,date,"未审核",username,moviename)
    try:
        # 执行sql语句
        cursor.execute(sql2)
        # 提交到数据库执行
        result = cursor.fetchall()
        if len(result) == 0:
            cursor.execute(sql)
        # 提交到数据库执行
            db.commit()
        else:
            cursor.execute(sql3)
            # 提交到数据库执行
            db.commit()
        print("数据插入成功")
    except:
        # 如果发生错误则回滚
        db.rollback()
        # 关闭数据库连接
    db.close()

def insertInteraction(userId,movieId):
    db = pymysql.connect("localhost", "root", "123456", "data")
    # 使用cursor()方法获取操作游标
    cursor = db.cursor()
    # 电影简介内容出现""双引号 无法直接插入数据表中 需要进行处理
    # 使用正则替换，便可以插入数据表中
    # SQL 插入语句
    sql1 = "INSERT INTO interaction (movieId, userId,date) VALUES ({},{},'{}')" \
        .format(movieId, userId,datetime.datetime.now().strftime('%Y-%m-%d'))
    # SQL 查询语句
    sql2 = "select * from interaction where userId='{}' and movieId='{}'".format(userId, movieId)
    try:
        # 执行sql语句
        cursor.execute(sql2)
        # 提交到数据库执行
        result = cursor.fetchall()
        if len(result) == 0:
            cursor.execute(sql1)
            # 提交到数据库执行
            db.commit()
            print("数据插入成功")
    except:
        # 如果发生错误则回滚
        db.rollback()
        # 关闭数据库连接
    db.close()

def insertMovie(dic):
    db = pymysql.connect("localhost", "root", "123456", "data")
    # 使用cursor()方法获取操作游标
    cursor = db.cursor()
    # 电影简介内容出现""双引号 无法直接插入数据表中 需要进行处理
    # 使用正则替换，便可以插入数据表中
    # SQL 插入语句
    sql = """INSERT INTO movie3 (name,director,writer,actors,type,date,timelong,IMDburl,introduction,trailerurl,movieurl,movieid) 
        VALUES ("{}","{}","{}","{}","{}","{}","{}","{}","{}","{}","{}",{})""" \
        .format(dic['name'], dic['director'], dic['writer'], dic['actors'], dic['type'], dic['date'],
                dic['timelong'], dic['IMDburl'], dic['introduction'], dic['trailerurl'], dic['movieurl'],dic['movieid'])
    sql2 = "select name from movie3 where name='{}'".format(dic['name'])
    try:
        # 执行sql语句
        cursor.execute(sql2)
        # 提交到数据库执行
        result = cursor.fetchall()
        if len(result) == 0:
            # 执行sql语句
            cursor.execute(sql)
            # 提交到数据库执行
            db.commit()
            print("数据插入成功")
        else:
            print("数据表中记录已存在")
    except:
        # 如果发生错误则回滚
        print("数据插入失败")
        db.rollback()
    # 关闭数据库连接
    db.close()

def selectcollect(username,moviename):
    db = pymysql.connect("localhost", "root", "123456", "data")
    # 使用cursor()方法获取操作游标
    cursor = db.cursor()
    # 电影简介内容出现""双引号 无法直接插入数据表中 需要进行处理
    # 使用正则替换，便可以插入数据表中
    # SQL 插入语句
    # SQL 查询语句
    sql1 = "select * from comment where username='{}' and moviename='{}'".format(username, moviename)
    try:
        # 执行sql语句
        cursor.execute(sql1)
        # 提交到数据库执行
        result = cursor.fetchall()
        if len(result) == 0:
            # 提交到数据库执行
            db.commit()
            db.close()
            return
        else:
            if result[0][2] == "已收藏":
                return 1
    except:
        # 如果发生错误则回滚
        db.rollback()
        # 关闭数据库连接
    db.close()

def updatecollect(username, moviename):
    # 打开数据库连接
    db = pymysql.connect("localhost", "root", "123456", "data")
    # 使用cursor()方法获取操作游标
    cursor = db.cursor()
    # 电影简介内容出现""双引号 无法直接插入数据表中 需要进行处理
    # 使用正则替换，便可以插入数据表中
    # SQL 插入语句
    # SQL 查询语句
    sql1 = "select * from comment where username='{}' and moviename='{}'".format(username,moviename)
    try:
        # 执行sql语句
        cursor.execute(sql1)
        # 提交到数据库执行
        result = cursor.fetchall()
        if len(result) == 0:
            # 提交到数据库执行
            sql2 = "INSERT INTO comment (username, moviename,collect) VALUES ('{}', '{}','{}')" \
                .format(username, moviename, "已收藏")
            cursor.execute(sql2)
            db.commit()
        else:
            if result[0][2]=="未收藏":
                collect="已收藏"
            else:
                collect="未收藏"
            sql2 = "update comment set collect = '{}'where username='{}' and moviename='{}'" \
                .format(collect, username, moviename)
            cursor.execute(sql2)
            # 提交到数据库执行
            db.commit()
        print("数据插入成功")
    except:
        # 如果发生错误则回滚
        db.rollback()
        # 关闭数据库连接
    db.close()

def updateUserStatus(username):
    db = pymysql.connect("localhost", "root", "123456", "testdatabase")
    # 使用cursor()方法获取操作游标
    cursor = db.cursor()
    sql1 = "select * from login_user where name='{}'".format(username)
    try:
        # 执行sql语句
        cursor.execute(sql1)
        # 提交到数据库执行
        result = cursor.fetchall()
        if result[0][6] == "正常":
            sql2="update login_user set status = '黑名单' where name='{}'".format(username)
        else:
            sql2="update login_user set status = '正常' where name='{}'".format(username)
        cursor.execute(sql2)
            # 提交到数据库执行
        db.commit()
        print("数据修改成功")
    except:
        # 如果发生错误则回滚
        db.rollback()
        # 关闭数据库连接
    db.close()

def updateCommentStatus(id,status):
    db = pymysql.connect("localhost", "root", "123456", "data")
    # 使用cursor()方法获取操作游标
    cursor = db.cursor()
    sql = "update comment set status = '{}' where id='{}'".format(status,id)
    try:
        # 执行sql语句
        cursor.execute(sql)
            # 提交到数据库执行
        db.commit()
        print("数据修改成功")
    except:
        # 如果发生错误则回滚
        db.rollback()
        # 关闭数据库连接
    db.close()

def updateMovie(movieid,dic):
    db = pymysql.connect("localhost", "root", "123456", "data")
    # 使用cursor()方法获取操作游标
    cursor = db.cursor()
    sql = """update movie3 set name = '{}',director='{}',writer='{}',actors='{}',type='{}',date='{}',timelong='{}',
        IMDburl='{}',introduction="{}",trailerurl='{}',movieurl='{}' where movieid='{}'"""\
        .format(dic['name'],dic['director'],dic['writer'],dic['actors'],dic['type'],dic['date'],dic['timelong']
                ,dic['IMDburl'],dic['introduction'],dic['trailerurl'],dic['movieurl'],movieid)
    try:
        # 执行sql语句
        cursor.execute(sql)
            # 提交到数据库执行
        db.commit()
        print("数据修改成功")
    except:
        # 如果发生错误则回滚
        print("数据修改失败")
        db.rollback()
        # 关闭数据库连接
    db.close()

def checkMovie(movieid):
    db = pymysql.connect("localhost", "root", "123456", "data")
    # 使用cursor()方法获取操作游标
    cursor = db.cursor()
    # 电影简介内容出现""双引号 无法直接插入数据表中 需要进行处理
    # 使用正则替换，便可以插入数据表中
    # SQL 插入语句
    # SQL 查询语句
    sql1 = "select * from movie3 where movieid={}".format(movieid)
    try:
        # 执行sql语句
        cursor.execute(sql1)
        # 提交到数据库执行
        result = cursor.fetchall()
        db.commit()
        db.close()
        if len(result) == 0:
            return 0
        else:
            return 1
    except:
        # 如果发生错误则回滚
        db.rollback()
        # 关闭数据库连接