from django.shortcuts import render,redirect
from module.models import purchase,project,purchase_request,user_info,user_type
from module.forms import ProjectForm,PurchaseForm,RequestForm
from datetime import date
from django.http import HttpResponse
from django.contrib import messages
from django.core.files.storage import FileSystemStorage
from django.core.mail import send_mail
import pandas as pd


# Create your views here.

def login(request):
    if request.method == "POST":
        name = request.POST.get('uname')
        password = request.POST.get('pwd')
        if user_info.objects.filter(uname=name,password=password).exists():
            print('true')
            check_utype = user_info.objects.filter(uname=name,password=password).values('user_type')
            user_type = list(check_utype)[0]['user_type']
            request.session['utype']=user_type
            request.session['uname'] = name
            request.session['is_login'] = True
            if user_type == '1':
                return redirect("/index")
            elif user_type == '2':
                return redirect("/pr_index")
            else:
                return redirect("/pu_index")
        else:
            messages.error(request,'Invalid Credentials')
            return redirect("/")
    else:    
        return render(request,'login.html')

def logout(request):
    del request.session['uname']
    request.session['is_login'] = False
    return redirect("/")

def user_list(request):
    users = user_info.objects.values()
    return render(request,'user_list.html',{'user_list':users})

def edit_users(request,id):
    user_details = user_info.objects.get(uid=id)
    utype = user_type.objects.all()
    return render(request,'edit_users.html',{'user':user_details,'utype':utype})

def delete_users(request):
    uid = request.GET.get('id')
    delete_user = user_info.objects.filter(uid=uid).delete()
    return HttpResponse('User has been deleted')

    
def main(request):
    if request.method == "POST":  
        utype = request.POST['utype']
        if 'Employee' in utype:
            return redirect('/index')
        elif 'Project_Manager' in utype:
            return redirect('/pr_index')
        else:
            return redirect('/pu_index')
    else:
        return render(request,'main.html')


def index(request): 
    if not request.session['is_login']:
        messages.error(request,'Please login to perform this action') 
        return redirect("/")
    if request.session['utype'] != '1':
        messages.error(request,'You don\'t have access for this page') 
        return redirect("/")
    purchase_req = purchase_request.objects.values()
    project_mgr = project.objects.values() 
    purchase_mgr = purchase.objects.values() 
    return render(request,'index.html',{'pur_req':purchase_req,'pj_mgr':project_mgr,'pu_mgr':purchase_mgr})
    

def add(request):
    if not request.session['is_login']:
        messages.error(request,'Please login to perform this action') 
        return redirect("/")
    if request.method == "POST":  
        name = request.POST['name']
        team = request.POST['team']
        req_pro = request.POST['req_pro']
        purpose = request.POST['purpose']
        link = request.POST['link']
        price = request.POST['price']
        mgr = request.POST['mgr']
        img = request.FILES['pro_file']
        fss = FileSystemStorage()
        file = fss.save(img.name, img)
        file_url = fss.url(file)
        insert = purchase_request.objects.create(emp_name=name,team=team,req_product=req_pro,purpose=purpose,product_link=link,
        price=price,project_manager=str(mgr),purchase_manager='Not Assigned',status='Pending for Approval',request_date=date.today(),image=img)
        messages.success(request,'Request added successfully')
        return redirect('/index')
    else:
        project_mgr = project.objects.all() 
        #form = RequestForm()
    return render(request,'add_req.html',{'manager':project_mgr}) 


def project_index(request):  
    if not request.session['is_login']:
        messages.error(request,'Please login to perform this action') 
        return redirect("/")
    if request.session['utype'] != '2':
        messages.error(request,'You don\'t have access for this page') 
        return redirect("/") 
    user_details = user_info.objects.filter(uname=request.session['uname']).values_list('team',flat=True)
    purchase_req = purchase_request.objects.filter(team__in=user_details).values()
    return render(request,'project_index.html',{'pur_req':purchase_req})


