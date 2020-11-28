from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from django.views import View

from .models import SeaFood
from seafood.tables import ViewsTable

import pandas as pd

from bs4 import BeautifulSoup
import requests
from requests import HTTPError
import re

import time
import datetime


class UseRequestMethod():
    def __init__(self):
        return

    def get_requests(self, url):
        tries = 5
        for i in range(tries):
            try:
                get_method = requests.get(url)
                get_method.raise_for_status()
            except HTTPError as http_err:
                print(f'HTTP error occurred: {http_err}')  # Python 3.6
                if i < tries - 1:  # i is zero indexed
                    time.sleep(2)
                    continue
            except Exception as err:
                print(f'Other error occurred: {err}')  # Python 3.6
                if i < tries - 1:  # i is zero indexed
                    time.sleep(2)
                    continue
            else:
                return BeautifulSoup(get_method.content, 'html.parser', from_encoding='utf-8')

    def post_requests(self, url, params):
        tries = 5
        for i in range(tries):
            try:
                post_method = requests.post(url, data=params)
                post_method.raise_for_status()
            except HTTPError as http_err:
                print(f'HTTP error occurred: {http_err}')  # Python 3.6
                if i < tries - 1:  # i is zero indexed
                    time.sleep(2)
                    continue
            except Exception as err:
                print(f'Other error occurred: {err}')  # Python 3.6
                if i < tries - 1:  # i is zero indexed
                    time.sleep(2)
                    continue
            else:
                return BeautifulSoup(post_method.content, 'html.parser', from_encoding='utf-8')


class HomeView(View):
    def get(self, request):
        # 각 필드 순서로 Ordering 하여 제일 마지막 id를 키로하는 객체 리턴, 첫번째는 .first()
        # 실제 값은 max_object.field_name, view.html에 최초 전달할 초기값
        max_object = SeaFood.objects.order_by('sfd_yyyy', 'sfd_mm', 'sfd_dd').last()

        # distinct 한 어종을 가져옴옴
        list_names = SeaFood.objects.order_by().values_list('sfd_species').distinct()

        # 어종을 줄이기 위해 re_name 작업 - list 한번에 바꾸는 작업이 있는지 찾아보자
        # 괄호 삭제
        list_name = []
        for list_name_v in list_names:

            re_name = re.sub(r'\([^)]*\)', '', list_name_v[0])
            if re_name == '':
                continue
            elif re_name in ['고등 갯고동', '고둥 갯고동']:
                re_name = '갯고동'
            elif re_name in ['가오리날개']:
                re_name = '가오리'
            elif re_name in ['겉바지락', '깐바지락', '물바지락']:
                re_name = '바지락'
            elif re_name in ['겉맛', '깐맛', '대맛']:
                re_name = '맛'
            elif re_name in ['겉삐뚜리']:
                re_name = '삐뚜리'
            elif re_name in ['게 기타', '게발', '대게']:
                re_name = '게'
            elif re_name in ['깐소라']:
                re_name = '소라'
            elif re_name in ['깐굴']:
                re_name = '굴'
            elif re_name in ['겉우렁']:
                re_name = '우렁'
            elif re_name in ['맛조개', '우럭조개', '조개 기타', '코끼리 조개']:
                re_name = '조개'
            elif re_name in ['대구 기타']:
                re_name = '대구'
            elif re_name in ['새우 기타']:
                re_name = '새우'

            list_name.append(re_name)

        # 중복제거 해서 Sorting
        list_name = sorted(set(list_name))

        template = 'seafood/home.html'
        if len(list_name) > 0:
            contents = {'list_name': list_name, 'line_num': 10, 'sfd_yyyy': max_object.sfd_yyyy,
                        'sfd_mm': max_object.sfd_mm, 'sfd_dd': max_object.sfd_dd}
        else:
            contents = {'list_name': None, 'line_num': 0, 'sfd_yyyy': None,
                        'sfd_mm': None, 'sfd_dd': None}

        # home.html 데이터 넘김
        return render(request, template, contents)


