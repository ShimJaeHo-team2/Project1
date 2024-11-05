// 自分の名前ボタンをクリックするとウェブページが切り替わる
document.getElementById('navigate').addEventListener('click', function() {
    // HTMLドキュメント内でidが「navigate」の要素をクリックすると、指定された関数が実行
    window.location.href = 'NoticeBoard3.html';
    // window.location.hrefプロパティは、ボタンをクリックした際に他のページに移動する際に使用
    // 現在のページから「NoticeBoard3.html」ページに移動
});

    