def purchase_index(request):  
    if not request.session['is_login']:
        messages.error(request,'Please login to perform this action') 
        return redirect("/")
    if request.session['utype'] != '3':
        messages.error(request,'You don\'t have access for this page') 
        return redirect("/")
    purchase_req = purchase_request.objects.values() 
    project_mgr = project.objects.values() 
    purchase_mgr = purchase.objects.values() 
    return render(request,'purchase_index.html',{'pur_req':purchase_req,'pj_mgr':project_mgr,'pu_mgr':purchase_mgr})


def change_status(request):
    req_id = request.GET.get('id')
    status = request.GET.get('status')
    utype = request.GET.get('utype')
    if 'project' in utype:
        if '1' in status:
            status = 'Approved by project manager'
            purchase_manager = purchase.objects.values('name').filter(purchase_manager_id=1) 
            approve_date = date.today() 
            update = purchase_request.objects.filter(req_id=req_id).update(status=status,approved_date=approve_date,purchase_manager=list(purchase_manager)[0]['name'])
        elif '2' in status:
            status = 'Rejected by project manager'
            purchase_manager = purchase.objects.values('name').filter(purchase_manager_id=0)
            update = purchase_request.objects.filter(req_id=req_id).update(status=status)
    elif 'purchase' in utype:
        if '1' in status:
            status = 'Order placed'
            purchase_manager = purchase.objects.values('name').filter(purchase_manager_id=1)
            purchase_date = date.today() 
            update = purchase_request.objects.filter(req_id=req_id).update(status=status,approved_date=purchase_date,purchase_date=purchase_date,purchase_manager=list(purchase_manager)[0]['name'])  
        elif '2' in status:
            status = 'Rejected by purchase manager'
            update = purchase_request.objects.filter(req_id=req_id).update(status=status)  
        elif '3' in status:
            status = 'Closed'
            del_date = date.today() 
            update = purchase_request.objects.filter(req_id=req_id).update(status=status)
     
    return HttpResponse('success') 


def update_delivery_date(request):
    req_id = request.GET.get('id')
    del_date = request.GET.get('del_date')
    update = purchase_request.objects.filter(req_id=req_id).update(delivery_date=del_date)
    return HttpResponse('Delivery date updated')


def upload_invoice(request):
    if request.method == "POST":  
        inv = request.FILES['invoice']
        req_id = request.POST['req_id']
        inv_name = inv.name.replace(inv.name.split('.')[0],req_id)
        fss = FileSystemStorage()
        file = fss.save(inv.name.replace(inv.name.split('.')[0],req_id), inv)
        file_url = fss.url(file)
        update = purchase_request.objects.filter(req_id=req_id).update(invoice=inv_name)
        messages.success(request,"Invoice Uploaded")
        return redirect('/pu_index')
    else:
        print('hi')
        pass


def upload_user(request):
    if request.method == "POST":  
        usr = request.FILES['user_info']
        fss = FileSystemStorage()
        file = fss.save(usr.name, usr)
        file_url = fss.url(file)
        print(file_url)
        data = pd.read_excel(r"./media/"+usr.name) 
        df = pd.DataFrame(data)
        for row in df.itertuples():
            user_insert = user_info.objects.create(name=row.name,email=row.email,team=row.team,user_type=row.user_type,uname=row.uname,password=row.password,created_on=date.today())
            if row.user_type == '2':
                pj_manager_insert = project.objects.create(name=row.name)
            elif row.user_type == '3':
                pu_manager_insert = purchase.objects.create(name=row.name)
        messages.success(request, 'User details has been added')
        return redirect("/user_list")


def registration(request):
    if request.method == "POST":  
        name = request.POST['name']
        email = request.POST['email']
        team = request.POST['team']
        utype = request.POST['utype']
        uname = request.POST['uname']
        password = request.POST['pwd']
        if utype=='2':
            pj_manager_insert = project.objects.create(name=name)
        elif utype=='3':
            pu_manager_insert = purchase.objects.create(name=name)
        user_insert = user_info.objects.create(name=name,email=email,team=team,user_type=utype,uname=uname,password=password,created_on=date.today())
        messages.success(request,'User Created Successfully')
        return redirect("/user_list") 
    else:
        utype = user_type.objects.all()
        return render(request,'registration.html',{'utype':utype}) 
    
    


