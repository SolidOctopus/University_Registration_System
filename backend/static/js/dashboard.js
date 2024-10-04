document.addEventListener('DOMContentLoaded', function () {
    var calendarEl = document.getElementById('calendar');
    var calendar = new FullCalendar.Calendar(calendarEl, {
        initialView: 'listYear',
        headerToolbar: false,
        events: '/get-assignments/',
        height: 'auto',
        dayHeaders: true,
        showNonCurrentDates: false,
        eventOrder: false,
        eventOverlap: false,
        eventLimit: false,
        noEventsContent: '',  // Hide empty box
        eventContent: function(arg) {
            return {
                html: `
                    <div class="assignment-row">
                        <div class="assignment-info">
                            <input type="checkbox">
                            <span class="assignment-title">${arg.event.title}</span>
                        </div>
                        <div class="assignment-meta">
                            <span class="assignment-points">${arg.event.extendedProps.points || 0} pts</span>
                            <span class="assignment-status">${arg.event.extendedProps.status || 'No Status'}</span>
                        </div>
                    </div>
                `
            };
        },
    });

    // Display calendar only if there are events
    if (calendar.getEvents().length > 0) {
        calendarEl.style.display = 'block';
    }

    calendar.render();

    
    const viewToggleBtn = document.getElementById('view-toggle-btn'); // Ensure the ID is correct
    const weeklyView = document.getElementById('weekly-view');
    const dailyView = document.getElementById('daily-view');
    
    if (viewToggleBtn && weeklyView && dailyView) {
        viewToggleBtn.addEventListener('click', function () {
            if (weeklyView.style.display === 'none') {
                // Show weekly view, hide daily view
                weeklyView.style.display = 'block';
                dailyView.style.display = 'none';
                viewToggleBtn.textContent = 'Switch to Daily View';
            } else {
                // Show daily view, hide weekly view
                weeklyView.style.display = 'none';
                dailyView.style.display = 'block';
                viewToggleBtn.textContent = 'Switch to Weekly View';
            }
        });
    }

    // Sidebar hover functionality
    const hoverArea = document.getElementById('hover-area');
    const leftIcons = document.querySelector('.left-icons');

    hoverArea.addEventListener('mouseenter', function () {
        leftIcons.classList.add('show'); // Show icons when hovering over the area
    });

    leftIcons.addEventListener('mouseleave', function () {
        leftIcons.classList.remove('show'); // Hide icons when mouse leaves the sidebar
    });
});

function handleSidebar(iconId, sidebarId) {
    const icon = document.getElementById(iconId);
    const sidebar = document.getElementById(sidebarId);

    icon.addEventListener("click", function () {
        sidebar.style.width = "250px";
    });

    sidebar.addEventListener("mouseleave", function () {
        sidebar.style.width = "0";
    });
}

handleSidebar("courses-icon", "courses-sidebar");
handleSidebar("projects-icon", "projects-sidebar");
handleSidebar("grades-icon", "grades-sidebar");
handleSidebar("announcements-icon", "announcements-sidebar");
handleSidebar("messages-icon", "messages-sidebar");
handleSidebar("help-icon", "help-sidebar");
handleSidebar("resources-icon", "resources-sidebar");