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

# # １章 ウェブの注文数を分析する１０本ノック
#
# ここでは、ある企業のECサイトでの商品の注文数の推移を分析していきます。  
# データの属性を理解し、分析をするためにデータを加工した後、  
# データの可視化を行うことで問題を発見していくプロセスを学びます。

# ### ノック１：データを読み込んでみよう

import pandas as pd
customer_master = pd.read_csv('customer_master.csv')

customer_master.head()

# !ls

item_master = pd.read_csv('item_master.csv')
item_master

transaction_1 = pd.read_csv('transaction_1.csv')
transaction_1

transaction_detail_1 = pd.read_csv('transaction_detail_1.csv')
transaction_detail_1

# ### ノック２：データを結合(ユニオン)してみよう

# データ分析する時はなるべく粒度が低いデータに合わせて、加工データを作成することから始める。
# 今回、一番粒度が低いのは、transaction関連データなので、これに合わせる。

transaction_2 = pd.read_csv('transaction_2.csv')
transaction = pd.concat([transaction_1, transaction_2], ignore_index=True)
transaction

transaction_detail_2 = pd.read_csv('transaction_detail_2.csv')
transaction_detail = pd.concat([transaction_detail_1, transaction_detail_2], ignore_index=True)
transaction_detail

## transactrion_detailがどういうデータかを見てみる
transaction_detail[transaction_detail['transaction_id'].duplicated()] # 購入されたアイテムの評価かな

# ### ノック３：売上データ同士を結合(ジョイン)してみよう

# 商品のレビューごとのレビュー情報に、商品ごとの販売情報を付与してみる。
# また、販売情報のpriseは複数商品の価格を合計したものになっているので、正しく加工しないうちにくっつけないことを注意する

## SQLでのjoinと大体一緒
transaction_detail_with_paydata = pd.merge(transaction_detail, transaction[["transaction_id", "payment_date", "customer_id"]], on="transaction_id")
transaction_detail_with_paydata

# ### ノック４：マスタデータを結合(ジョイン)してみよう
#
# 先程作成したデータに対して、顧客の詳細情報を付与する
#
# 顧客詳細 : customer_master

transaction_detail_with_paydata_with_customer_info = pd.merge(transaction_detail_with_paydata, customer_master, on="customer_id")
transaction_detail_with_paydata_with_customer_info

transaction_detail_with_paydata_with_customer_info_with_item_info = pd.merge(transaction_detail_with_paydata_with_customer_info, item_master, on="item_id")
transaction_detail_with_paydata_with_customer_info_with_item_info

## 加工しやすいように一時保存しておく
transaction_master = transaction_detail_with_paydata_with_customer_info_with_item_info.copy()

# ### ノック5：必要なデータ列を作ろう
# 作成したデータに、transactionごとの売上金額が書かれていないので、データを加工して作成する。
# quantityとpriseがあるので、そこから作成する。

transaction_master["sell_price"] = transaction_master["item_price"] * transaction_master["quantity"]
transaction_master[["quantity", "item_price", "sell_price"]]

# ### ノック6：データ検算をしよう
# データ加工は間違えやすいので、なるべく加工が間違っていないことを確かめる必要がある。
#
# MLOps的に言うと、データのチェックみたいな。今回は、売上の元データがあるので、それと比較する。

print(transaction["price"].sum())
print(transaction_master["sell_price"].sum())

transaction["price"].sum() == transaction_master["sell_price"].sum()

# ### ノック7：各種統計量を把握しよう

transaction_master.isnull().sum()

transaction_master.describe()

# ### ノック8：月別でデータを集計してみよう
# データがどのように変化しているのかを見ていく。

transaction_master["payment_date"] = pd.to_datetime(transaction_master["payment_date"])
# dtを使えば、時間データを変換できる
transaction_master["payment_month"] = transaction_master["payment_date"].dt.strftime("%Y%m")
transaction_master

# +
# groupbyを使って、月ごとに集計して和を計算する
# -
transaction_master.groupby("payment_month").sum()


# ### ノック9：月別、商品別でデータを集計してみよう

# 複数をまとめたい場合は、list型で指定する
transaction_master.groupby(["payment_month", "item_name"]).sum()

# 上記だとわかりずらいので、pivot_tableメソッドを使用して可視化してみる
pd.pivot_table(transaction_master, index="item_name", columns="payment_month", values=['sell_price', 'quantity'], aggfunc="sum")

# これで月別にデータを表示することができた。しかし、このままではひと目でデータを理解することができない。分析のゴールは、現場で適切に運用されることなので、わかりやすくすることが重要。

# ### ノック10：商品別の売上推移を可視化してみよう

## 可視化用のデータを作成する
graph_data = pd.pivot_table(transaction_master, index='payment_month', columns='item_name', values='sell_price', aggfunc='sum')
graph_data.index

# +
# matplotlibを使用して月ごとにデータを描画する
import matplotlib.pyplot as plt
# %matplotlib inline # jupyter notebook上で表示するためのコマンド

# plt.plot(横軸, 縦軸)
plt.plot(list(graph_data.index), graph_data['PC-A'], label='PC-A')
plt.plot(list(graph_data.index), graph_data['PC-B'], label='PC-B')
plt.plot(list(graph_data.index), graph_data['PC-C'], label='PC-C')
plt.plot(list(graph_data.index), graph_data['PC-D'], label='PC-D')
plt.plot(list(graph_data.index), graph_data['PC-E'], label='PC-E')
plt.legend()
# -


