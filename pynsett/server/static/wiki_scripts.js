
function drt_triplets_from_api(cb){
    var request = new XMLHttpRequest();
    request.open('POST', 'api/wikidata', true);
    request.setRequestHeader("Content-type", "application/json");
    request.onload = function () {
        data = this.response;
        console.log(data)
        err = '';
        cb(data, err);
    }
    request.send(JSON.stringify({'text': document.getElementById('query').value}));
}