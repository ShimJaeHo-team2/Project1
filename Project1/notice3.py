from fastapi import FastAPI, HTTPException
# fastapiライブラリを使ってウェブアプリケーションを構築。FastAPIクラスはウェブアプリケーションを作成し、HTTPExceptionはHTTP例外を処理するのに使用
from pydantic import BaseModel, Field
# pydanticライブラリからBaseModelとFieldクラスをインポート。pydanticはデータモデルを定義し、データのバリデーションに便利。Fieldはフィールドの条件を設定するために使用
from typing import List, Optional
# typingモジュールからListとOptionalタイプヒントをインポート。フィールドの型を明確に指定するために使用
from databases import Database
# databaseライブラリは非同期DBアクセスをサポートし、DatabaseクラスはDB接続を設定し、クエリ実行やトランザクション管理
from datetime import datetime
# datetimeクラスを使用して、日付と時間を扱う目的
import decimal
# decimalモジュールは正確な小数点計算が必要な場合に便利
import pytz  
# pytzライブラリをインポート。特定のタイムゾーンを考慮して日付と時間の変換や操作が可能
# 日本時間で設定するために利用
from fastapi.middleware.cors import CORSMiddleware


japan_timezone = pytz.timezone('Asia/Tokyo')
# pytzライブラリを活用して、日本のタイムゾーン(Asia/Tokyo)を表すタイムゾーンオブジェクトを作成
# 日付と時間の変換や操作が可能

app = FastAPI()


# CORS設定の追加
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # すべてのドメインを許可
    allow_credentials=True,
    allow_methods=["*"],  # すべてのHTTPメソッドを許可
    allow_headers=["*"],  # すべてのHTTPヘッダーを許可
)

DATABASE1_URL = "mysql://admin:Seigakushakorea0308(!@localhost/boardDB1_sjh3"
DATABASE2_URL = "mysql://admin:Seigakushakorea0308(!@localhost/boardDB2_sjh3"
DATABASE3_URL = "mysql://admin:Seigakushakorea0308(!@localhost/boardDB3_sjh3"
# MySQLサーバーに接続するためのデータベースURLを定義

database1 = Database(DATABASE1_URL)
database2 = Database(DATABASE2_URL)
database3 = Database(DATABASE3_URL)
# DATABASE_URLを使用して各データベースに別々に接続を設定


class CreateData(BaseModel):
    # messageIdカラムは自動生成される主キーとして追加しない
    purposeIdx: str
    message: str
    mean: decimal.Decimal
    meanAddPhrase: decimal.Decimal
    meanAddMor: decimal.Decimal
    meanAddAll: decimal.Decimal
    runningTime: str
    createdDate: datetime = Field(default_factory=lambda: datetime.now(japan_timezone))
    # フィールドのデフォルト値を設定して現地時間に戻すラムダ関数活用
    # ラムダ関数はPythonで使用する匿名関数の一形態で簡潔に関数を定義できるツール
    # 一時的に使用される簡単な関数や、他の関数内で即座に定義して使用する場合に有用
    yesValue: str
    noValue: str
    confirmStatus: bool = False
    # 初期値をFalseに設定


class UpdateData(BaseModel):
    sendDate: Optional[datetime]
# datetimeオブジェクトとして指定され、値が入力されなければNoneと見なされる
# 更新時にsendDateカラムのみ変更されると判断して1つのカラムのみを記入

class CreateAnswer(BaseModel):
# アンサーメッセージのバリデーションのためにDBで設定したフィールドとタイプを指定
    messageId: str
    answer: str
    mean: decimal.Decimal
    meanAddPhrase: decimal.Decimal
    meanAddMor: decimal.Decimal
    meanAddAll: decimal.Decimal
    yesOrNo: bool = False
    # answermessagesにはconfirmStatusカラムの代わりにyesOrNoカラムを使用


@app.on_event("startup")
async def startup():
    await database1.connect()
    await database2.connect()
    await database3.connect()
