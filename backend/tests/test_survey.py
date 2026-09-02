from app.models.project import Project
from app.models.survey import Survey, SurveyCreate, create_survey


def test_create_survey_updates_existing_record_for_project(db_session):
    project = Project(name="Survey project")
    db_session.add(project)
    db_session.commit()
    db_session.refresh(project)

    first = create_survey(
        project.id,
        SurveyCreate(survey_json={"1": 5}, comment="First comment"),
        db_session,
    )
    second = create_survey(
        project.id,
        SurveyCreate(survey_json={"1": 10}, comment="Updated comment"),
        db_session,
    )

    surveys = db_session.query(Survey).filter(Survey.project_id == project.id).all()

    assert second.id == first.id
    assert len(surveys) == 1
    assert surveys[0].survey_json == {"1": 10}
    assert surveys[0].comment == "Updated comment"