import os
import time
from datetime import date, timedelta

def init_config():
    conf = """
        BackupFolder = "D:\\1САрхивы8"
        
        FirstMonth = day
        FirstQuarter = week
        FirstYear = month
        NextYear = year
    """.strip('\n')

    return conf

def read_config():
    backup_folder, first_month, first_quarter, first_year, next_year, email_mas = "", "", "", "", "", []

    dir = os.path.abspath(os.curdir)
    filename = dir + "\\config.ini"
    if os.path.isfile(filename):
        with open(filename, mode='r') as f:
            lines = f.readlines()
    else:
        conf = init_config()
        lines = conf.split("\n")

    for nom, stroka in enumerate(lines):
        stroka = stroka.replace('\n', '')
        stroka = stroka.strip()
        if stroka == "": continue

        if stroka[0] == "#": continue
        pos = stroka.find("#")
        if pos >= 0:
            stroka = stroka[0:pos]

        pos = stroka.find("=")
        if pos == -1: continue
        if pos == len(stroka) - 1: continue

        command = stroka[0:pos].strip()
        params = stroka[pos + 1:].strip()

        param_mas = params.split(",")
        for num, par in enumerate(param_mas):
            param_mas[num] = par.strip()

        if command == "BackupFolder":
            backup_folder = params.replace('"','')
        elif command == "FirstMonth":
            first_month = params
        elif command == "FirstQuarter":
            first_quarter = params
        elif command == "FirstYear":
            first_year = params
        elif command == "NextYear":
            next_year = params

    return backup_folder, first_month, first_quarter, first_year, next_year

def read_dir(path):
    file_list = []
    for root, dirs, files in os.walk(path):
        for file in files:
            if file.endswith('.zip') or file.endswith('.rar'):
                full_path = os.path.join(root, file)
                time_obj = time.strptime(time.ctime(os.path.getctime(full_path)))
                time_stamp = time.strftime("%d.%m.%Y", time_obj)
                date_obj = date(time_obj.tm_year,time_obj.tm_mon,time_obj.tm_mday)
                file_list.append( [full_path,file,"",date_obj,time_stamp] )
    return file_list

def decode_list(file_list):
    for nn,file_str in enumerate(file_list):
        path, file, name, date_obj, time_stamp = file_str
        file = file[:-4]

        file_year = file_month = file_day = 0
        if file[-4:].isdigit() and file[-5:-4]=='.':
            file_year = file[-4:]
            file = file[:-5]
        elif file[-2:].isdigit() and file[-3:-2]=='.':
            file_year = '20'+file[-2:]
            file = file[:-3]
        if file[-2:].isdigit() and file[-3:-2]=='.':
            file_month = file[-2:]
            file = file[:-3]
        if file[-2:].isdigit():
            file_day = file[-2:]
            file = file[:-3]

        if 0<int(file_day)<=31 and 0<int(file_month)<=12 and int(file_year)>0:
            time_stamp = file_day+"."+file_month+"."+file_year
            time_obj = time.strptime(time_stamp, "%d.%m.%Y")
            date_obj = date(time_obj.tm_year, time_obj.tm_mon, time_obj.tm_mday)
            file_list[nn][2] = file.strip()
            file_list[nn][3],file_list[nn][4] = date_obj, time_stamp
        else:
            file_list[nn][2] = file_list[nn][1]

    file_list.sort(key=lambda file: file[3], reverse=True)
    file_list.sort(key=lambda file: file[2])

    file_pack = []
    for nn,file_str in enumerate(file_list):
        path, file, name, date_obj, time_stamp = file_str

        f_name = file
        if name!="":
            f_name = name

        pos = -1
        for mm,pack in enumerate(file_pack):
            if pack[0]==f_name:
                pos = mm
                break
        if pos == -1:
            pos = len(file_pack)
            file_pack.append( [f_name, []] )

        pack = file_pack[pos]
        pack[1].append( [path, file, date_obj, time_stamp, True] )

    return file_pack

def print_info(file_pack):
    print("К очистке найдено групп архивов: "+str(len(file_pack)))
    count = 0
    for nn, file_str in enumerate(file_pack):
        print("  "+str(nn+1)+": "+file_str[0]+", вложений: "+str(len(file_str[1])))
        count += len(file_str[1])
    print("Всего архивов: " + str(count))