class CreateData(View):
    """
    노량신 수산시장 경략가격정보로부터 내 데이터베이스에 저장
    """

    def get_seafood(self, re_pageSize, yy, mm, dd):
        url = "https://www.susansijang.co.kr/nsis/mim/info/mim9030"
        params = {'pageIndex': re_pageSize,
                  'pageUnit': 20,
                  'pageSize': 1,
                  'kdfshNm': '',
                  'searchYear': yy,
                  'searchMonth': mm,
                  'searchDate': dd,
                  }
        get_info_cls = UseRequestMethod()

        content = get_info_cls.post_requests(url, params)
        paginate = content.select_one('div.paginate > span')
        page_size = paginate.text.split('/')[1]

        tables = content.find_all('table')
        trs = tables[0].find_all('tr')

        header = []

        for tr_i, tr_v in enumerate(trs):
            if tr_i == 0:
                ths = tr_v.find_all('th')
                for th in ths:
                    header.append(th.get_text().strip())
            else:
                tds = tr_v.find_all('td')
                if tds[0].get_text() == '조회된 경락시세가 없습니다.':
                    sfd = SeaFood(sfd_yyyy=yy, sfd_mm=mm, sfd_dd=dd, sfd_species='',
                                  sfd_orign='', sfd_standard='', packing_uint='',
                                  quantity=None,
                                  highest=None,
                                  lowest=None, average=None)
                    sfd.save()
                    return None
                value_data = []
                for td_index, td_value in enumerate(header):
                    value_data.append(tds[td_index].get_text().strip())

                sfd = SeaFood(sfd_yyyy=yy, sfd_mm=mm, sfd_dd=dd, sfd_species=value_data[0],
                              sfd_orign=value_data[1], sfd_standard=value_data[2], packing_uint=value_data[3],
                              quantity=float(value_data[4].replace(',', '')),
                              highest=int(value_data[5].replace(',', '')),
                              lowest=int(value_data[6].replace(',', '')), average=int(value_data[7].replace(',', '')))
                sfd.save()
        if int(re_pageSize) <= int(page_size):
            print(f'총 {page_size} 중 {re_pageSize} 읽었습니다.')
            re_pageSize += 1

            if int(re_pageSize) > int(page_size):
                print('저장을 마침니다.')
                return None
            else:
                self.get_seafood(re_pageSize, yy, mm, dd)

    def get(self, request):

        mode_span = False

        if mode_span:
            today = datetime.date.today()
            max_object = SeaFood.objects.order_by('sfd_yyyy', 'sfd_mm', 'sfd_dd').last()
            last_date = datetime.date(int(max_object.sfd_yyyy), int(max_object.sfd_mm), int(max_object.sfd_dd))
        else:
            today = datetime.date(2020,6,27)
            last_date = datetime.date(2019,7,31)

        day_cnt = today - last_date
        fromday = today.strftime('%Y/%m/%d').split('/')

        if day_cnt.days > 0:
            for n in range(day_cnt.days):
                deltaday = today - datetime.timedelta(days=n)
                strtoday = deltaday.strftime('%Y/%m/%d').split('/')
                print("#" * 100)
                print(f"{strtoday[0]}년, {strtoday[1]}월, {strtoday[2]}일")
                self.get_seafood(1, strtoday[0], strtoday[1], strtoday[2])
            msg = f'{strtoday[0]}년{strtoday[1]}월{strtoday[2]}일 부터  {fromday[0]}년{fromday[1]}월{fromday[2]}까지 저장을 마침니다.'
        else:
            msg = f'{fromday[0]}년{fromday[1]}월{fromday[2]}일 오늘까지 데이터가 저장되어 있습니다.'

        template = 'seafood/create.html'
        contents = {'end_result': msg}

        return render(request, template, contents)


class TableView(View):

    def get(self, request):
        # 헐 바로 request.GET 하면 얻을 수 있는 걸 거의 4시간이나 고생했네. view(request, arg....)
        # arg...방식은 쓸 필요가 없는 걸 괜히 ... 헐.
        name = request.GET['sfd_species']
        sfd_yyyy = request.GET['sfd_yyyy']
        sfd_mm = request.GET['sfd_mm']
        sfd_dd = request.GET['sfd_dd']

        talbe_sea = SeaFood.objects.filter(sfd_species__icontains=name, sfd_yyyy=sfd_yyyy, sfd_mm=sfd_mm,
                                           sfd_dd=sfd_dd).order_by('sfd_yyyy', 'sfd_mm', 'sfd_dd', 'sfd_species',
                                                                   'sfd_orign', 'sfd_standard',
                                                                   'packing_uint')

        if len(talbe_sea) == 0:
            max_object = SeaFood.objects.filter(sfd_species__icontains=name).order_by(
                'sfd_yyyy', 'sfd_mm', 'sfd_dd').last()
            last_sea = ViewsTable(
                SeaFood.objects.filter(
                    sfd_species__icontains=name,
                    sfd_yyyy=max_object.sfd_yyyy,
                    sfd_mm=max_object.sfd_mm,
                    sfd_dd=max_object.sfd_dd
                ).order_by('sfd_species','sfd_orign','sfd_standard','packing_uint')
            )
            distinct_sea = SeaFood.objects.filter(sfd_species__icontains=name,
                                                  sfd_yyyy=max_object.sfd_yyyy,
                                                  sfd_mm=max_object.sfd_mm,
                                                  sfd_dd=max_object.sfd_dd).values_list(
                'sfd_species', 'sfd_orign', 'sfd_standard', 'packing_uint').distinct()
        else:
            last_sea = ViewsTable(talbe_sea)
            distinct_sea = SeaFood.objects.filter(
                sfd_species__icontains=name, sfd_yyyy=sfd_yyyy, sfd_mm=sfd_mm, sfd_dd=sfd_dd).values_list(
                'sfd_species', 'sfd_orign', 'sfd_standard', 'packing_uint').distinct().order_by('sfd_species',
                                                                                                'sfd_orign',
                                                                                                'sfd_standard',
                                                                                                'packing_uint')

        distinct_values = []
        for distinct_value in distinct_sea:
            distinct_values.append([distinct_value[0], distinct_value[1], distinct_value[2], distinct_value[3]])

        template = 'seafood/view.html'
        contents = {'name': name, 'table': last_sea, "distinct_name": distinct_values}

        return render(request, template, contents)


