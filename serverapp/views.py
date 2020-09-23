from django.shortcuts import render
import json

from django.shortcuts import render
from django.db import connection
from .models import temp1,temp2
from django.shortcuts import render, HttpResponse, redirect, reverse
import socket
from django.http import HttpResponse
import serial
import serial.tools.list_ports

#主页
def index(request):
    return render(request,'index.html')

#地面站将航点信息发送给无人机 8100
def process(request):
    # 串口发送数据
    try:
        pos = []
        for i in range(1, 6):
            x = request.POST.get('posx' + str(i))
            y = request.POST.get('posy' + str(i))
            pos.append(x)
            pos.append(y)
        print(pos)

        for context in pos:
            if context != None:
                print(context)
                ser2.write(context.encode("utf-8"))
    except Exception as e:
        print("---异常---：", e)
    return HttpResponse("ok")

# form表单形式发送数据 起落站 8300
def search1(request):
    # 串口发送数据
    try:
        ctx1 = {}
        ctx1.setdefault('rlt1', 0)
        if request.POST:
            ctx1['rlt1'] = request.POST['q']
            context = str(ctx1['rlt1'])
            # 写数据
            result = ser1.write(context.encode("utf-8"))
            print("写总字节数:", result)
            print(context)
    except Exception as e:
        print("---异常---：", e)
    return render(request, "index.html", ctx1)

def search2(request):
    # 串口发送数据
    try:
        ctx2 = {}
        ctx2.setdefault('rlt2', 0)
        if request.POST:
            ctx2['rlt2'] = request.POST['p']
            context = str(ctx2['rlt2'])
            # 写数据
            result = ser2.write(context.encode("utf-8"))
            print("写总字节数:", result)
            print(context)
    except Exception as e:
        print("---异常---：", e)
    return render(request, "index.html", ctx2)



#起落站发送给地面站 8400用于接收起落站数据
def recvdata1(request):
    # 接收一个数据
    if request.is_ajax():
        # 串口接收数据
        try:
            # print(ser.read())#读一个字节
            # print(ser.read(10).decode("gbk"))#读十个字节
            # print(ser.readline().decode("gbk"))#读一行
            # print(ser.readlines())#读取多行，返回列表，必须匹配超时（timeout)使用
            # print(ser.in_waiting)#获取输入缓冲区的剩余字节数
            # print(ser.out_waiting)#获取输出缓冲区的字节数

            # 循环接收数据，此为死循环，可用线程实现
            while True:
                if ser1.in_waiting:
                    data = ser1.read(ser1.in_waiting).decode("utf-8")
                    if (data == "exit"):  # 退出标志
                        break
                    else:
                        print("收到数据：", data)
                        # data = str(data, encoding='utf-8')
                        data = data.split(' ')
                        position = data[0]  # 接收位置信息
                        temperature = data[1]  # 接收温度信息
                        print(position, temperature)
                        # 添加一条数据到数据库中
                        temp_data = temp1(position=position, temperature=temperature)
                        temp_data.save()
                        data = 'position = ' + str(position) + 'm' + '  ' + 'temperature = ' + str(temperature) + '°'
                        print(data)
                        r = HttpResponse(data)
                        return r
            print("---------------")
            ser1.close()  # 关闭串口
        except:
            data1 = '当前没有数据输入，请检查数据是否正在输入'
            r1 = HttpResponse(data1)
            return r1
    else:
        return HttpResponse('NO AJAX')
#起落站发送给地面站 8400用于接收起落站数据
def recvdata2(request):
    # 接收一个数据
    if request.is_ajax():
        # 串口接收数据
        try:
            # print(ser.read())#读一个字节
            # print(ser.read(10).decode("gbk"))#读十个字节
            # print(ser.readline().decode("gbk"))#读一行
            # print(ser.readlines())#读取多行，返回列表，必须匹配超时（timeout)使用
            # print(ser.in_waiting)#获取输入缓冲区的剩余字节数
            # print(ser.out_waiting)#获取输出缓冲区的字节数

            # 循环接收数据，此为死循环，可用线程实现
            while True:
                if ser2.in_waiting:
                    data = ser2.read(ser2.in_waiting).decode("utf-8")
                    if (data == "exit"):  # 退出标志
                        break
                    else:
                        print("收到数据：", data)
                        # data = str(data, encoding='utf-8')
                        data = data.split(' ')
                        position = data[0]  # 接收位置信息
                        temperature = data[1]  # 接收温度信息
                        print(position, temperature)
                        # 添加一条数据到数据库中
                        temp_data = temp2(position=position, temperature=temperature)
                        temp_data.save()
                        data = 'position = ' + str(position) + 'm' + '  ' + 'temperature = ' + str(temperature) + '°'
                        print(data)
                        r = HttpResponse(data)
                        return r
            print("---------------")
            ser2.close()  # 关闭串口
        except:
            data2 = '当前没有数据输入，请检查数据是否正在输入'
            r1 = HttpResponse(data2)
            return r1
    else:
        return HttpResponse('NO AJAX')


def get_cursor1():
    return connection.cursor()
def show1(request):
    cursor = get_cursor1()
    cursor.execute("select id,position,date_added,temperature from serverapp_temp1")
    data_temps = cursor.fetchall()  # 数据库所有数据
    length = len(data_temps)
    context ={
        'data' : data_temps,
        'length' : length}
    return render(request, 'show1.html',context)
def show2(request):
    cursor = get_cursor1()
    cursor.execute("select id,position,date_added,temperature from serverapp_temp2")
    data_temps = cursor.fetchall()  # 数据库所有数据
    length = len(data_temps)
    context ={
        'data' : data_temps,
        'length' : length}
    return render(request, 'show2.html',context)