# startupハンドラは重複して定義できないため、1回のみ定義
# 各データベース接続を設定


@app.on_event("shutdown")
async def shutdown():
    await database1.disconnect()
    await database2.disconnect()
    await database3.disconnect()
# shutdownハンドラは重複して定義できないため、1回のみ定義
# 各データベース接続を解除


@app.get("/private_data")
# 個人DBを照会するAPI
async def get_private_data():
    
    try:
        query1 = """
                SELECT
                    messageId, purposeIdx, message, mean, meanAddPhrase, meanAddMor, meanAddAll, runningTime, createdDate, yesValue, noValue, confirmStatus FROM firstmessages
                """

        query2 = """
                SELECT
                    answerId, messageId, answer, mean, meanAddPhrase, meanAddMor, meanAddAll, yesOrNo, sendDate, receiveDate FROM answermessages   
                """

        # 個人DB照会時にfirstmessageとanswermessageカラムに関する値をすべて取得するため、2つのクエリを生成
        first_data = await database1.fetch_all(query1)
        answer_data = await database1.fetch_all(query2)
        # query1とquery2に関するすべての値をそれぞれfirst_dataとanswer_dataに保存

        if first_data is None:
                raise HTTPException(status_code=404, detail="fisrtmessage not found")
        

        # デフォルトのデータ構造化。 基本データをディクショナリー形式で1か所に保存
        # 基本メッセージに関連するデータを効率的に保存および検索することを目的
        messages = {}
        for record in first_data:
        # 基本メッセージ関連のDBから取得したメッセージを繰り返し処理
            message_id = record['messageId']
            # キー値であるmessageIdの値を取得して基本のmessage_id変数に保存
            messages[message_id] = {
            # テーブルのカラムをmessageの属性として辞書化して、後で簡単に検索や呼び出しができるように設定
                "messageId": record['messageId'],
                "purposeIdx": record['purposeIdx'],
                "message": record['message'],
                "mean": record['mean'],
                "meanAddPhrase": record['meanAddPhrase'],
                "meanAddMor": record['meanAddMor'],
                "meanAddAll": record['meanAddAll'],
                "runningTime": record['runningTime'],
                "createdDate": record['createdDate'],
                "yesValue": record['yesValue'],
                "noValue": record['noValue'],
                "confirmStatus": record['confirmStatus'],
                "answers": []
            }

        # アンサーデータをメッセージにリンク
        # answer_dataリストからアンサーデータを取得し、各メッセージに対応するアンサーをリンク
        for answer in answer_data:
        # アンサーメッセージ関連のDBから取得したメッセージを繰り返し処理
            message_id = answer['messageId']
            # キー値であるmessageIdの値を取得してアンサーmessage_id変数に保存
            if message_id in messages:
                messages[message_id]["answers"].append({
                # データベースから取得したアンサーデータをmessages辞書の各メッセージにリンク
                    "answerId": answer['answerId'],
                    "answer": f"ㄴ {answer['answer']}",
                    # すべてのアンサーメッセージの前に"ㄴ"を追加して、基本メッセージと区別できるように設計
                    "mean": answer['mean'],
                    "meanAddPhrase": answer['meanAddPhrase'],
                    "meanAddMor": answer['meanAddMor'],
                    "meanAddAll": answer['meanAddAll'],
                    "yesOrNo": answer['yesOrNo'],
                    "sendDate": answer['sendDate'],
                    "receiveDate": answer['receiveDate']
                })

        return {"firstmessages": list(messages.values())}
    # messages.values()は、それぞれのメッセージに対する情報と回答リストを含むディクショナリーを返すメソッド
    # これをリスト化して「firstmessages」キーに指定
    # ユーザーがすべてのメッセージに関する回答を「firstmessages」キーでアクセスできるように設計
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail={
                "error": "内部サーバーエラー",
                "message": str(e)
            }
        )