class ChartData(APIView):
    authentication_classes = []
    permission_classes = []

    def get(self, request):
        # API (ChartData:api/chart/) 에 request_input: 요청 파라메터 , request.GET['request_input'] : 요청값
        # name = request.GET['request_input']
        # QuerySet은 문자열, 문자제거 처리과정 필요

        distinct_name = request.GET['distinct_input']
        print(distinct_name)
        distinct_name = distinct_name.replace('&#39;', '')
        # distinct_name = distinct_name.replace('&#x27;', '')
        distinct_name = distinct_name[0:-1]
        distinct_name = distinct_name[1:]
        rex_list = re.findall((r"\[(.*?)\]"), distinct_name)

        sfd_species = []
        sfd_orign = []
        sfd_standard = []
        packing_uint = []

        df_distinct = []
        for rex_str in rex_list:
            rex_split = rex_str.split(',')
            str_species = rex_split[0].strip(' ')
            str_orign = rex_split[1].strip(' ')
            str_standard = rex_split[2].strip(' ')
            str_uint = rex_split[3].strip(' ')
            sfd_species.append(str_species)
            sfd_orign.append(str_orign)
            sfd_standard.append(str_standard)
            packing_uint.append(str_uint)
            df_distinct.append(str_species + '_' + str_orign + '_' + str_standard + '_' + str_uint)
        sfd_species = list(set(sfd_species))
        sfd_orign = list(set(sfd_orign))
        sfd_standard = list(set(sfd_standard))
        packing_uint = list(set(packing_uint))

        # Queryset
        list_all = SeaFood.objects.filter(
            sfd_species__in=sfd_species, sfd_orign__in=sfd_orign, sfd_standard__in=sfd_standard,
            packing_uint__in=packing_uint).values(
            'sfd_yyyy', 'sfd_mm', 'sfd_dd', 'sfd_species', 'sfd_orign', 'sfd_standard', 'packing_uint',
            'average').order_by(
            'sfd_yyyy', 'sfd_mm', 'sfd_dd')

        # Queryset : sfd_species__icontains=name 아래는 차트에서 Legend 가 너무 많아 위처럼 바꿈
        # list_all = SeaFood.objects.filter(sfd_species__icontains=name).values(
        #     'sfd_yyyy', 'sfd_mm', 'sfd_dd', 'sfd_species', 'sfd_orign',
        #     'sfd_standard', 'packing_uint', 'average').order_by(
        #     'sfd_yyyy', 'sfd_mm', 'sfd_dd')

        # DataFrame으로 변환 : Legend, 날짜, 값의 length를 동일하게 하기 위해서.. Queryset에서 하는 방법을 모르겠음
        df_list_all = pd.DataFrame(list_all)

        # DataFrame 전처리
        df_list_all['date_str'] = df_list_all['sfd_yyyy'] + df_list_all['sfd_mm'] + df_list_all['sfd_dd']
        df_list_all['species'] = df_list_all['sfd_species'] + '_' + df_list_all['sfd_orign'] + '_' + df_list_all[
            'sfd_standard'] + '_' + df_list_all['packing_uint']
        df_list_all.drop(['sfd_yyyy', 'sfd_mm', 'sfd_dd', 'sfd_species', 'sfd_orign', 'sfd_standard', 'packing_uint'],
                         axis=1, inplace=True)

        # 테이블에 나온 항목
        df_list_all = df_list_all[df_list_all['species'].isin(df_distinct)]

        # 문자열로 된 Date를 date 타입으로 바꾸려면 아래
        # df_list_all['date_str'] = pd.to_datetime(df_list_all['date_str'], format='%Y%m%d')
        # df_res = df_list.pivot(index='date_str', columns='species', values='average')

        # fillna('') 하지 않으면 chartjs 에서 에러 발생.
        df_res = df_list_all.pivot('date_str', 'species')['average'].fillna('')
        # print(df_res)
        # Response할 데이터 구조로 반들기
        data_set = []
        for legend in df_res.columns.values:
            data_set.append({"legend": legend, "y": df_res[legend].values.tolist()})

        return_data = {
            "x": df_res.index.values.tolist(),
            "data_set": data_set
        }

        return Response(return_data)
