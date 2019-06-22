
function drt_triplets_from_api(cb){
    var request = new XMLHttpRequest();
    request.open('POST', 'http://localhost:4001/api/drt', true);
    request.setRequestHeader("Content-type", "application/json");
    request.onload = function () {
        data = this.response;
        err = '';
        cb(data, err);
    }
    request.send(JSON.stringify({'text': 'Isaac Asimov was an American writer and professor of biochemistry at Boston University. He was known for his works of science fiction and popular science. Asimov was a prolific writer who wrote or edited more than 500 books and an estimated 90,000 letters and postcards. His books have been published in 9 of the 10 major categories of the Dewey Decimal Classification.'}));

}