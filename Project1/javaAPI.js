// テキストボックスに入力したデータをDBに挿入
document.getElementById('push').addEventListener('click', async () => {
    const purposeIdx = document.getElementById('var1').value;
    const message = document.getElementById('var2').value;
    const mean = document.getElementById('var3').value;
    const meanAddPhrase = document.getElementById('var4').value;
    const meanAddMor = document.getElementById('var5').value;
    const meanAddAll = document.getElementById('var6').value;
    const runningTime = document.getElementById('var7').value;
    const yesValue = document.getElementById('var8').value;
    const noValue = document.getElementById('var9').value;

    const data = {
        purposeIdx,
        message,
        mean: parseFloat(mean),
        meanAddPhrase: parseFloat(meanAddPhrase),
        meanAddMor: parseFloat(meanAddMor),
        meanAddAll: parseFloat(meanAddAll),
        runningTime,
        yesValue,
        noValue
    };

    try {
        // fetchを使用してHTTPリクエストを送信
        const response = await fetch('http://57.180.41.44:5003/data', {
            method: 'POST',
            headers: {
                // JSON形式でデータをサーバーに送信
                'Content-Type': 'application/json'
            },
            // JavaScriptオブジェクトをJSON文字列に変換して送信
            body: JSON.stringify(data)
        });

        console.log(response.ok);

        if (response.ok) {
            alert('メッセージ保存完了');
            // データ保存後、個人DB照会関数を呼び出してテーブルを更新
            getDataById();
        } else {
            alert('메세지 저장 실패');
        }
    } catch (error) {
        console.error('Error:', error);
        alert('오류 발생');
    }
});




// メッセージ送信時間を更新する関数
// 更新対象のメッセージIDと表示するHTMLセル要素を引数として受け取る
async function updateSendDate(messageId, sendDateCell) {
    try {
        // 現在の日本時間を取得し、適切な形式に変換
        const formattedTime = showCurrentJapanTime();
        // 現在の時刻をSend Dateに表示
        sendDateCell.textContent = formattedTime; 


        // 実際のサーバーへの更新リクエスト
        const response = await fetch(`http://57.180.41.44:5003/data/${messageId}`, {
            method: 'PUT',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ sendDate: formattedTime })
        });

        if (response.ok) {
            const data = await response.json();
            sendDateCell.textContent = data.timeDisplay;
        } else {
            alert('전송 시간 업데이트 실패');
        }
    } catch (error) {
        console.error('Error updating send date:', error);
        alert('전송 시간 업데이트 중 오류 발생');
    }
}

// 個人DB照会関数
async function getDataById() {
    const response = await fetch('http://57.180.41.44:5003/private_data'); 
    const data = await response.json();
    // データをテーブル形式でウェブページに表示
    addPersonalDataToTable(data.firstmessages, 'dataTable1');
}

// チームDB照会関数
async function teamData() {
    const response = await fetch('http://57.180.41.44:5003/2team_data');
    const team_datas = await response.json();
    // データをテーブル形式でウェブページに表示
    addTeamOrAllDataToTable(team_datas, 'dataTable2');
}

// 全体DB照会関数
async function allData() {
    const response = await fetch('http://57.180.41.44:5003/all_data');
    const all_datas = await response.json();
    // データをテーブル形式でウェブページに表示
    addTeamOrAllDataToTable(all_datas, 'dataTable3');
}

