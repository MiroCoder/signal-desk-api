from app.models import User, Project, Ticket, TicketStatus
from app.security import create_access_token


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

def test_in_progress_cannot_move_to_open(client, db_session,make_user, make_project, make_ticket):
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

def test_ownership(client, make_user, make_project, make_ticket):
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
                    json ={"status": "in_progress"},
                    headers = {"Authorization": f"Bearer {token}"})

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
                            headers = {"Authorization": f"Bearer {token}"})

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
                        json= {"status": "in_progress"})

    assert response.status_code == 401

def test_invalid_ticket_id_patch(client, make_user):
    user = make_user("baby@gail.com")

    token = create_access_token(user.id)

    response = client.patch(f"/tickets/999999/status",
                            json = {"status": "in_progress"},
                            headers={"Authorization": f"Bearer {token}"})

    assert response.status_code == 404
    assert response.json()["detail"] == "No ticket found."

def test_post_ticket(client, make_user, make_project):
    user = make_user("tired@gmail.com")

    project = make_project("just be", user.id)

    token = create_access_token(user.id)

    response = client.post(f"/tickets",
                           json= {
                               "title": "Test ticket",
                               "description": "Created through API",
                               "priority": 2,
                               "project_id": project.id
                           },
                           headers={"Authorization":  f"Bearer {token}"}
                           )

    assert response.status_code == 201
    assert response.json()["status"] == "open"

def test_ticket_post_ownership(client, make_user, make_project):
    user_a = make_user("sad@gmail.com")
    user_b = make_user("happy@gmail.com")

    project= make_project("Be fine", user_a.id)

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
    project= make_project("papas_work", user.id)

    token = create_access_token(user.id)

    response = client.post(f"/tickets",
                           json= {"title": "Test ticket",
                               "description": "Created through API",
                               "priority": 99,
                               "project_id": project.id
                           },
                           headers = {"Authorization": f"Bearer {token}"}
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
                            json = {"title": "New title"},
                            headers = {"Authorization": f"Bearer {token}"}
                            )

    assert response.status_code ==200
    assert response.json()["title"] == "New title"
    assert response.json()["description"] == "Keep me"
    assert response.json()["priority"] == 4

    db_session.refresh(ticket)

    assert ticket.title == "New title"
    assert ticket.description == "Keep me"
    assert ticket.priority == 4