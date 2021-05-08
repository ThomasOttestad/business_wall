
var changedEvents= {};

function msToHHMMSS(s) {
  const ms = s % 1000;
  s = (s - ms) / 1000;
  const secs = s % 60;
  s = (s - secs) / 60;
  const mins = s % 60;
  const hrs = (s - mins) / 60;
  return `${("00"+hrs).slice(-2)}:${("00"+mins).slice(-2)}:${("00"+secs).slice(-2)}`;
}

function getValueFromText(selectId, text) {
  return $(selectId+" option").filter(function () { return $(this).html() == text; }).val();
}

function getEventData(event) {
  return {
    department: getValueFromText("#editModal #id_department", event.extendedProps.location),
    worker: getValueFromText("#editModal #id_worker", event.title),
    shift_leader: getValueFromText("#editModal #id_shift_leader", event.extendedProps.organizer),
    start: moment(event.start).format("YYYY-MM-DD HH:mm"),
    duration: msToHHMMSS(event.end-event.start)
  };
}

function eventChange(info) {
  const {event, revert, el} = info;
  $.post("/api/shifts/"+event.id, getEventData(event))
  .done((data) => setAlert("#notifications", "Edited shift", "success"))
  .fail((xhr, textStatus, errorThrown) => {
    revert()
    if (xhr.responseJSON) {
      const {error, validationErrors} = xhr.responseJSON
      if (validationErrors) {
        for (let field in validationErrors) {
          setAlert("#notifications", validationErrors[field].join("\n"), "danger");
        }
      } else {
        setAlert("#notifications", xhr.responseJSON.error, "danger");
      }
    } else {
      setAlert("#notifications", "Failed to edit shift!", "danger");
    }
  })
}


function eventRender(info) {
  const {event, el} = info;
  $(el).contextmenu(function () {
    const eventData = getEventData(event);
    $("#editModal #shift_id").val(event.id);
    $("#editModal #id_department").val(eventData.department);
    $("#editModal #id_worker").val(eventData.worker);
    $("#editModal #id_shift_leader").val(eventData.shift_leader);
    $("#editModal #id_start").val(eventData.start);
    $("#editModal #id_duration").val(eventData.duration);
    $("#editModal").modal("toggle");
    return false;
  });

  $(el).append(`<div class="fc-content text-muted">${event.extendedProps.location}</div>`);
}

class EditableCalendar extends FullCalendar.Calendar {
  constructor(elem, settings) {
    const default_settings = {
      plugins: ['dayGrid', 'timeGrid', "interaction", "bootstrap"],
      themeSystem: 'bootstrap',
      defaultView: 'week',
      locale: 'en-gb',
      firstDay: 1,
      editable: true,
      timeformat: "H:mm",
      header: {
        left: 'prev,next',
        center: 'title',
        right: 'month,week,day'
      },
      views: {
        month: {
          type: 'dayGridMonth',
          buttonText: 'Month'
        },
        week: {
          type: 'timeGridWeek',
          buttonText: 'Week'
        },
        day: {
          type: 'timeGridDay',
          buttonText: 'Day'
        }
      },
      eventTimeFormat: {
        hour: '2-digit',
        minute: '2-digit',
        meridiem: false
      },
      eventDrop: eventChange,
      eventResize: eventChange,
      eventRender: eventRender
    };
    const settings_ex = Object.assign({}, default_settings, settings);
    super(elem, settings_ex);
  }
}