// 個人データをテーブルに追加する関数
function addPersonalDataToTable(datas, getId) {
    // ブラウザは明示的に<tbody>を書かなくても自動的に追加
    const table = document.getElementById(getId).getElementsByTagName('tbody')[0];
    while (table.rows.length > 2) {
        table.deleteRow(2);
    }

    // 各項目はテーブルに新しい行として追加
    datas.forEach((item) => {
        const row = table.insertRow();
            const cell1 = row.insertCell(0);
            const cell2 = row.insertCell(1);
            const cell3 = row.insertCell(2);
            const cell4 = row.insertCell(3);
            const cell5 = row.insertCell(4);
            const cell6 = row.insertCell(5);
            const cell7 = row.insertCell(6);
            const cell8 = row.insertCell(7);
            const cell9 = row.insertCell(8);
            const cell10 = row.insertCell(9);
            const cell11 = row.insertCell(10);
            const cell12 = row.insertCell(11);
            const cell13 = row.insertCell(12);


            let purpose = item.purposeIdx;
            let message = item.message;

            if (message.startsWith('ㄴ')) {
                purpose += ' ㄴ';
                message = message.replace(/^ㄴ\s*/, '');
            }


            // 各セルにデータを割り当て
            cell1.textContent = item.messageId;
            cell2.textContent = item.purposeIdx;
            cell3.textContent = item.message;
            cell4.textContent = item.mean;
            cell5.textContent = item.meanAddPhrase;
            cell6.textContent = item.meanAddMor;
            cell7.textContent = item.meanAddAll;
            cell8.textContent = item.runningTime;
            cell9.textContent = item.sendDate || ""; 
            cell10.textContent = item.receiveDate || ""; 
            cell11.textContent = item.yesValue;
            cell12.textContent = item.noValue;
            cell13.textContent = item.confirmStatus === 1 ? "Answer Yes" : "Answer No";

            // 各行にメッセージ送信」ボタンを追加、クリックすると現在の日本時間が表示
            const sendButton = document.createElement('button');
            sendButton.id = 'sendMessageButton';
            sendButton.textContent = 'メッセージ送り';

            // イベントリスナーを追加
            sendButton.addEventListener('click', function() {
                const japanTime = showCurrentJapanTime();
                cell9.textContent = japanTime;

                // データベースでsendDateを更新
                updateSendDate(item.messageId, cell9)
                    .then(() => {
                        alert('転送時間が更新されました。');
                        teamData(); // 팀DB와 전체DB 갱신
                        allData();
                    })
                    .catch((error) => {
                        console.error('전송 시간 업데이트 중 오류:', error);
                        alert('전송 시간 업데이트 실패');
                    });
            });
            cell10.appendChild(sendButton);


        // 各回答メッセージを追加
        item.answers.forEach(answer => {
            const answerRow = table.insertRow();
            const answerCell1 = answerRow.insertCell(0);
            const answerCell2 = answerRow.insertCell(1);
            const answerCell3 = answerRow.insertCell(2);
            const answerCell4 = answerRow.insertCell(3);
            const answerCell5 = answerRow.insertCell(4);
            const answerCell6 = answerRow.insertCell(5);
            const answerCell7 = answerRow.insertCell(6);
            const answerCell8 = answerRow.insertCell(7);
            const answerCell9 = answerRow.insertCell(8);
            const answerCell10 = answerRow.insertCell(9);
            const answerCell11 = answerRow.insertCell(10);
            const answerCell12 = answerRow.insertCell(11);
            const answerCell13 = answerRow.insertCell(12);

             const multiplier = answer.yesOrNo === 1 ? parseFloat(item.yesValue) : parseFloat(item.noValue);

            // 計算されたmean値を適用して回答データを入力
            answerCell1.textContent = answer.answerId;
            answerCell2.textContent = answer.messageId;
            answerCell3.textContent = answer.answer;
            answerCell4.textContent = (parseFloat(item.mean) * multiplier).toFixed(2);
            answerCell5.textContent = (parseFloat(item.meanAddPhrase) * multiplier).toFixed(2);
            answerCell6.textContent = (parseFloat(item.meanAddMor) * multiplier).toFixed(2);
            answerCell7.textContent = (parseFloat(item.meanAddAll) * multiplier).toFixed(2);
            answerCell8.textContent = "";
            answerCell9.textContent = answer.sendDate || "";
            answerCell10.textContent = answer.receiveDate || "";
            answerCell11.textContent = "";
            answerCell12.textContent = "";
            answerCell13.textContent = answer.yesOrNo === 1 ? "Yes" : "No";

            // 行のスタイルを調整
            answerRow.style.fontStyle = 'italic';
            answerRow.style.backgroundColor = '#F0F0F0';
        });
    });
}


// チームDBと全体DBをテーブルに追加する関数
function addTeamOrAllDataToTable(datas, getId) {
    const table = document.getElementById(getId).getElementsByTagName('tbody')[0];

    while (table.rows.length > 2) {
        table.deleteRow(2);
    }

    datas.forEach((item) => {
        const row = table.insertRow();
        const cell1 = row.insertCell(0);
        const cell2 = row.insertCell(1);
        cell1.textContent = item.messageId;
        cell2.textContent = item.message;
    });
}




// 現在の日本時間を取得する関数
function showCurrentJapanTime() {
    const now = new Date();
    const options = {
        timeZone: 'Asia/Tokyo',
        year: 'numeric',
        month: '2-digit',
        day: '2-digit',
        hour: '2-digit',
        minute: '2-digit',
        second: '2-digit',
        hour12: false
    };
    // ja-JPという日本語形式(日本の国家設定)と設定されたoptionsを使用して日付と時間のフォーマッティング
    const formatter = new Intl.DateTimeFormat('ja-JP', options);
    return formatter.format(now).replace(/\//g, '-');
}
// フォーマッティングされた日付と時刻を返します
// 文字列内の/をすべて-に置き換える
// /\/gは正規表現式、最初/と最後/は正規表現式の始まりと終わりの意味、gは文字列内のすべての該当パターンを探索
// \はエスケープ文字で、後からくる文字を特殊文字ではなく一般文字で処理


// ページの読み込み時に関数を実行
window.onload = function () {
    getDataById();
    teamData();
    allData();
};

// ページを再読み込みするリロードボタン
document.getElementById('reload').addEventListener('click', function() {
    location.reload(true);
});
