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

# # 3章 顧客の全体像を把握する１０本ノック
#
# ここでは、スポーツジムの会員データを使って顧客の行動を分析していきます。  
# これまでと同様にまずはデータを理解し、加工した後、顧客の行動データを分析していきましょう。  
# ここでは、機械学習に向けての初期分析を行います。

# ### ノック21：データを読み込んで把握しよう
# - use_log.csv : 会員のジム利用履歴
# - customer_master.csv : 集計時点での会員データ
# - class_master.csv : 会員のステータスデータ(オールタイム、デイタイムなど)
# - campaign_master.csv : ユーザに付与されているキャンペーンデータ

# +
import pandas as pd

use_log_df = pd.read_csv("use_log.csv")
use_log_df
# -

customer_master_df = pd.read_csv("customer_master.csv")
customer_master_df

class_master_df = pd.read_csv("class_master.csv")
class_master_df

campaign_master_df = pd.read_csv("campaign_master.csv")
campaign_master_df

# ### 僕が思った方針メモ
# まずは退会しているユーザが全体でどの程度かを見てみる。
#
# 次に退会したユーザに絞って、行動特性を見てみる。
# ex. 月ごとの利用回数の推移、会員ステータス、キャンペーンの有無
#
# そこから、退会しそうなユーザの特徴をなんとなく掴み、退会しそうなユーザ層を予測する。

# ### ノック22：顧客データを整形しよう

# customerにキャンペーンとステータスをmergeする
customer_master_df = pd.merge(customer_master_df, class_master_df, on='class', how='left')
customer_master_df = pd.merge(customer_master_df, campaign_master_df, on='campaign_id', how='left')
customer_master_df

# join後は、上手く結合できてないと欠損値が発生しているので、nanを見ておく
customer_master_df.isnull().sum() # 追加したデータに欠損がなければ一旦OK

# ### ノック23：顧客データの基礎集計をしよう

# まずは退会情報、会員ステータスの分布、キャンペーンの分布を見てみる
customer_master_df.groupby('is_deleted').count()['customer_id']

# 会員ステータス
customer_master_df.groupby('class_name').count()['customer_id']

# キャンペーン
customer_master_df.groupby('campaign_name').count()['customer_id']

# 性別
customer_master_df.groupby('gender').count()['customer_id']

# ### ノック24：最新顧客データの基礎集計をしよう
# 最新状態の顧客データを把握する。
# まずは現在時点の在籍しているユーザを取得する。
# また、退会のis_deletedが書き込まれるのにディレイが発生するので、end_dateで把握する。

customer_master_df['end_date'].isna()

customer_master_df['end_date'] = pd.to_datetime(customer_master_df['end_date'])
latest_customer_master_df = customer_master_df.loc[(customer_master_df['end_date'] >= pd.to_datetime('20190331')) | (customer_master_df['end_date'].isna())]
latest_customer_master_df

# 最新時点で退会していないユーザは、退会日が存在していないか、最終月に退会申請があったユーザとなる
latest_customer_master_df['end_date'].unique()

# 在籍しているユーザの各種属性を見てみる
latest_customer_master_df.groupby('class').count()['customer_id']

latest_customer_master_df.groupby('gender').count()['customer_id']

latest_customer_master_df.groupby('campaign_name').count()['customer_id']

# ### ノック25：利用履歴データを集計しよう
# 在籍ユーザと全体で基本データから有意な差分が発見できなかったので、利用データを見てみる。

use_log_df

use_log_df['usedate'] = pd.to_datetime(use_log_df['usedate'])
use_log_df['use_month'] = use_log_df['usedate'].dt.strftime('%Y%m')
use_month_df = use_log_df.groupby(['use_month', 'customer_id'], as_index=False).count() # 月ごとの利用履歴をユーザごとにまとめる
use_month_df.rename(columns={"log_id":"count"}, inplace=True) #カラム名を変更する。inplace無いと更新されない
del use_month_df["usedate"]
use_month_df

# +
# 集計した月ごとデータを元に統計情報を見てみる
use_month_customer = use_month_df.groupby('customer_id').agg(["mean", "median", "max", "min"])['count']
use_month_customer = use_month_customer.reset_index(drop=False)
use_month_customer

# ユーザごとの利用回数統計
# -

# ### ノック26：利用履歴データから定期利用フラグを作成しよう





# ### ノック27：顧客データと利用履歴データを結合しよう





# ### ノック28：会員期間を計算しよう



# ### ノック29：顧客行動の各種統計量を把握しよう







# ### ノック30：退会ユーザーと継続ユーザーの違いを把握しよう






