# -*- coding: utf-8 -*-
# ---
# jupyter:
#   jupytext:
#     text_representation:
#       extension: .py
#       format_name: light
#       format_version: '1.5'
#       jupytext_version: 1.5.2
#   kernelspec:
#     display_name: Python 3
#     language: python
#     name: python3
# ---

# # ２章　小売店のデータでデータ加工を行う１０本ノック
#
# 本章では、ある小売店の売上履歴と顧客台帳データを用いて、データ分析の素地となる「データの加工」を習得することが目的です。
# 実際の現場データは手入力のExcel等、決して綺麗なデータではない事が多いため、
# データの揺れや整合性の担保など、汚いデータを取り扱うデータ加工を主体に進めて行きます。

# ### ノック１１：データを読み込んでみよう

import pandas as pd
uriage_df = pd.read_csv('uriage.csv')
uriage_df

user_df = pd.read_excel('kokyaku_daicho.xlsx')
user_df

# ### ノック１２：データの揺れを見てみよう

# +
# 入力データに欠損値や、全角半角などの表記ゆれが存在しているかをチェックする。
# -

uriage_df['item_name'] #全角半角が混じってる。小文字と大文字が混じっている

uriage_df['item_price'] # 欠損値が含まれている

# ### ノック１３：データに揺れがあるまま集計しよう
# 欠損値の影響を見るために、まずはデータに揺れを含んだまま各種値を集計してみる。

# 商品ごとの月別売上個数
uriage_df['purchase_date'] = pd.to_datetime(uriage_df['purchase_date'])
uriage_df['purchase_month'] = uriage_df['purchase_date'].dt.strftime("%Y%m")
uriage_df

pivot = uriage_df.pivot_table(index='purchase_month', columns='item_name', aggfunc="size", fill_value=0)
pivot
# 本来は26商品しかないが、99商品として集計されてしまっている

# 各月の売上金額も見てみる
pivot = uriage_df.pivot_table(index='purchase_month', columns='item_name', values='item_price', aggfunc='sum', fill_value=0)
pivot

# ### ノック１４：商品名の揺れを補正しよう
#
# 対応方針 : 商品名のデータを見てから、全角に揃える

print(len(uriage_df['item_name'].unique()))

# 僕のやり方 : 空白を除去してから、大文字に揃える
uriage_df['item_name'] = uriage_df['item_name'].str.replace(' ', '')
uriage_df['item_name'] = uriage_df['item_name'].str.replace('　', '')
uriage_df['item_name'] = uriage_df['item_name'].str.upper()

print(len(uriage_df['item_name'].unique()))
print(uriage_df['item_name'].unique())

# ### ノック１５：金額欠損値の補完をしよう

# +
# 次は金額の欠損値を行う。
# 業務で行う場合、欠損値はヒアリング等を行うことが必要になるかもしれない。
# 今回は、普通に欠損しているだけなので、コードで埋める
# -

# nullチェック
uriage_df.isnull().any()

# +
# item_priceが欠損しているが、商品名が存在するので、そこから補完する
null_flg = uriage_df["item_price"].isnull() # nullにフラグを立てる
# print(null_flg)

for trg in list(uriage_df.loc[null_flg, "item_name"].unique()): # 欠損がある商品名をすべて取得する
    hoten_price = uriage_df.loc[(~null_flg) & (uriage_df["item_name"] == trg), "item_price"].max() # 欠損してない要素かつ、対象の商品を取得. 一つだけを選択するためにmaxを指定
    print(hoten_price)
    uriage_df["item_price"].loc[(null_flg) & (uriage_df["item_name"] == trg)] = hoten_price
# -

# nullチェック
uriage_df.isnull().any()

# ただしく値を置換できたからをチェックする。
# そのために、各種商品名の最小値、最大値を確認する
for item_name in list(uriage_df["item_name"].unique()):
    max_price = uriage_df['item_price'].loc[uriage_df['item_name'] == item_name].max()
    min_price = uriage_df['item_price'].loc[uriage_df['item_name'] == item_name].min()
    print_text = "item_name : {0}, max_price: {1}, min_price: {2}".format(item_name, max_price, min_price)
    print(print_text)