@app.get("/answer_data")
# /answer_dataのパスでGETリクエストを処理するAPIエンドポイントを定義
# answermessagesテーブルのデータを取得してユーザーに返す役割
async def get_answer_data():
    try:
        query = """
        SELECT 
            answerId, messageId, answer, mean, meanAddPhrase, meanAddMor, meanAddAll, yesOrNo
        FROM answermessages
        ORDER BY answerId
        """
        answer_data = await database1.fetch_all(query)
        
        if not answer_data:
            raise HTTPException(status_code=404, detail="アンサーが見つかりません。")
        
        return {"answermessages": [dict(answer) for answer in answer_data]}
        # クエリー結果をJSON形式に変換してユーザーに配信
        # answer_dataの各項目をディクショナリーに変換し、これをリスト形式で表示
    
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail={
                "error": "内部サーバーエラー",
                "message": str(e)
            }
        )



@app.get("/2team_data")
# チームDBを照会するAPI
async def get_2team_data():
    try:    
        query = "SELECT messageId, message, sendDate FROM firstmessages"
        # チームDBとしてメッセージIDとメッセージ内容のみを取得するためのクエリ
        result = await database2.fetch_all(query)
        # queryに対する値をすべて取得してresult変数に保存
        if result is None:
            raise HTTPException(status_code=404, detail="メッセージが見つかりません。")
        return result
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail={
                "error": "内部サーバーエラー",
                "message": "予期しないエラーが発生しました。後でもう一度お試しください。"
            }
            )
    # resultにデータがない場合、404エラーコードの表示設定
    # サーバー上でエラーが発生した場合、500エラーコード設定


@app.get("/all_data")
# 全体DBを照会するAPI
async def get_all_data():
    try:    
        query = "SELECT messageId, message, sendDate FROM firstmessages"
        # 全体DBとしてメッセージIDとメッセージ内容のみを取得するためのクエリ
        result = await database3.fetch_all(query)
        if result is None:
            raise HTTPException(status_code=404, detail="メッセージが見つかりません。")
        return result
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail={
                "error": "内部サーバーエラー",
                "message": "予期しないエラーが発生しました。後でもう一度お試しください。"
            }
            )


@app.post("/data")