def minus_years(d, years):
    try:
        return d.replace(year = d.year - years)
    except ValueError:
        return d + (date(d.year - years, 3, 1) - date(d.year, 3, 1))

def minus_month(orig_date,month):
    # advance year and month by one month
    new_year = orig_date.year
    new_month = orig_date.month - month
    # note: in datetime.date, months go from 1 to 12
    if new_month <= 0:
        new_year -= 1
        new_month += 12
    new_day = orig_date.day
    # while day is out of range for month, reduce by one
    while True:
        try:
            new_date = date(new_year, new_month, new_day)
        except ValueError as e:
            new_day -= 1
        else:
            break
    return new_date

def mark_files(pack,period, pred_date,cur_date):
    if period=="day":
        return
    elif period=="week": #1 файл в неделю
        date_1 = cur_date
        date_0 = cur_date-timedelta(days=7)
        date_0 = pred_date if date_0<pred_date else date_0

        while date_1>pred_date:
            list_pack = []
            for file in pack:
                date_file = file[2]
                if date_0<=date_file<=date_1:
                    list_pack.append(file)

            len_list = len(list_pack)
            if len_list>1:
                for nn,file in enumerate(list_pack):
                    file[4] = True if nn==0 else False

            date_1 = date_0-timedelta(days=1)
            date_0 = date_1-timedelta(days=7)
            date_0 = pred_date if date_0<pred_date else date_0

    elif period == "month":  # 1 файл в месяц
        date_1 = cur_date
        date_0 = minus_month(date_1,1)
        date_0 = pred_date if date_0<pred_date else date_0

        while date_1>pred_date:
            list_pack = []
            for file in pack:
                date_file = file[2]
                if date_0<=date_file<=date_1:
                    list_pack.append(file)

            len_list = len(list_pack)
            if len_list>1:
                for nn,file in enumerate(list_pack):
                    file[4] = True if nn==0 else False

            date_1 = date_0-timedelta(days=1)
            date_0 = minus_month(date_1,1)
            date_0 = pred_date if date_0<pred_date else date_0

    elif period == "year":  # 1 файл в год
        date_1 = cur_date
        date_0 = minus_years(date_1,1)
        date_0 = pred_date if date_0<pred_date else date_0

        while date_1>pred_date:
            list_pack = []
            for file in pack:
                date_file = file[2]
                if date_0<=date_file<=date_1:
                    list_pack.append(file)

            len_list = len(list_pack)
            if len_list>1:
                for nn,file in enumerate(list_pack):
                    file[4] = True if nn==0 else False

            date_1 = date_0-timedelta(days=1)
            date_0 = minus_years(date_1,1)
            date_0 = pred_date if date_0<pred_date else date_0

    return

def mark_list(file_pack, first_month, first_quarter, first_year, next_year):
    current_date = date.today()
    current_date_minus_month = minus_month(current_date,1)
    current_date_minus_quarter = minus_month(current_date,4)
    current_date_minus_year  = minus_years(current_date,1)

    for pack in file_pack:
        mark_files(pack[1],first_month,current_date_minus_month,current_date)
        mark_files(pack[1],first_quarter,current_date_minus_quarter,current_date_minus_month-timedelta(days=1))
        mark_files(pack[1],first_year,current_date_minus_year,current_date_minus_quarter-timedelta(days=1))

        mark_files(pack[1],next_year,minus_years(current_date_minus_year,50),current_date_minus_year-timedelta(days=1))

    return

def delete_files(file_pack):
    count = 0
    for pack in file_pack:
        for file in pack[1]:
            if not file[4]:
                os.remove(file[0])
                count += 1
    print("Удалено архивов :"+str(count))

def main():
    backup_folder, first_month, first_quarter, first_year, next_year = read_config()
    file_list = read_dir(backup_folder)
    file_pack = decode_list(file_list)
    mark_list(file_pack, first_month, first_quarter, first_year, next_year)
    print_info(file_pack)
    delete_files(file_pack)

    return

main()
