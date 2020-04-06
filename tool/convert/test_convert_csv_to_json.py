#!/bin/python

import csv
import datetime
import unittest
import io
import json
import convert_csv_to_json as ctj


class ConvertTest(unittest.TestCase):
    maxDiff = None

    @classmethod
    def setUpClass(self):
        patients_csv = '''
No,全国地方公共団体コード,都道府県名,市区町村名,公表_年月日,曜日,発症_年月日,居住地,年代,性別,患者_属性,患者_状態,患者_症状,患者_渡航歴の有無フラグ,備考,退院済フラグ,職業
2,440001,大分県,,2020/03/17,木,,大分市,10代,女性,,,,,,"",自営業
2,440001,大分県,,2020/03/19,木,,臼杵市,20代,男性,,,,,,"",自営業
3,440001,大分県,,2020/03/19,木,,臼杵市,30代,女性,,,,,,"",無職
4,440001,大分県,,2020/03/20,金,,大分市,40代,女性,,,,,,"",医療機関職員
5,440001,大分県,,2020/03/20,金,,大分市,60代,女性,,,,,,"",医療機関職員
6,440001,大分県,,2020/03/20,金,,大分市,90代,女性,,,,,,"",医療機関職員
'''.strip()

        data_summary_csv = '''
日付,検査実施件数,うち陽性,相談窓口相談件数,退院,死亡
3月20日,67,5,100,,
3月21日,111,7,117,,
3月22日,182,6,99,1,
3月23日,205,1,311,,
'''.strip()

        self.patients_data = self.csv_to_dict(patients_csv)
        self.data_summary = self.csv_to_dict(data_summary_csv)

    @classmethod
    def csv_to_dict(self, csv_data):
        rows = csv.DictReader(io.StringIO(csv_data))
        return json.loads(json.dumps(list(rows), ensure_ascii=False))

    def test_generate_patients(self):
        expect_json = '''
[{
  "リリース日": "2020-03-17T08:00:00",
  "居住地": "大分市",
  "年代": "10代",
  "性別": "女性",
  "退院": "",
  "date": "2020-03-17"
},
{
  "リリース日": "2020-03-19T08:00:00",
  "居住地": "臼杵市",
  "年代": "20代",
  "性別": "男性",
  "退院": "",
  "date": "2020-03-19"
},
{
  "リリース日": "2020-03-19T08:00:00",
  "居住地": "臼杵市",
  "年代": "30代",
  "性別": "女性",
  "退院": "",
  "date": "2020-03-19"
},
{
  "リリース日": "2020-03-20T08:00:00",
  "居住地": "大分市",
  "年代": "40代",
  "性別": "女性",
  "退院": "",
  "date": "2020-03-20"
},
{
  "リリース日": "2020-03-20T08:00:00",
  "居住地": "大分市",
  "年代": "60代",
  "性別": "女性",
  "退院": "",
  "date": "2020-03-20"
},
{
  "リリース日": "2020-03-20T08:00:00",
  "居住地": "大分市",
  "年代": "90代",
  "性別": "女性",
  "退院": "",
  "date": "2020-03-20"
}]
'''.strip()

        result = ctj.generate_patients(self.patients_data)
        expect = json.loads(expect_json)

        self.assertListEqual(result, expect)

    def test_generate_patients_summary(self):

        expect_json = '''
[{
  "日付": "2020-03-17",
  "小計": 1
},
{
  "日付": "2020-03-18",
  "小計": 0
},
{
  "日付": "2020-03-19",
  "小計": 2
},
{
  "日付": "2020-03-20",
  "小計": 3
}]
'''.strip()
        # テストデータのため2020-03-21から本日までの日付のデータを作成する
        null_data = self.__generate_null_data(datetime.datetime(2020, 3, 21))

        result = ctj.generate_patients_summary_by_date(self.patients_data)
        expect = json.loads(expect_json)
        expect.extend(null_data)

        self.assertListEqual(result, expect)

    def test_generate_inspections_summary(self):
        expect_json = '''
[{
  "日付": "2020-03-20",
  "小計": 67
},
{
  "日付": "2020-03-21",
  "小計": 111
},
{
  "日付": "2020-03-22",
  "小計": 182
},
{
  "日付": "2020-03-23",
  "小計": 205
}]
'''.strip()
        null_data = self.__generate_null_data(datetime.datetime(2020, 3, 24))

        result = ctj.generate_inspections_summary(self.data_summary)
        expect = json.loads(expect_json)
        expect.extend(null_data)

        self.assertListEqual(result, expect)

    def test_generate_patients_summary_by_age(self):
        expect_json = '''
{
  "10代以下": 1,
  "20代〜30代": 2,
  "40代〜50代": 1,
  "60代〜70代": 1,
  "80代以上": 1
}
'''.strip()

        result = ctj.generate_patients_summary_by_age(self.patients_data)
        expect = json.loads(expect_json)

        self.assertDictEqual(result, expect)

    def test_generate_sickbeds_summary(self):
        expect_json = '''
{
  "入院患者数": 18,
  "残り病床数": 100
}
'''.strip()

        result = ctj.generate_sickbeds_summary(self.data_summary)
        expect = json.loads(expect_json)

        self.assertDictEqual(result, expect)

    def test_generate_main_summary(self):
        expect_json = '''
{
  "attr": "累計",
  "value": 19,
  "children": [
      {
        "attr": "入院中",
        "value": 18
      },
      {
        "attr": "死亡",
        "value": 0
      },
      {
        "attr": "退院",
        "value": 1
      }
  ]
}
'''.strip()

        result = ctj.generate_main_summary(self.data_summary)
        expect = json.loads(expect_json)

        self.assertDictEqual(result, expect)

    def test_generate_querents(self):
        expect_json = '''
[
  {
    "日付": "2020-03-20",
    "小計": 100
  },
  {
    "日付": "2020-03-21",
    "小計": 117
  },
  {
    "日付": "2020-03-22",
    "小計": 99
  },
  {
    "日付": "2020-03-23",
    "小計": 311
  }
]
'''.strip()

        result = ctj.generate_querents(self.data_summary)
        expect = json.loads(expect_json)

        self.assertListEqual(result, expect)

    def __generate_null_data(self, start_date):
        datetime_now = datetime.datetime.now()
        end_date = datetime_now if datetime_now.hour >= 22 else \
            datetime_now - datetime.timedelta(days=1)

        null_data = []
        for i in ctj.daterange(start_date, end_date):
            d = {
                "日付": i.strftime("%Y-%m-%d"),
                "小計": 0,
            }
            null_data.append(d)

        return null_data


if __name__ == "__main__":
    unittest.main()