def newest1(request):
    cursor = get_cursor1()
    cursor.execute("select id,position,date_added,temperature from serverapp_temp1")
    data_temps = cursor.fetchall()  # 数据库所有数据
    length = len(data_temps)
    data_temps = data_temps[length-1]
    context ={
        'data' : data_temps,
        'length' : length}
    return render(request, 'newest1.html',context)
def newest2(request):
    cursor = get_cursor1()
    cursor.execute("select id,position,date_added,temperature from serverapp_temp2")
    data_temps = cursor.fetchall()  # 数据库所有数据
    length = len(data_temps)
    data_temps = data_temps[length-1]
    context ={
        'data' : data_temps,
        'length' : length}
    return render(request, 'newest2.html',context)
# 查询
def select1(request):
    if request.method == "POST":
        id = request.POST.get('id')
        position = request.POST.get('position')
        temperature = request.POST.get('temperature')
        date_added = request.POST.get('date_added')
        if id:
            temp_data = temp1.objects.filter(id=id).first()
        if position:
            temp_data = temp1.objects.filter(position=position).all()
        if temperature:
            temp_data = temp1.objects.filter(temperature=temperature).all()
        if date_added:
            temp_data = temp1.objects.filter(date_added=date_added).first()
        if temp_data == None:
            #NoneType
            return HttpResponse("错误")
        else:
            temp_datas = []
            print(temp_data)
            try:
                length = len(temp_data)
                for temp in temp_data:
                    id = temp.id
                    position = temp.position
                    temperature = temp.temperature
                    date_added = temp.date_added
                    datas = [id,position,temperature,date_added]
                    temp_datas.append(datas)
                print(temp_datas)
                context = {
                    'data': temp_datas,
                    'length': length,
                    'msg': True,
                            }
            except TypeError:
                length=1
                id = temp_data.id
                position = temp_data.position
                temperature = temp_data.temperature
                date_added = temp_data.date_added
                datas = [id, position, temperature, date_added]
                temp_datas.append(datas)
                context = {
                    'data': temp_datas,
                    'length': length,
                    'msg': True,
                }
        return render(request, 'select1.html', context)

    else:
        context = {
            'msg' : False,
        }
        return render(request, 'select1.html', context)
def select2(request):
    if request.method == "POST":
        id = request.POST.get('id')
        position = request.POST.get('position')
        temperature = request.POST.get('temperature')
        date_added = request.POST.get('date_added')
        if id:
            temp_data = temp2.objects.filter(id=id).first()
        if position:
            temp_data = temp2.objects.filter(position=position).all()
        if temperature:
            temp_data = temp2.objects.filter(temperature=temperature).all()
        if date_added:
            temp_data = temp2.objects.filter(date_added=date_added).first()
        if temp_data == None:
            #NoneType
            return HttpResponse("错误")
        else:
            temp_datas = []
            print(temp_data)
            try:
                length = len(temp_data)
                for temp in temp_data:
                    id = temp.id
                    position = temp.position
                    temperature = temp.temperature
                    date_added = temp.date_added
                    datas = [id,position,temperature,date_added]
                    temp_datas.append(datas)
                print(temp_datas)
                context = {
                    'data': temp_datas,
                    'length': length,
                    'msg': True,
                            }
            except TypeError:
                length=1
                id = temp_data.id
                position = temp_data.position
                temperature = temp_data.temperature
                date_added = temp_data.date_added
                datas = [id, position, temperature, date_added]
                temp_datas.append(datas)
                context = {
                    'data': temp_datas,
                    'length': length,
                    'msg': True,
                }
        return render(request, 'select2.html', context)

    else:
        context = {
            'msg' : False,
        }
        return render(request, 'select2.html', context)

def serialSet(request):
    # # 获取可用串口
    # port_list = list(serial.tools.list_ports.comports())
    # print(port_list)
    # if len(port_list) == 0:
    #     print('无可用串口')
    # else:
    #     for i in range(0, len(port_list)):
    #         print(port_list[i])

    flags2 = {}
    flags2['flag'] = "端口还未配置，请点击配置按钮"
    if request.POST:
        x1 = request.POST.get('portx1')
        y1 = request.POST.get('bps1')
        x2 = request.POST.get('portx2')
        y2 = request.POST.get('bps2')
        # 串口发送数据
        try:
            # 端口，GNU / Linux上的/ dev / ttyUSB0 等 或 Windows上的 COM3 等
            portx1 = x1
            # 波特率，标准值之一：50,75,110,134,150,200,300,600,1200,1800,2400,4800,9600,19200,38400,57600,115200
            bps1 = y1
            # 超时设置,None：永远等待操作，0为立即返回请求结果，其他值为等待超时时间(单位为秒）
            timex = 5
            # 打开串口，并得到串口对象
            global ser1
            ser1 = serial.Serial(portx1, bps1, timeout=timex)
            print("ser1配置完成")
            print(ser1)
            # 端口，GNU / Linux上的/ dev / ttyUSB0 等 或 Windows上的 COM3 等
            portx2 = x2
            # 波特率，标准值之一：50,75,110,134,150,200,300,600,1200,1800,2400,4800,9600,19200,38400,57600,115200
            bps2 = y2
            # 超时设置,None：永远等待操作，0为立即返回请求结果，其他值为等待超时时间(单位为秒）
            timex = 5
            # 打开串口，并得到串口对象
            global ser2
            ser2 = serial.Serial(portx2, bps2, timeout=timex)
            print("ser2配置完成")
            print(ser2)
            flags2['flag'] = "配置完成"
        except Exception as e:
            print("---异常---：", e)
    return render(request,'index.html',flags2)
