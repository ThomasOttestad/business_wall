
function myFunction() {
    const filter = document.querySelector('#myInput').value.toUpperCase();
    const trs = document.querySelectorAll('#myTable tr:not(.header)');
    trs.forEach(tr => tr.style.display = [...tr.children].find(td => td.innerHTML.toUpperCase().includes(filter)) ? '' : 'none');
}


//Stops propagation on row, so last cell does not toggle collapsed row 
$('#doNotShowCollapsed').click(function (e) {
    e.stopPropagation();
});

// Changes background color of opened row so it´s easier to see which message is opened
$('#row{{ele.id}}').ready(function () {
    $('tr').click(function () {
        //Check to see if background color is set or if it's set to white.
        if(this.style.background == "" || this.style.background =="white") {
            $(this).css('background', 'lightgrey');
        }
        else {
            $(this).css('background', 'white');
        }
    });
});


// Removes a message, but still a bit wonky. Need to fix
// issue where only main row gets deleted(and not collapsed)
$('.email_delete').on('click', function(){
    let confirmation = confirm("Are you sure you want to delete the message?");
    if (confirmation) {
        let object_id = $(this).attr('data-usrid');
        let remove_row = $(this).closest("tr");
        let remove_next = remove_row.next("tr");
        $.ajax({
            url: "/inbox/delete_message/" + object_id,
            type: "POST",
            beforeSend: function(xhr) {
                xhr.setRequestHeader("X-CSRFToken", "{{ csrf_token }}");
            },
            success: function(response){
                if (response["success"]){
                    // Removing row and hidden row
                    remove_row.remove(); 
                    remove_next.remove();
                }
            },
            error: function (response) {
                console.log(response)
            }
        });
    }
});
