from app.models import User, Project, Ticket, TicketStatus
from app.security import create_access_token
from sqlalchemy import select

def test_open_ticket_can_move_to_in_progress(client, db_session, make_user, make_project, make_ticket):
    user = make_user("test@example.com")

    project = make_project("Test project", user.id)

    ticket = make_ticket("Test ticket",
                         "Test description",
                         2,
                         project.id,
                         TicketStatus.OPEN
                         )

    token = create_access_token(user.id)

    response = client.patch(
        f"/tickets/{ticket.id}/status",
        json={"status": "in_progress"},
        headers={"Authorization": f"Bearer {token}"}
    )

    assert response.status_code == 200
    assert response.json()["status"] == "in_progress"

    db_session.refresh(ticket)

    assert ticket.status == TicketStatus.IN_PROGRESS


def test_in_progress_cannot_move_to_open(client, db_session, make_user, make_project, make_ticket):
    user = make_user("test@gmail.com")

    project = make_project("hi", user.id)

    ticket = make_ticket("Test ticket",
                         "Test description",
                         2,
                         project.id,
                         TicketStatus.IN_PROGRESS
                         )

    token = create_access_token(user.id)

    response = client.patch(
        f"/tickets/{ticket.id}/status",
        json={"status": "open"},
        headers={"Authorization": f"Bearer {token}"}
    )

    assert response.status_code == 409
    assert response.json()["detail"] == "Not allowed"

    db_session.refresh(ticket)

    assert ticket.status == TicketStatus.IN_PROGRESS


def test_mark_done(client, make_user, make_project, make_ticket):
    user = make_user("test@gmail.com")

    project = make_project("Jelly", user.id)

    ticket = make_ticket("Test ticket",
                         "Test description",
                         2,
                         project.id,
                         TicketStatus.IN_PROGRESS
                         )

    token = create_access_token(user.id)
    response = client.patch(f"/tickets/{ticket.id}/status", json={"status": "done"},
                            headers={"Authorization": f"Bearer {token}"})

    assert response.status_code == 200
    assert response.json()["status"] == "done"


def test_other_user_cannot_update_ticket_status(client, make_user, make_project, make_ticket):
    user = make_user("fake@gmail.com")

    user_b = make_user("fakiee@gmail.com")

    project = make_project("Kot", user.id)

    ticket = make_ticket("Test ticket",
                         "Test description",
                         2,
                         project.id,
                         TicketStatus.OPEN
                         )

    token = create_access_token(user_b.id)
    response = client.patch(f"/tickets/{ticket.id}/status",
                            json={"status": "in_progress"},
                            headers={"Authorization": f"Bearer {token}"})

    assert response.status_code == 404


def test_validation_status(client, make_user, make_project, make_ticket):
    user = make_user("fakie@gmail.com")

    project = make_project("baby", user.id)

    ticket = make_ticket("Test ticket",
                         "Test description",
                         2,
                         project.id,
                         TicketStatus.OPEN
                         )

    token = create_access_token(user.id)

    response = client.patch(f"/tickets/{ticket.id}/status",
                            json={"status": "banana"},
                            headers={"Authorization": f"Bearer {token}"})

    assert response.status_code == 422


def test_not_authorized_user_makes_patch(client, make_user, make_project, make_ticket):
    user = make_user("hello@gmail.com")

    project = make_project("mimi", user.id)

    ticket = make_ticket("Test ticket",
                         "Test description",
                         2,
                         project.id,
                         TicketStatus.OPEN
                         )

    response = client.patch(f"/tickets/{ticket.id}/status",
                            json={"status": "in_progress"})

    assert response.status_code == 401


def test_invalid_ticket_id_patch(client, make_user):
    user = make_user("baby@gail.com")

    token = create_access_token(user.id)

    response = client.patch(f"/tickets/999999/status",
                            json={"status": "in_progress"},
                            headers={"Authorization": f"Bearer {token}"})

    assert response.status_code == 404
    assert response.json()["detail"] == "No ticket found."


def test_post_ticket(client, make_user, make_project):
    user = make_user("tired@gmail.com")

    project = make_project("just be", user.id)

    token = create_access_token(user.id)

    response = client.post(f"/tickets",
                           json={
                               "title": "Test ticket",
                               "description": "Created through API",
                               "priority": 2,
                               "project_id": project.id
                           },
                           headers={"Authorization": f"Bearer {token}"}
                           )

    assert response.status_code == 201
    assert response.json()["status"] == "open"


def test_ticket_post_ownership(client, make_user, make_project):
    user_a = make_user("sad@gmail.com")
    user_b = make_user("happy@gmail.com")

    project = make_project("Be fine", user_a.id)

    token = create_access_token(user_b.id)

    response = client.post(f"/tickets",
                           json={
                               "title": "Test ticket",
                               "description": "Created through API",
                               "priority": 2,
                               "project_id": project.id
                           },
                           headers={"Authorization": f"Bearer {token}"}
                           )

    assert response.status_code == 404


def test_pydantic_validation_post_ticket(client, make_user, make_project):
    user = make_user("papa@gmail.com")
    project = make_project("papas_work", user.id)

    token = create_access_token(user.id)

    response = client.post(f"/tickets",
                           json={"title": "Test ticket",
                                 "description": "Created through API",
                                 "priority": 99,
                                 "project_id": project.id
                                 },
                           headers={"Authorization": f"Bearer {token}"}
                           )

    assert response.status_code == 422


