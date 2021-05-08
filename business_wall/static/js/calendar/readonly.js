var currentUser = null;

function eventRenderReadOnly(info) {
  const {event, view} = info;
  const {extendedProps} = event;

  info.el.setAttribute("id", "event_" + event.id);
  info.el.setAttribute("data-toggle", "popover");
  info.el.setAttribute("data-trigger", "click");
  info.el.setAttribute("tabindex", "-1");
  const shiftDuration = FullCalendar.formatRange(event.start, event.end, {
    month: "2-digit",
    day: "2-digit",
    hour: "2-digit",
    minute: "2-digit",
    hour12: false,
  });

  const tradeButton = `
      <span>
        <a href="/roster/shifts/${event.id}/trade" class="btn btn-sm btn-primary">
          Trade shift
        </a>
      </span>
  `;

  $(info.el).popover({
    title: `${event.title}'s shift`,
    html: true,
    sanitize: false,
    animation: true,
    placement: "top",
    content: (
      `<div class="popover-duration">
          <div>
          ${shiftDuration}
          ${currentUser == extendedProps.worker ? tradeButton : ""}
          </div>
        </div>
        <div class="popover-shift-leader">
          Shift leader: ${extendedProps.organizer}
        </div>
        <div class="popover-department">
          Department: ${extendedProps.location}
        </div>
      </div>`
    )
  });
}

class ReadOnlyCalendar extends FullCalendar.Calendar {
  constructor(elem, settings) {
    const default_settings = {
      plugins: [ 'dayGrid', 'timeGrid', 'list', "bootstrap"],
      themeSystem: 'bootstrap',
      defaultView: 'week',
      locale: 'en-gb',
      firstDay: 1,
      timeformat: "H:mm",
      header: {
        left: 'prev,next today',
        center: 'title',
        right: 'month,week'
      },
      views: {
        month: {
          type: 'dayGridMonth',
          buttonText: 'Month'
        },
        week: {
          type: 'listWeek',
          buttonText: 'Week'
        }
      },
      eventTimeFormat: {
        hour: '2-digit',
        minute: '2-digit',
        meridiem: false
      },
      eventRender: eventRenderReadOnly,
      eventSourceSuccess: function (content, xhr) {
        setAlert("#alerts", "Loaded new shifts", "success");
      },
      eventSourceFailure: function (errorObj) {
        setAlert("#alerts", "Failed to load new shifts", "warning");
      },
      noEventsMessage: "No shifts to display"
    };
    const settings_ex = Object.assign({}, default_settings, settings);
    super(elem, settings_ex);
  }
}