# 個人、チーム、全体DBを保存するAPI。登録ボタンを押すとfirstmessageに入力内容を保存(insert)
async def create_data(data: CreateData):
# 데이터를 생성하는 작업을 할때 CreateData basemodel에서 messageId는 파라미터로 가져오지 않기 때문에 "messageId: str"내용 삭제(에러1)
    async with database1.transaction():
    # database1とトランザクションを開始し、ブロック内の作業がすべて完了すると終了し、途中でエラーが発生すると初期状態にロールバックされてDB状態を維持
    # トランザクションは、データベースの信頼性と完全性を保証するメカニズム
        search = "SELECT messageId FROM firstmessages ORDER BY CAST(SUBSTRING_INDEX(messageId, '-', -1) AS UNSIGNED) DESC LIMIT 1;"
        # messageIdを-で分割して最後の数字部分を整数に変換。降順でソートして最も最近のメッセージIDを1つだけ取得するように設定 
        result = await database1.fetch_one(query=search)
        # 直近のmessageIdを読み込むクエリ文

        if not result:
            new_messageId = "2-3-1"
        else:
            last_messageId = result['messageId']
            # resultに値がある場合、最新のmessageIdをlast_messageId変数に保存
            last_number = int(last_messageId.split('-')[-1])
            # last_messageId.split('-')[-1]でmessageIdの最後の部分(数字部分)を取得し、整数型に変換してlast_numberに保存
            new_messageId = f"2-3-{last_number + 1}"
            # new_messageIdを"2-3-{last_number + 1}"形式で生成(自動追加)

        query = """
        INSERT INTO firstmessages (
        messageId, purposeIdx, message, mean, meanAddPhrase, meanAddMor, meanAddAll, runningTime, createdDate, yesValue, noValue, confirmStatus)
        VALUES (:messageId, :purposeIdx, :message, :mean, :meanAddPhrase, :meanAddMor, :meanAddAll, :runningTime, :createdDate, :yesValue, :noValue, :confirmStatus)    
        """
        # データベースに新しいデータを挿入
        values = data.dict()

        values = {
            "messageId": new_messageId,
            # new_messageId変数に保存された値を使用
            "purposeIdx": data.purposeIdx,
            # dataオブジェクトのpurposeIdxフィールドをそのまま保存
            "message": data.message,
            # dataオブジェクトのmessageフィールドをそのまま保存
            "mean": float(data.mean),
            # dataオブジェクトのmeanフィールドを小数形式に変換して保存
            "meanAddPhrase": float(data.meanAddPhrase),
            # dataオブジェクトのmeanAddPhraseフィールドを小数形式に変換して保存
            "meanAddMor": float(data.meanAddMor),
            # dataオブジェクトのmeanAddMorフィールドを小数形式に変換して保存
            "meanAddAll": float(data.meanAddAll),
            # dataオブジェクトのmeanAddAllフィールドを小数形式に変換して保存
            "runningTime": data.runningTime,
            # dataオブジェクトのrunningtimeフィールドをそのまま保存
            "createdDate": data.createdDate,
            # dataオブジェクトのcreatedDateフィールドをそのまま保存
            "yesValue": float(data.yesValue),
            # dataオブジェクトのyesValueフィールドを小数形式に変換して保存
            "noValue": float(data.noValue),
            # dataオブジェクトのnoValueフィールドを小数形式に変換して保存
            "confirmStatus": data.confirmStatus
            # dataオブジェクトのconfirmStatusフィールドをそのまま保存
        }
        # データ値の設定。Pydanticモデルのデータをvalues辞書の形に変換し、各フィールドを適切な型に設定
        # Pydanticはデータのバリデーションと設定管理を行うPythonライブラリ

        await database1.execute(query, values=values)
        await database2.execute(query, values=values)
        await database3.execute(query, values=values)
        # クエリ内のVALUES値が下のvalues辞書から取得した各入力値で置き換えられ、DBに挿入（バインディング・マッピングしたデータをDBに挿入）
        return {"message": "Data created successfully"}


@app.put("/data/{messageId}")
# sendDate生成API呼び出し。PUTリクエストがこのパスに送られるとtimeDisplay関数が呼び出し
# 初期値のnullに新しい情報を上書きする方式のためput（update）を使用
async def timeDisplay(messageId: str):
        query = "SELECT * FROM firstmessages WHERE messageId = :messageId"
        existing_data = await database1.fetch_one(query, values={"messageId": messageId})
        # database1でクエリを実行し、結果をexisting_dataに保存
        if not existing_data:
            raise HTTPException(status_code=400, detail="Bad request")
        # クエリの結果が存在しない場合（データが存在しない場合）にエラーコード400で処理
        
        now = datetime.now(japan_timezone)
        # 現在の日付と時間を日本時間（JST）でYYYY-MM-DD HH:MM:SS形式の文字列にフォーマット
        update_query = """
        UPDATE firstmessages
        SET sendDate = :sendDate
        WHERE messageId = :messageId
        """
        await database1.execute(update_query, values={"sendDate": now, "messageId": messageId})
        await database2.execute(update_query, values={"sendDate": now, "messageId": messageId})
        await database3.execute(update_query, values={"sendDate": now, "messageId": messageId})
        # 個人DB、チームDB、全体DBのsendDateデータが同一に挿入されるよう設定（連動）
        # sendDateを更新するupdate_queryを実行し、valuesはsendDateとmessageIdの実際の値で置き換え（バインディング）
        return {"timeDisplay": now.strftime('%Y-%m-%d %H:%M:%S')}
        # now変数に保存された現在の日本時間を提供
        # {"timeDisplay": "2024-07-23 12:34:56"}の形で値が返し
        