def test_partial_update_ticket(client, db_session, make_user, make_project, make_ticket):
    user = make_user("bebe@gmail.com")
    project = make_project("bebe's", user.id)
    ticket = make_ticket("Old title",
                         "Keep me",
                         4,
                         project.id,
                         TicketStatus.OPEN
                         )
    token = create_access_token(user.id)
    response = client.patch(f"/tickets/{ticket.id}",
                            json={"title": "New title"},
                            headers={"Authorization": f"Bearer {token}"}
                            )

    assert response.status_code == 200
    assert response.json()["title"] == "New title"
    assert response.json()["description"] == "Keep me"
    assert response.json()["priority"] == 4

    db_session.refresh(ticket)

    assert ticket.title == "New title"
    assert ticket.description == "Keep me"
    assert ticket.priority == 4


def test_delete_ticket(client, db_session, make_user, make_project, make_ticket):
    user = make_user("angry@mail.com")
    project = make_project("angries", user.id)
    ticket = make_ticket("Test ticket",
                         "Test description",
                         2,
                         project.id,
                         TicketStatus.OPEN
                         )

    token = create_access_token(user.id)

    response = client.delete(f"/tickets/{ticket.id}",
                             headers={"Authorization": f"Bearer {token}"}
                             )

    assert response.status_code == 204

    deleted_ticket = db_session.scalar(select(Ticket).where(Ticket.id == ticket.id))
    assert deleted_ticket is None

def test_get_one_ownership(client, make_user, make_project, make_ticket):
    user = make_user("angry@mail.com")
    user_b = make_user("user@gmail.com")
    project = make_project("angries", user.id)
    ticket = make_ticket("Test ticket",
                         "Test description",
                         2,
                         project.id,
                         TicketStatus.OPEN
                         )

    token = create_access_token(user_b.id)

    response = client.get(f"/tickets/{ticket.id}",
                             headers={"Authorization": f"Bearer {token}"}
                             )

    assert response.status_code == 404

def test_list_ownership(client, make_user, make_project, make_ticket):
    user = make_user("angry@mail.com")
    user_b = make_user("user@gmail.com")
    project = make_project("angries", user.id)
    project_2 = make_project("test", user_b.id)
    ticket = make_ticket("Test ticket",
                         "Test description",
                         2,
                         project.id,
                         TicketStatus.OPEN
                         )
    ticket_2 = make_ticket("Test ticket 2",
                         "Test description 2",
                         3,
                         project.id,
                         TicketStatus.OPEN
                         )
    ticket_3 = make_ticket("Test ticket 3",
                           "Test description 3",
                           3,
                           project_2.id,
                           TicketStatus.OPEN
                           )

    token = create_access_token(user.id)

    response = client.get(f"/tickets",
                          headers={"Authorization": f"Bearer {token}"}
                          )

    assert response.status_code==200
    assert len(response.json()) == 2

    ids = [item["id"] for item in response.json()]
    assert ticket.id in ids
    assert ticket_2.id in ids
    assert ticket_3.id not in ids

def test_filter_by_priority(client, make_user, make_project, make_ticket):
    user = make_user("angry@mail.com")

    project = make_project("angries", user.id)

    ticket = make_ticket("Test ticket",
                         "Test description",
                         1,
                         project.id,
                         TicketStatus.OPEN
                         )
    ticket_2 = make_ticket("Test ticket 2",
                           "Test description 2",
                           3,
                           project.id,
                           TicketStatus.OPEN
                           )
    ticket_3 = make_ticket("Test ticket 3",
                           "Test description 3",
                           3,
                           project.id,
                           TicketStatus.OPEN
                           )

    token = create_access_token(user.id)

    response = client.get(f"/tickets?priority=3",
                          headers={"Authorization": f"Bearer {token}"}
                          )

    priorities = [item["priority"] for item in response.json()]

    assert all(priority == 3 for priority in priorities)
    assert len(priorities) == 2


    assert ticket_2.priority == 3
    assert ticket_3.priority == 3
    assert ticket.priority not in priorities


def test_pagination(client, make_user, make_project, make_ticket):
    user = make_user("angry@mail.com")

    project = make_project("angries", user.id)

    ticket = make_ticket("Test ticket",
                         "Test description",
                         5,
                         project.id,
                         TicketStatus.OPEN
                         )
    ticket_2 = make_ticket("Test ticket 2",
                           "Test description 2",
                           4,
                           project.id,
                           TicketStatus.OPEN
                           )
    ticket_3 = make_ticket("Test ticket 3",
                           "Test description 3",
                           3,
                           project.id,
                           TicketStatus.OPEN
                           )
    ticket_4 = make_ticket("Test ticket 4",
                           "Test description 4",
                           2,
                           project.id,
                           TicketStatus.OPEN
                           )

    ticket_5 = make_ticket("Test ticket 5",
                           "Test description 5",
                           1,
                           project.id,
                           TicketStatus.OPEN
                           )


    token = create_access_token(user.id)

    response = client.get(f"/tickets?skip=2&limit=2",
                          headers={"Authorization": f"Bearer {token}"}
                          )

    assert response.status_code == 200
    assert len(response.json()) == 2

    priorities = [item["priority"] for item in response.json()]
    assert priorities == [3,2]