# ### ノック１６：顧客名の揺れを補正しよう

# +
# まずはデータの揺れを確認する
user_df

# 顧客名に、半角全角スペースが混ざってる
# 登録日に日付と、数字データが混じってる

# +
# くっつける予定のデータと比較してみる
uriage_df

# user_dfが名前の間に空白が含まれているが、uriage_dfには存在しない
# -

# user_dfの顧客名から、空白を削除する
user_df['顧客名'] = user_df['顧客名'].str.replace(" ", "")
user_df['顧客名'] = user_df['顧客名'].str.replace("　", "")
user_df['顧客名']

# +
# 今回は、空白削除だけだったが、顧客名単体での補正は現実的には難しい
# 同性同名の存在や誤変換などが考えられるので、ヒアリングや別資料をもらう必要性がある
# -

# ### ノック１７：日付の揺れを補正しよう

# +
user_df["登録日"]
# 数字の意味がわからないので解読する

# 当該データの形式がexcelなので、excelで見てみると正しく表示されているので、形式を変更する
# -

# まずは欠損データの数を見てみる. 数値データのみを選択して取り出す
flg_is_number = user_df["登録日"].astype("str").str.isdigit() # isdigit()で数値データのみを取得
flg_is_number.sum()

# +
# https://qiita.com/y-vectorfield/items/323960a01d73ec1b4006
# excelの日付データを変換するときの注意点
# excelの日付データは1900/01/01を基準としているので、UNIXではないことを注意

# timedeltaで基準日からの経過時間をプラスする
conv_date = pd.to_timedelta(user_df.loc[flg_is_number, "登録日"].astype('float'), unit='D') + pd.to_datetime('1900/01/01')
conv_date

# excelとpythonでは日数の計算方法が違うので、注意。
# python側を-2日する
# -

# すべての日付データをdatetime化する
str_date = pd.to_datetime(user_df.loc[~flg_is_number, "登録日"])
str_date

# 正しく置換したデータを結合する
user_df["登録日"] = pd.concat([conv_date, str_date]) # concatを保有しているindexが維持されるので大丈夫
user_df

# 登録日を月ごとにまとめる
user_df['登録月'] = user_df['登録日'].dt.strftime("%Y%m")
user_df

# 登録月を集計してみてみる
temp = user_df.groupby("登録月").count()["顧客名"]
print(temp)
print(len(user_df))

# ### ノック１８：顧客名をキーに２つのデータを結合(ジョイン)しよう

# これまでの結果で、user_dfとuriage_dfでユーザ名が一致したので、結合してみる
merge_data = pd.merge(uriage_df, user_df, left_on="customer_name", right_on="顧客名", how="left")
merge_data = merge_data.drop("customer_name", axis=1) # ユーザ名が重複しているので削除する\
merge_data

# ### ノック１９：クレンジングしたデータをダンプしよう

# データクレンジングして、キレイになったデータができたので、その状態で一時保存しておく
merge_data.to_csv("dump_data.csv", index=False) # indexをfalseにしないとデータが汚くなるので注意

# ### ノック２０：データを集計しよう

# 保存したデータから読み込む
import_data = pd.read_csv("dump_data.csv")
import_data

# 地域ごとの販売実績を見てみる
byRegion = import_data.pivot_table(index="purchase_month", columns='地域', aggfunc='size', fill_value=0)
byRegion

# 集計期間で購入していないユーザを見てみる
# import_dataは購買履歴が基準になっているので、使えない。
# そこで、ユーザデータを基準としたデータを作成する
away_user_df = pd.merge(uriage_df, user_df, left_on='customer_name', right_on='顧客名', how='right')
away_user_df

# 購入していないユーザがいれば、nanのデータが発生しているはず
away_user_df.isnull().sum()

# nanがあるので、購入してないユーザが存在する。
away_user_df[away_user_df["purchase_date"].isnull()]
