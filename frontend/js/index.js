/*
 * @Author: JasonYU
 * @Date: 2020-10-01 10:16:39
 * @LastEditTime: 2020-10-04 10:05:01
 * @FilePath: \SE\flask_se\frontend\js\index.js
 */
$(document).ready(function () {
    $("#resultSection").hide();
    $("#searchPaper").click(function () {
        keyword = $("#keyword").val();
        searchPaper(keyword);
    });
    $("#keyword").on("input propertychange", function () {
        getSuggest();
    });
});


$(document).keyup(function (event) {
    if (event.keyCode == 13) {
        searchPaper($("#keyword").val());
    }
});

function searchPaper(key) {

    $("#result").empty();

    request = new XMLHttpRequest();
    request.open('GET', "http://localhost:8000/search/query/" + key, true);

    request.onreadystatechange = function() {
        if (this.readyState == 4 && this.status == 200){
            data = JSON.parse(this.responseText);
            res = data.docs;
            console.log(res);
            if (res.length) {
                for (i = 0; i < res.length; i++) {

                    resultItem =
                        `
                        <div class='col-md-12 mb-4'>
                            <div class='card mb-12 shadow-sm'>
                                <div class='card-body'>
                                    <h5>` + res[i].title + ` <small style='margin-left: 10px'>` + res[i].authors + `</small> <small style='margin-left: 10px'>` + res[i].year +  `</small></h5>
                                    <p class='card-text'>` + res[i].abstract + `</p>
                                </div>
                            </div>
                        </div>
                    `;

                    $("#result").append(resultItem);
                }

                $("section.jumbotron").animate({
                    margin: "0"
                });

                $("#resultSection").show();

                // 清空输入联想
                $("#suggestList").empty();
            }

        }
    }
    request.send();
}


function getSuggest() {
    // 首先清空 suggestList 中原来的内容以便内容填入
    $("#suggestList").empty();
    request = new XMLHttpRequest();
    request.open('GET', "http://localhost:8000/search/suggest/" + $("#keyword").val(), true);

    request.onreadystatechange = function() {
        $("#suggestList").empty();
        if (this.readyState == 4 && this.status == 200){
            result = JSON.parse(this.responseText);
            res = result.mySuggester;
            if (res.suggestions.length) {
                // 利用for插入每一个结果
                for (i = 0; i < res.suggestions.length; i++) {
                    // 将返回的结果包装成HTML
                    suggestItem =
                        "<a class='list-group-item list-group-item-action'>" + res.suggestions[i] + "</a>";
                    // 插入HTML到suggestList中
                    $("#suggestList").append(suggestItem);
                }
            }
        }
    }
    request.send();
}
