function draw_drt() {
    new submit_rules();
    new drt_triplets_from_api(function (data, err) {
        data = JSON.parse(data);
        var container = document.getElementById('graph');
        var options = {
            nodes : {
                shape: 'dot',
                size: 10
            }
        };
        var network = new vis.Network(container, data, options);
        document.getElementById('rules').disabled=false;
    });
}

function submit_rules() {
    document.getElementById('rules').disabled=true
    new submit_rules_to_api(function (data, err) {
            data = JSON.parse(data);
            console.log(data);
    });
}