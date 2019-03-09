// /static/custom.js

<script src="https://js.pusher.com/4.4/pusher.min.js"></script>


    $.datetimepicker.setDateFormatter({
        parseDate: function (date, format) {
            var d = moment(date, format);
            return d.isValid() ? d.toDate() : false;
        },
        formatDate: function (date, format) {
            return moment(date).format(format);
        },
    });

    $('.datetime').datetimepicker({
        format:'DD-MM-YYYY hh:mm A',
        formatTime:'hh:mm A',
        formatDate:'DD-MM-YYYY',
        useCurrent: false,
    });

    // /static/custom.js

    // Initialize Pusher
    const pusher = new Pusher('0e7b8797c6f6736a1aae', {
        cluster: 'eu',
        encrypted: true
    });

    Pusher.logToConsole = true;
    // Subscribe to table channel
    var channel = pusher.subscribe('table');
    channel.bind('new-record', (data) => {
        alert(data.message)
        //const check_in = moment(`${data.data.check_in}`, 'DD/MM/YYYY hh:mm a').format('YYYY-MM-DD hh:mm:ss a')
        //const depature = moment(`${data.data.depature}`, 'DD/MM/YYYY hh:mm a').format('YYYY-MM-DD hh:mm:ss a')
    /*
       $('#flights').append(`
            <tr id="${data.data.id} ">
                <th scope="row"> ${data.data.date} </th>
                <td> ${data.data.time} </td>
                <td> ${data.data.period} </td>
                <td> ${data.data.user_id} </td>
                <td> ${data.data.table_id} </td>
            </tr>
       `)*/
    });

    // /static/custom.js

    channel.bind('update-record', (data) => {
        //const check_in = moment(`${data.data.check_in}`, 'DD/MM/YYYY hh:mm a').format('YYYY-MM-DD hh:mm:ss a')
        //const depature = moment(`${data.data.depature}`, 'DD/MM/YYYY hh:mm a').format('YYYY-MM-DD hh:mm:ss a')

        $(`#${data.data.id}`).empty()

        $(`#${data.data.id}`).html(`
            <th scope="row"> ${data.data.date} </th>
                <td> ${data.data.time} </td>
                <td> ${data.data.period} </td>
                <td> ${data.data.user_id} </td>
                <td> ${data.data.table_id} </td>
        `)
     });