from app.models import TicketStatus


def is_status_transition_allowed(
        current_status: TicketStatus,
        new_status: TicketStatus,
) -> bool:
    allowed_transitions = {
        TicketStatus.OPEN: {TicketStatus.IN_PROGRESS},
        TicketStatus.IN_PROGRESS: {TicketStatus.DONE},
        TicketStatus.DONE: set(),
    }

    return new_status in allowed_transitions[current_status]